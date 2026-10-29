import inspect, json, os, random, shutil, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import lineage as L, isolated_launch as IL, immune as IM


def get(path):
    with open(path, "rb") as f:
        return f.read()


def put(path, text, mode="w"):
    with open(path, mode) as f:
        f.write(text)

SRC = {"core.py": "X = 1\n", "wire.py": "def enc(x): return x\n", "notary.py": "print('notary')\n",
       "lscs_harness.py": "H = 2\n", "supervisor.py": "S = 3\n", "session.py": "T = 4\n"}


class H1Lineage(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.root = os.path.join(self.d, "rel"); os.makedirs(self.root)
        for n, c in SRC.items():
            put(os.path.join(self.root, n), c)
        self.founder, self.germ = Ed25519PrivateKey.generate(), Ed25519PrivateKey.generate()
        self.F = L.pub_hex(self.founder)
        files = L.hash_tree(self.root, SRC)
        self.chain = L.genesis(self.founder, "1.1.5", files, [L.pub_hex(self.germ)])
        self.chain = L.descend(self.chain, self.germ, "1.1.6", files, [L.pub_hex(self.germ)])

    def tearDown(self): shutil.rmtree(self.d, ignore_errors=True)

    def test_valid_lineage_passes(self):
        self.assertEqual(L.gate(self.root, list(SRC), self.chain, self.F)["generation"], 1)

    def test_one_byte_change_refused(self):
        p = os.path.join(self.root, "notary.py"); b = bytearray(get(p)); b[0] ^= 0x20
        put(p, bytes(b), "wb")
        with self.assertRaisesRegex(L.LineageError, "notary.py"):
            L.gate(self.root, list(SRC), self.chain, self.F)

    def test_unmarked_executed_file_refused(self):
        put(os.path.join(self.root, "usercustomize.py"), "pass\n")
        with self.assertRaisesRegex(L.LineageError, "unmarked strand"):
            L.gate(self.root, list(SRC) + ["usercustomize.py"], self.chain, self.F)

    def test_edit_files_map_without_resigning_refused(self):
        # the old H1/L1 move: change the source AND the reference that describes it
        p = os.path.join(self.root, "notary.py"); put(p, "BACKDOOR = 1\n", "a")
        forged = json.loads(json.dumps(self.chain)); forged[-1]["files"]["notary.py"] = L.sha256_file(p)
        with self.assertRaisesRegex(L.LineageError, "bad mark"):
            L.gate(self.root, list(SRC), forged, self.F)

    def test_self_signed_child_refused(self):
        # the checked side mints its own key and signs a new generation: no ancestor authorized it
        rogue = Ed25519PrivateKey.generate()
        put(os.path.join(self.root, "notary.py"), "BACKDOOR = 1\n", "a")
        forged = L.descend(self.chain, rogue, "evil", L.hash_tree(self.root, SRC), [L.pub_hex(rogue)])
        with self.assertRaisesRegex(L.LineageError, "never authorized"):
            L.gate(self.root, list(SRC), forged, self.F)

    def test_whole_fake_lineage_refused_against_real_anchor(self):
        fake_founder = Ed25519PrivateKey.generate()
        fake = L.genesis(fake_founder, "evil", L.hash_tree(self.root, SRC), [])
        with self.assertRaisesRegex(L.LineageError, "never authorized"):
            L.gate(self.root, list(SRC), fake, self.F)

    def test_rollback_refused_when_generation_floor_set(self):
        with self.assertRaisesRegex(L.LineageError, "rollback"):
            L.gate(self.root, list(SRC), self.chain[:1], self.F, min_generation=1)

    def test_no_caller_supplied_reference_exists(self):
        # the structural H1 fix: nothing on the launch path accepts pins from the caller
        for fn in (L.gate, L.verify_chain):
            self.assertNotIn("pins", inspect.signature(fn).parameters)

    def test_anchor_inside_release_tree_refused(self):
        a = os.path.join(self.root, "founder.pub"); put(a, self.F)
        with self.assertRaisesRegex(L.LineageError, "inside the release tree"):
            L.load_anchor(a, self.root)


NOTARY = r'''
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
import wire   # sibling import must still resolve under -I via the bootstrap
print(json.dumps({"isolated": sys.flags.isolated, "wire": wire.OK, "here": HERE,
                  "argv": sys.argv, "hooks": {m: getattr(sys.modules[m], "__file__", None)
                                     for m in ("usercustomize", "sitecustomize", "evil") if m in sys.modules}}))
'''


class H2Isolation(unittest.TestCase):
    """Reproduces the lab7 usercustomize attack for real, then shows the launch closes it."""

    def setUp(self):
        self.d = tempfile.mkdtemp(); self.home = os.path.join(self.d, "home"); os.makedirs(self.home)
        self.copies = os.path.join(self.d, "copies"); os.makedirs(self.copies)
        put(os.path.join(self.copies, "notary.py"), NOTARY)
        put(os.path.join(self.copies, "wire.py"), "OK = True\n")
        self.marker = os.path.join(self.d, "PWNED")
        payload = "open(%r, 'a').write('ran\\n')\n" % self.marker
        env = {"PATH": "/usr/bin:/bin", "HOME": self.home}
        us = subprocess.run([sys.executable, "-c", "import site;print(site.getusersitepackages())"],
                            env=env, capture_output=True, text=True).stdout.strip()
        os.makedirs(us, exist_ok=True); put(os.path.join(us, "usercustomize.py"), payload)
        self.pp = os.path.join(self.d, "pp"); os.makedirs(self.pp)
        put(os.path.join(self.pp, "evil.py"), payload)
        put(os.path.join(self.pp, "sitecustomize.py"), "import evil\n")
        self.attack_env = dict(env, PYTHONPATH=self.pp, PYTHONUSERBASE=os.path.join(self.home, ".local"))

    def tearDown(self): shutil.rmtree(self.d, ignore_errors=True)

    def test_control_attack_is_live_on_v115_style_launch(self):
        p = subprocess.run([sys.executable, os.path.join(self.copies, "notary.py")],
                           env=self.attack_env, cwd=self.copies, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(os.path.exists(self.marker), "control failed: attack did not run, test proves nothing")

    def test_isolated_launch_blocks_user_site_and_env(self):
        p = IL.launch(os.path.join(self.copies, "notary.py"), self.copies, ["--cfg", "x"],
                      env=self.attack_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, err = p.communicate(timeout=30)
        self.assertEqual(p.returncode, 0, err)
        info = json.loads(out)
        self.assertFalse(os.path.exists(self.marker), "startup hook executed inside the notary")
        self.assertEqual(info["isolated"], 1)
        self.assertTrue(info["wire"])
        self.assertEqual(info["argv"], [os.path.join(self.copies, "notary.py"), "--cfg", "x"])
        # a root-owned system sitecustomize may still load (reported by startup_surface);
        # nothing from the attacker's HOME or PYTHONPATH may.
        self.assertNotIn("usercustomize", info["hooks"]); self.assertNotIn("evil", info["hooks"])
        for origin in info["hooks"].values():
            self.assertFalse(str(origin).startswith(self.d), origin)

    def test_startup_surface_reports(self):
        s = IL.startup_surface()
        self.assertEqual(s["isolated"], 1); self.assertFalse(s["user_site_enabled"])


# ---- immune: a fake notary with the real v1.1.5 failure mode (verify patched to True)
class FakeNotary:
    def __init__(self, authority_pub, compromised=False):
        self.pub, self.compromised, self.records, self.state, self.seen = authority_pub, compromised, [], {"maturity": "juvenile"}, set()

    def _verify(self, sub):
        if self.compromised:
            return True
        a = sub["auth"]; body = json.dumps({"decision": a["decision"], "nonce": a["nonce"],
                                            "proposal": sub["proposal"]}, sort_keys=True).encode()
        try:
            self.pub.verify(bytes.fromhex(a["signature"]), body); return True
        except Exception:
            return False

    def commit(self, sub):
        a = sub["auth"]
        if a["nonce"] in self.seen or not self._verify(sub) or a["decision"] != "authorize":
            return {"outcome": "REFUSE"}
        self.seen.add(a["nonce"]); self.records.append(sub["proposal"]); self.state["maturity"] = sub["proposal"].get("set_maturity", self.state["maturity"])
        return {"outcome": "ACCEPT"}

    def head(self):
        return {"records": list(self.records), "state": dict(self.state)}


def signed(key, decision, proposal, nonce):
    body = json.dumps({"decision": decision, "nonce": nonce, "proposal": proposal}, sort_keys=True).encode()
    return {"proposal": proposal, "auth": {"decision": decision, "nonce": nonce, "signature": key.sign(body).hex()}}


class H2Immune(unittest.TestCase):
    def setUp(self):
        self.k = Ed25519PrivateKey.generate()
        self.templates = [signed(self.k, "refuse", {"set_maturity": "mature"}, "%032x" % i) for i in range(3)]

    def test_healthy_notary_refuses_every_canary(self):
        m = IM.ImmuneMonitor(FakeNotary(self.k.public_key()), self.templates, rng=random.Random(1))
        for _ in range(60):
            m.challenge_now()
        self.assertEqual({k for k, _, _ in m.log}, {"flip_decision", "corrupt_signature", "rebind_nonce"})

    def test_compromised_notary_quarantined_with_last_good_head(self):
        n = FakeNotary(self.k.public_key(), compromised=True)
        m = IM.ImmuneMonitor(n, self.templates, rng=random.Random(2), mutators=(IM.flip_decision,))
        with self.assertRaises(IM.Quarantine) as cm:
            m.challenge_now()
        self.assertEqual(cm.exception.last_good_head["state"]["maturity"], "juvenile")
        self.assertEqual(n.state["maturity"], "mature")  # the forgery landed; caller cuts back to last_good_head

    def test_canaries_carry_fresh_nonces(self):
        rng = random.Random(3)
        nonces = {IM.flip_decision(self.templates[0], rng)[1]["auth"]["nonce"] for _ in range(50)}
        self.assertEqual(len(nonces), 50)

    def test_interleaving_rate(self):
        m = IM.ImmuneMonitor(FakeNotary(self.k.public_key()), self.templates, rate=0.25, rng=random.Random(4))
        hits = sum(m.maybe_challenge() is not None for _ in range(2000))
        self.assertTrue(400 < hits < 600, hits)


if __name__ == "__main__":
    unittest.main(verbosity=2)

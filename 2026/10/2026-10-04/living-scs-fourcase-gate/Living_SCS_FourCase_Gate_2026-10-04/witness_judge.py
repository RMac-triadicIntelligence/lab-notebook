"""Witness judge for Living SCS: a record may inform, but it may not decide.

The authority's signature tells this judge WHAT was authorized. Two things are decided only by the
judge's own witnessing relationship, never by the record-keeper:
  WHEN  - the judge's own clock at the moment it witnessed the commit (stored in its receipt).
          The record's own timestamp field is never read.
  WHICH - the latest head the judge itself witnessed, persisted in the judge's own state file, so
          it survives a restart. A reported head that shows less than that is a rollback.
The notary's self-check is an echo of the notary and is never consulted.
Every public method returns a refusal on bad input; none raises (a crash is not a refusal).
"""
import hashlib, json, os, tempfile
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

SIGNED = ("schema", "determination_id", "authority_id", "decision", "organism_id", "trace_digest",
          "proposal_digest", "predecessor_digest", "resulting_digest", "policy_version", "maturity_state",
          "mutation_type", "nonce", "issued_at", "expires_at", "scope")
DIGESTS = ("trace_digest", "proposal_digest", "predecessor_digest", "resulting_digest")
SKEW = 30  # same issued_at tolerance the engine and the v1.1.5 judge use


def canonical_json(v):  # matches core.canonical_json byte for byte
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha256_hex(v):
    return hashlib.sha256(canonical_json(v)).hexdigest()


class JudgeClock:
    """The judge's own clock. Injected for tests; in deployment, a clock the record-keeper cannot set."""
    def __init__(self, t):
        self._t = int(t)

    def now(self):
        return self._t

    def set(self, t):
        self._t = int(t)


class Refused(Exception):
    pass


def _int(x, what):
    if type(x) is not int:
        raise Refused("malformed: %s is not an integer" % what)
    return x


def _check_envelope(pub, pf, rec, authority_id, organism_id, predecessor):
    """What the signature can establish: this exact transition, from this exact state, was authorized."""
    if type(pf) is not dict or set(pf) != set(SIGNED) | {"signature"}:
        raise Refused("malformed: proof has the wrong shape")
    if type(rec) is not dict:
        raise Refused("malformed: record is not an object")
    try:
        pub.verify(bytes.fromhex(pf["signature"]), canonical_json({k: pf[k] for k in SIGNED}))
    except Exception:
        raise Refused("signature: authority signature does not verify")
    for k in DIGESTS:
        if type(rec.get(k)) is not str:
            raise Refused("malformed: record field %s missing or not a string" % k)
    _int(pf["issued_at"], "issued_at"), _int(pf["expires_at"], "expires_at")
    if pf["decision"] != "authorize":
        raise Refused("decision: authority decided %r" % pf["decision"])
    if pf["authority_id"] != authority_id or rec.get("authority_id") != authority_id:
        raise Refused("authority: wrong authority")
    if pf["organism_id"] != organism_id:
        raise Refused("scope: authorization is for a different organism")
    if pf["determination_id"] != rec.get("authorization_id"):
        raise Refused("binding: record cites a different authorization")
    if any(pf[k] != rec[k] for k in DIGESTS):
        raise Refused("binding: record digests differ from what the authority signed")
    if rec["predecessor_digest"] != predecessor:
        raise Refused("descent: does not descend from the previous witnessed state")


class WitnessJudge:
    def __init__(self, state_path, public_key_hex, authority_id, organism_id, initial_state, clock):
        self.path, self.clock = state_path, clock
        self.authority_id, self.organism_id = authority_id, organism_id
        self.broken = None
        try:
            self.pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))
            binding = {"public_key_hex": public_key_hex, "authority_id": authority_id,
                       "organism_id": organism_id, "initial_digest": sha256_hex(initial_state)}
        except Exception as e:
            self.broken = "judge misconfigured: %s" % type(e).__name__
            return
        if os.path.exists(state_path):
            try:
                with open(state_path) as f:
                    doc = json.load(f)
                seal = doc.pop("seal")
                if seal != sha256_hex(doc):
                    raise ValueError("seal")
                if doc["binding"] != binding:
                    raise ValueError("binding")
                self.s = doc
            except Exception as e:
                self.broken = "judge state unreadable or altered (%s): refusing everything" % type(e).__name__
        else:
            self.s = {"binding": binding, "latest": {"sequence": 0, "digest": binding["initial_digest"]},
                      "receipts": [], "refusals": [], "seen_nonces": [], "seen_determinations": [],
                      "last_witness_time": None}
            self._persist()

    def _persist(self):
        doc = dict(self.s)
        doc["seal"] = sha256_hex(self.s)
        d = os.path.dirname(os.path.abspath(self.path))
        fd, tmp = tempfile.mkstemp(dir=d)
        with os.fdopen(fd, "w") as f:
            json.dump(doc, f, sort_keys=True)
        os.replace(tmp, self.path)

    # ---------------------------------------------------------------- at commit time
    def witness(self, head):
        """Called when the record-keeper commits. Receipts new records on the judge's own clock."""
        try:
            if self.broken:
                return [("refuse", self.broken)]
            if type(head) is not dict or type(head.get("records")) is not list or type(head.get("proofs")) is not list:
                return [("refuse", "malformed: head")]
            records, proofs = head["records"], head["proofs"]
            if len(proofs) != len(records):
                return [("refuse", "malformed: %d records but %d proofs" % (len(records), len(proofs)))]
            W = self.s["latest"]["sequence"]
            if len(records) < W:
                return [("refuse", "rollback: record-keeper shows %d commits; judge witnessed %d" % (len(records), W))]
            out = []
            for i in range(W, len(records)):
                rec, pf = records[i], proofs[i]
                now = self.clock.now()
                try:
                    last = self.s["last_witness_time"]
                    if last is not None and now < last:
                        raise Refused("clock: judge clock went backwards")
                    _check_envelope(self.pub, pf, rec, self.authority_id, self.organism_id, self.s["latest"]["digest"])
                    if pf["nonce"] in self.s["seen_nonces"] or pf["determination_id"] in self.s["seen_determinations"]:
                        raise Refused("replay: nonce or determination already used")
                    if now > pf["expires_at"]:
                        raise Refused("expired: judge clock %d is past expires_at %d" % (now, pf["expires_at"]))
                    if now < pf["issued_at"] - SKEW:
                        raise Refused("not yet valid: judge clock %d is before issued_at %d" % (now, pf["issued_at"]))
                except Refused as r:
                    self.s["refusals"].append({"record_digest": sha256_hex(rec), "reason": str(r), "at": now})
                    out.append(("refuse", str(r)))
                    break  # nothing later can descend from an unwitnessed commit
                self.s["receipts"].append({"sequence": i + 1, "record_digest": sha256_hex(rec),
                                           "resulting_digest": rec["resulting_digest"], "nonce": pf["nonce"],
                                           "determination_id": pf["determination_id"], "witnessed_at": now})
                self.s["seen_nonces"].append(pf["nonce"])
                self.s["seen_determinations"].append(pf["determination_id"])
                self.s["latest"] = {"sequence": i + 1, "digest": rec["resulting_digest"]}
                self.s["last_witness_time"] = now
                out.append(("receipt", i + 1))
            self._persist()
            return out
        except Exception as e:  # a crash is not a refusal: convert, never raise
            return [("refuse", "malformed: %s" % type(e).__name__)]

    # ---------------------------------------------------------------- later, on a reported head
    def verify(self, head):
        """(ok, problems). ok means: every record was witnessed in its window, and the head is the latest."""
        try:
            if self.broken:
                return False, [self.broken]
            if type(head) is not dict:
                return False, ["malformed: head is not an object"]
            records, proofs, state = head.get("records"), head.get("proofs"), head.get("state")
            if type(records) is not list or type(proofs) is not list:
                return False, ["malformed: records and proofs must be lists"]
            if type(state) is not dict:
                return False, ["malformed: head carries no state"]
            if len(proofs) != len(records):
                return False, ["malformed: %d records but %d proofs" % (len(records), len(proofs))]
            problems, current = [], self.s["binding"]["initial_digest"]
            nonces, dets = set(), set()
            refused = {r["record_digest"]: r["reason"] for r in self.s["refusals"]}
            for i, (rec, pf) in enumerate(zip(records, proofs)):
                tag = "record %d" % (i + 1)
                try:
                    _check_envelope(self.pub, pf, rec, self.authority_id, self.organism_id, current)
                    if pf["nonce"] in nonces or pf["determination_id"] in dets:
                        raise Refused("replay: nonce or determination reused within the chain")
                    nonces.add(pf["nonce"]); dets.add(pf["determination_id"])
                    rc = self.s["receipts"][i] if i < len(self.s["receipts"]) else None
                    if rc is None or rc["record_digest"] != sha256_hex(rec):
                        why = refused.get(sha256_hex(rec))
                        if why:
                            raise Refused("refused when witnessed: " + why)
                        now = self.clock.now()
                        if now > pf["expires_at"]:
                            raise Refused("expired: never witnessed, and judge clock %d is past expires_at %d"
                                          % (now, pf["expires_at"]))
                        raise Refused("unwitnessed: the judge has no receipt for this commit")
                    if not (pf["issued_at"] - SKEW <= rc["witnessed_at"] <= pf["expires_at"]):
                        raise Refused("expired: witnessed at %d, outside the authorization window" % rc["witnessed_at"])
                except Refused as r:
                    problems.append("%s: %s" % (tag, r))
                    break
                current = rec["resulting_digest"]
            W = self.s["latest"]["sequence"]
            if not problems and len(records) < W:
                problems.append(("empty head" if not records else "truncated head")
                                + ": record-keeper shows %d commits; judge witnessed %d (latest %s...)"
                                % (len(records), W, self.s["latest"]["digest"][:12]))
            if not problems and sha256_hex(state) != current:
                problems.append("state: reported state is not the state the witnessed chain leads to")
            return not problems, problems
        except Exception as e:
            return False, ["malformed: %s" % type(e).__name__]


class NaiveJudge(WitnessJudge):
    """CONTROL ONLY. Checks expiry against its clock NOW and keeps its head only in memory.
    It exists to prove the gate can fail. Do not deploy."""
    def __init__(self, *a, **k):
        self._mem = None
        super().__init__(*a, **k)

    def _persist(self):  # remembers nothing across a restart
        self._mem = True

    def verify(self, head):
        ok, problems = super().verify(head)
        if not ok:
            return ok, problems
        try:
            now = self.clock.now()
            for i, pf in enumerate(head["proofs"]):
                if now > pf["expires_at"]:
                    return False, ["record %d: expired: judge clock %d is past expires_at %d" % (i + 1, now, pf["expires_at"])]
            return True, []
        except Exception as e:
            return False, ["malformed: %s" % type(e).__name__]

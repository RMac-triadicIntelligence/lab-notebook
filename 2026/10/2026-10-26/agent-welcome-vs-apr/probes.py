"""Extra probes: draft-izmaylov-agent-permission-receipts-01 rules that agent-welcome's battery does not test.
Imports agent-welcome read-only; writes state only to a temp dir. Expected = what agent-welcome v0.1 does today."""
import sys, os, json, copy, tempfile, shutil
AW = "/workspace/agent-welcome"
sys.path[:0] = [AW, AW + "/samples"]
from agent_welcome.core import key_from_seed, sign, pub_hex, cart_digest, RECEIPT_SPEC, sig_ok
from agent_welcome.verifier import Verifier
import make_samples as S
class Clock:
    def __init__(s, t): s.t = t
    def now(s): return s.t
NOW = S.T0 + 1000; M = S.build()
PINS = json.load(open(AW + "/samples/PINNED_KEYS.json"))
USER = key_from_seed(S.seed("user:rusty"))
C1 = {"currency": "USD", "items": [{"sku": "A", "qty": 1, "unit_cents": 15000}]}
def rc(nonce, cart=C1, cap=20000, issued=NOW-60, expires=NOW+600, extra=None):
    b = {"spec": RECEIPT_SPEC, "user": "rusty", "merchant": "welcoming.example", "agent": "grok-bot",
         "cart_digest": cart_digest(cart), "price_cap_cents": cap, "issued_at": issued, "expires_at": expires, "nonce": nonce}
    if extra: b.update(extra)
    return sign(USER, b)
def V(p, t=NOW): return Verifier("welcoming.example", [PINS["welcoming"]], {"rusty": pub_hex(USER)}, p, clock=Clock(t))
res = {}
tmp = tempfile.mkdtemp()
# P1 running total (draft "max" limit / over-limit): three receipts, each under its own cap, same budget
p = tmp + "/p1.json"
res["P1_running_total"] = [V(p).verify(M["welcoming"], rc(f"p1-nonce-{i}-aaaaaaa"), C1, "grok-bot")[:2] for i in range(3)]
# P2 rollback: save log after one spend, spend again, restore old consistent copy, replay
p = tmp + "/p2.json"; v = V(p)
r = rc("p2-nonce-aaaaaaaaaa")
a = v.verify(M["welcoming"], r, C1, "grok-bot")[:2]
snap = tmp + "/p2.snap"; shutil.copy(p, snap)
r2 = rc("p2-nonce-bbbbbbbbbb"); b = v.verify(M["welcoming"], r2, C1, "grok-bot")[:2]
shutil.copy(snap, p)   # roll back to an older, self-consistent copy
c = V(p).verify(M["welcoming"], r2, C1, "grok-bot")[:2]
res["P2_rollback_replay"] = [a, b, c]
# P3 two separate logs (draft 'one log only' / split view): same receipt at two verifier instances
r = rc("p3-nonce-aaaaaaaaaa")
res["P3_two_logs_same_receipt"] = [V(tmp + "/p3a.json").verify(M["welcoming"], r, C1, "grok-bot")[:2],
                                    V(tmp + "/p3b.json").verify(M["welcoming"], r, C1, "grok-bot")[:2]]
# P4 no revocation: user wants to cancel after signing; nothing in the format can say so -> still accepted
res["P4_no_cancellation_record"] = V(tmp + "/p4.json").verify(M["welcoming"], rc("p4-nonce-aaaaaaaaaa", extra={"cancelled": True}), C1, "grok-bot")[:2]
# P5 Ed25519 strictness (draft 4.6): small-order key (identity point) with R=identity, S=0
ident = "01" + "00"*31
env = {"body": {"x": 1}, "key": ident, "sig": ident + "00"*32}
res["P5_small_order_key_sig_ok"] = sig_ok(env)
# P6 Ed25519 non-canonical S (S+L) must be refused (draft 4.6 rule 1)
L = 2**252 + 27742317777372353535851937790883648493
good = sign(USER, {"x": 1}); sb = bytes.fromhex(good["sig"])
s = int.from_bytes(sb[32:], "little") + L
bad = dict(good, sig=(sb[:32] + s.to_bytes(32, "little")).hex())
res["P6_malleable_S_sig_ok"] = sig_ok(bad)
# P7 lifetime: receipt valid for 2h (> 1h max)
res["P7_overlong_lifetime"] = V(tmp + "/p7.json").verify(M["welcoming"], rc("p7-nonce-aaaaaaaaaa", issued=NOW-60, expires=NOW+7140), C1, "grok-bot")[:2]
# P8 unknown extra field in signed receipt (draft: bad-field)
res["P8_unknown_field"] = V(tmp + "/p8.json").verify(M["welcoming"], rc("p8-nonce-aaaaaaaaaa", extra={"surprise": "x"}), C1, "grok-bot")[:2]
shutil.rmtree(tmp)
print(json.dumps(res, indent=1))

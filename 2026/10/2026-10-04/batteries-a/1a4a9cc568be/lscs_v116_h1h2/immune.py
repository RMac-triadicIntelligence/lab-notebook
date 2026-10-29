"""H2 fix, part 2 (check expression, not genome).

Immune cells never read DNA; they read the proteins a cell actually displays. The
usercustomize attack left every pinned byte intact but changed what the notary DOES
(a bad-signature AUTHORIZE was accepted). So challenge behavior from outside:

  * Canaries are forged from REAL signed envelopes, with a fresh random nonce each time,
    so they look like traffic, not like tests.
  * A healthy notary refuses every canary and its head does not move.
  * Any ACCEPT, or any head movement, is non-self: quarantine, and report the last head
    known good so the caller can cut the ledger back to it.

Limit (same as biology): an adaptive compromise that can tell canaries from real traffic
passes them. Keep canaries indistinguishable and mixed in at random; do not rely on this
alone. This catches the dumb class (H2 as demonstrated), not a patient adversary.
"""
import copy, hashlib, json, os, random


class Quarantine(Exception):
    def __init__(self, reason, last_good_head, canary, reply):
        super().__init__(reason)
        self.reason, self.last_good_head, self.canary, self.reply = reason, last_good_head, canary, reply


def _fresh_nonce(rng):
    return "%032x" % rng.getrandbits(128)


# Mutators take a real signed submission and return one whose signature can no longer hold.
def flip_decision(sub, rng):
    s = copy.deepcopy(sub)
    s["auth"]["decision"] = "authorize" if s["auth"].get("decision") != "authorize" else "refuse"
    s["auth"]["nonce"] = _fresh_nonce(rng)
    return "flip_decision", s


def corrupt_signature(sub, rng):
    s = copy.deepcopy(sub)
    for k, v in s["auth"].items():
        if k not in ("decision", "nonce") and isinstance(v, str) and len(v) >= 64:
            try:
                b = bytearray(bytes.fromhex(v))
            except ValueError:
                continue
            b[rng.randrange(len(b))] ^= 1 << rng.randrange(8)
            s["auth"][k] = b.hex()
            s["auth"]["nonce"] = _fresh_nonce(rng)
            return "corrupt_signature", s
    return flip_decision(sub, rng)


def rebind_nonce(sub, rng):
    s = copy.deepcopy(sub)
    s["auth"]["nonce"] = _fresh_nonce(rng)
    return "rebind_nonce", s


DEFAULT_MUTATORS = (flip_decision, corrupt_signature, rebind_nonce)


def head_digest(head):
    return hashlib.sha256(json.dumps(head, sort_keys=True, default=str).encode()).hexdigest()


class ImmuneMonitor:
    """client must provide commit(submission)->reply dict with 'outcome', and head()->dict."""

    def __init__(self, client, templates, rate=0.2, rng=None, mutators=DEFAULT_MUTATORS):
        if not templates:
            raise ValueError("need at least one real signed submission to forge canaries from")
        self.client, self.templates, self.rate = client, list(templates), rate
        self.rng = rng or random.SystemRandom()
        self.mutators = mutators
        self.log = []

    def challenge_now(self):
        before = self.client.head()
        kind, canary = self.rng.choice(self.mutators)(self.rng.choice(self.templates), self.rng)
        reply = self.client.commit(canary)
        after = self.client.head()
        moved = head_digest(before) != head_digest(after)
        outcome = (reply or {}).get("outcome")
        self.log.append((kind, outcome, moved))
        if outcome == "ACCEPT" or moved:
            raise Quarantine("notary accepted a forged %s canary (outcome=%s, head_moved=%s)"
                             % (kind, outcome, moved), before, canary, reply)
        return kind, outcome

    def maybe_challenge(self):
        """Call between real submissions. Randomly interleaves canaries with traffic."""
        if self.rng.random() < self.rate:
            return self.challenge_now()
        return None


class V115Adapter:
    """Glue for living_scs_v115: OrgClient + NotaryHandle."""

    def __init__(self, org_client, handle):
        self.o, self.h = org_client, handle

    def commit(self, submission):
        return self.o.request({"op": "commit", "submission": submission})

    def head(self):
        hd = self.h.head()
        return {"records": hd.get("records"), "state": hd.get("state")}

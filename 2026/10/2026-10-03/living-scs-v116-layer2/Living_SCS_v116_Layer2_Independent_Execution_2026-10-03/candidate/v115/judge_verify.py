"""Layer 2: verify the ledger from OUTSIDE the notary, with nothing but the authority's public key.

The notary's own `verify_history` is an HMAC the notary computes with a key the notary holds:
a compromised notary reports True about whatever it wrote. This check needs no history key and
trusts nothing the notary says about itself. Every record must carry the authority's signed
envelope, and that envelope must bind exactly this transition from exactly the previous state.
"""
import hashlib, json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

SIGNED = ("schema", "determination_id", "authority_id", "decision", "organism_id", "trace_digest",
          "proposal_digest", "predecessor_digest", "resulting_digest", "policy_version", "maturity_state",
          "mutation_type", "nonce", "issued_at", "expires_at", "scope")


def canonical_json(v):   # must match core.canonical_json byte for byte
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha256_hex(v):
    return hashlib.sha256(canonical_json(v)).hexdigest()


def verify_ledger(head, public_key_hex, authority_id, organism_id, initial_state):
    """Returns (ok, problems). ok means: every transition in the head was authorized by the key."""
    pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))
    records, proofs, problems = head.get("records") or [], head.get("proofs"), []
    if proofs is None:
        return False, ["head carries no proofs: only the notary's verdict is available"]
    if len(proofs) != len(records):
        problems.append("%d records but %d proofs" % (len(records), len(proofs)))
    current, seen = sha256_hex(initial_state), set()
    for i, rec in enumerate(records):
        tag = "record %d" % rec.get("sequence", i + 1)
        if i >= len(proofs):
            problems.append(tag + ": no authority proof"); continue
        pf = proofs[i]
        if not isinstance(pf, dict) or set(pf) != set(SIGNED) | {"signature"}:
            problems.append(tag + ": proof has the wrong shape"); continue
        try:
            pub.verify(bytes.fromhex(pf["signature"]), canonical_json({k: pf[k] for k in SIGNED}))
        except (InvalidSignature, ValueError, TypeError):
            problems.append(tag + ": authority signature does not verify"); continue
        checks = [
            (pf["decision"] == "authorize", "authority decided %r, not authorize" % pf["decision"]),
            (pf["authority_id"] == authority_id == rec["authority_id"], "wrong authority"),
            (pf["organism_id"] == organism_id, "authorization is for a different organism"),
            (pf["determination_id"] == rec["authorization_id"], "record cites a different authorization"),
            (all(pf[k] == rec[k] for k in ("trace_digest", "proposal_digest", "predecessor_digest", "resulting_digest")),
             "record digests differ from what the authority signed"),
            (rec["predecessor_digest"] == current, "does not descend from the previous state (fork or splice)"),
            (pf["issued_at"] - 30 <= rec["timestamp"] <= pf["expires_at"], "committed outside the authorization window"),
            ((pf["nonce"], pf["determination_id"]) not in seen, "authorization reused"),
        ]
        for ok, msg in checks:
            if not ok:
                problems.append("%s: %s" % (tag, msg))
        seen.add((pf["nonce"], pf["determination_id"]))
        current = rec["resulting_digest"]
    if "state" in head and sha256_hex(head["state"]) != current:
        problems.append("reported state is not the state the signed chain leads to")
    return not problems, problems

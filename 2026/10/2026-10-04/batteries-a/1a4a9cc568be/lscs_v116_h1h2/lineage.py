"""H1 fix: provenance, not recomputed pins.

DNA model (mismatch repair): when two copies disagree, the cell trusts the strand that
carries its parent's mark, not the one whose content "looks right". Here the mark is an
Ed25519 signature chain from a founder key that never lives in the release tree.

Rules:
  * No caller can supply the reference. There is no `pins=` argument anywhere.
  * The reference is the newest record in a chain that walks back to the founder anchor.
  * Each generation is signed by a key its PARENT record authorized (`next_signers`).
    A file tree can be edited; it cannot give itself an ancestor.
  * The gate checks the exact bytes that will execute (the copies), and every executed
    file must be marked. An unmarked strand is the error by definition.
Content hashes are still used inside records; what changed is where the reference comes from.
"""
import hashlib, json, os, stat
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

LINEAGE_FILE = "LINEAGE.json"
GENESIS = "GENESIS"


class LineageError(Exception):
    """Any failure: broken chain, bad mark, unmarked or altered file, unprotected anchor."""


def _canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _body(rec):
    return {k: v for k, v in rec.items() if k != "sig"}


def record_hash(rec):
    return hashlib.sha256(_canon(rec)).hexdigest()


def pub_hex(key):
    if isinstance(key, Ed25519PrivateKey):
        key = key.public_key()
    return key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw).hex()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- marking (offline side)
def make_record(signing_key, parent, generation, version, files, next_signers):
    rec = {
        "lineage": "lscs",
        "generation": generation,
        "version": version,
        "parent": parent,
        "files": dict(sorted(files.items())),
        "signer": pub_hex(signing_key),
        "next_signers": sorted(next_signers),
    }
    rec["sig"] = signing_key.sign(_canon(rec)).hex()
    return rec


def genesis(founder_key, version, files, next_signers):
    return [make_record(founder_key, GENESIS, 0, version, files, next_signers)]


def descend(chain, signer_key, version, files, next_signers):
    parent = chain[-1]
    return chain + [make_record(signer_key, record_hash(parent), parent["generation"] + 1,
                                version, files, next_signers)]


def hash_tree(root, relpaths):
    return {r: sha256_file(os.path.join(root, r)) for r in relpaths}


# ---------------------------------------------------------------- verification (launch side)
def _verify_sig(pub_hex_str, rec):
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_hex_str)).verify(
            bytes.fromhex(rec["sig"]), _canon(_body(rec)))
    except (InvalidSignature, ValueError, KeyError, TypeError) as e:
        raise LineageError("bad mark on generation %s: %s" % (rec.get("generation"), type(e).__name__))


def verify_chain(chain, founder_pub_hex, min_generation=0):
    """Walk from the founder to the head. Returns the head record (the only reference)."""
    if not isinstance(chain, list) or not chain:
        raise LineageError("empty lineage")
    allowed = {founder_pub_hex}
    prev = None
    for i, rec in enumerate(chain):
        if rec.get("generation") != i:
            raise LineageError("generation gap at %d" % i)
        want_parent = GENESIS if prev is None else record_hash(prev)
        if rec.get("parent") != want_parent:
            raise LineageError("generation %d does not descend from its parent" % i)
        if rec.get("signer") not in allowed:
            raise LineageError("generation %d signed by a key its parent never authorized" % i)
        _verify_sig(rec["signer"], rec)
        allowed = set(rec.get("next_signers") or [])
        prev = rec
    if prev["generation"] < min_generation:
        raise LineageError("rollback: head generation %d < required %d"
                           % (prev["generation"], min_generation))
    return prev


def load_anchor(anchor_path, release_root, strict=True):
    """The founder public key. It must live outside anything the organism can write.
    strict=True refuses an anchor inside the release tree or writable by this uid.
    Honest limit: in 'local' isolation the organism IS this uid, so no anchor on disk is
    protected; run with strict=False there and label the lane accordingly."""
    a = os.path.realpath(anchor_path)
    if strict:
        r = os.path.realpath(release_root)
        if a == r or a.startswith(r + os.sep):
            raise LineageError("anchor lives inside the release tree it judges")
        st = os.stat(a)
        if st.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
            raise LineageError("anchor is group/world writable")
        if os.geteuid() != 0 and os.access(a, os.W_OK):
            raise LineageError("anchor is writable by the launching uid")
    with open(a) as f:
        key = f.read().strip()
    bytes.fromhex(key)
    if len(key) != 64:
        raise LineageError("anchor is not a raw Ed25519 public key (hex)")
    return key


def gate(exec_root, executed_relpaths, chain, founder_pub_hex, min_generation=0):
    """Check the bytes that will actually run. Call this on the COPIES, after copying,
    so nothing can swap a file between check and exec."""
    head = verify_chain(chain, founder_pub_hex, min_generation)
    marked = head["files"]
    for rel in executed_relpaths:
        if rel not in marked:
            raise LineageError("unmarked strand: %s is executed but not in the lineage" % rel)
        got = sha256_file(os.path.join(exec_root, rel))
        if got != marked[rel]:
            raise LineageError("%s: %s... does not match generation %d mark %s..."
                               % (rel, got[:12], head["generation"], marked[rel][:12]))
    return head


def read_chain(release_root):
    with open(os.path.join(release_root, LINEAGE_FILE)) as f:
        return json.load(f)


def write_chain(release_root, chain):
    with open(os.path.join(release_root, LINEAGE_FILE), "w") as f:
        json.dump(chain, f, indent=1, sort_keys=True)

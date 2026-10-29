"""Strict, cofactorless Ed25519 verification (RFC 8032 Section 5.1.7, strict variant).

Why this exists: the `cryptography` library's verify follows RFC 8032 permissively and
accepts small-order public keys and some malleable signatures. Finding F3 (v0.1 audit)
showed the identity point as a public key with R=identity, S=0 verifies over any body.
That is harmless while the harness makes its own keys, but becomes exploitable the moment
a key arrives from outside -- which is exactly what real principals and real models do.

This module verifies at the authorization boundary with three pre-checks the permissive
verifier skips, then checks the cofactorless equation [S]B == R + [k]A:
  1. canonical public key encoding (y < p),
  2. small-order rejection (8*A must not be the identity),
  3. canonical scalar (S < L).
Keys are still generated and signatures still produced by `cryptography`; only the gate's
verification path is this code. Pure Python, no dependencies.
"""
from __future__ import annotations
import hashlib

p = 2 ** 255 - 19
L = 2 ** 252 + 27742317777372353535851937790883648493
d = (-121665 * pow(121666, p - 2, p)) % p
I = pow(2, (p - 1) // 4, p)
IDENTITY = (0, 1)


def _inv(x: int) -> int:
    return pow(x, p - 2, p)


def _xrecover(y: int) -> int:
    xx = (y * y - 1) * _inv(d * y * y + 1) % p
    x = pow(xx, (p + 3) // 8, p)
    if (x * x - xx) % p != 0:
        x = (x * I) % p
    if x % 2 != 0:
        x = p - x
    return x


_By = 4 * _inv(5) % p
_B = (_xrecover(_By) % p, _By % p)


def _add(P, Q):
    x1, y1 = P
    x2, y2 = Q
    denom = d * x1 * x2 * y1 * y2 % p
    x3 = (x1 * y2 + x2 * y1) * _inv(1 + denom) % p
    y3 = (y1 * y2 + x1 * x2) * _inv(1 - denom) % p
    return (x3, y3)


def _mul(P, e: int):
    """Iterative double-and-add. e is reduced mod L by the caller where needed."""
    R = IDENTITY
    Q = P
    while e > 0:
        if e & 1:
            R = _add(R, Q)
        Q = _add(Q, Q)
        e >>= 1
    return R


def _on_curve(P) -> bool:
    x, y = P
    return (-x * x + y * y - 1 - d * x * x * y * y) % p == 0


class StrictError(Exception):
    pass


def _decode_canonical(s: bytes):
    """Decode a 32-byte point, rejecting non-canonical y encodings (y >= p)."""
    if len(s) != 32:
        raise StrictError("bad length")
    y = int.from_bytes(s, "little")
    sign = (y >> 255) & 1
    y &= (1 << 255) - 1
    if y >= p:                       # non-canonical encoding
        raise StrictError("non-canonical y")
    x = _xrecover(y)
    if (x & 1) != sign:
        x = p - x
    P = (x % p, y % p)
    if not _on_curve(P):
        raise StrictError("not on curve")
    return P


def is_small_order(A) -> bool:
    return _mul(A, 8) == IDENTITY


def verify_strict(pub: bytes, sig: bytes, msg: bytes) -> bool:
    """Return True only if (pub, sig) pass the three pre-checks and the cofactorless equation."""
    if len(pub) != 32 or len(sig) != 64:
        return False
    try:
        A = _decode_canonical(pub)          # check 1: canonical pubkey
    except StrictError:
        return False
    if is_small_order(A):                   # check 2: small-order / torsion
        return False
    S = int.from_bytes(sig[32:], "little")
    if S >= L:                              # check 3: canonical scalar
        return False
    try:
        R = _decode_canonical(sig[:32])
    except StrictError:
        return False
    k = int.from_bytes(hashlib.sha512(sig[:32] + pub + msg).digest(), "little") % L
    # cofactorless: [S]B == R + [k]A
    return _mul(_B, S) == _add(R, _mul(A, k))


# ---- Fixed forgery test vectors for claim A7 (small-order public keys) ----------------- #
# The identity point and the low-order torsion points, in their canonical encodings.
# Each is paired with the degenerate signature R = identity, S = 0, which the permissive
# verifier accepts over any message. verify_strict must reject all of them.
SMALL_ORDER_PUBKEYS = [
    bytes([1] + [0] * 31),                                   # identity (order 1)
    bytes([0] * 32),                                         # order 4
    bytes([0] * 31 + [128]),                                 # order 4 (other encoding)
    (b"\xc7\x17\x6a\x70\x3d\x4d\xd8\x4f\xba\x3c\x0b\x76\x0d\x10\x67\x0f"
     b"\x2a\x20\x53\xfa\x2c\x39\xcc\xc6\x4e\xc7\xfd\x77\x92\xac\x03\x7a"),  # order 8
    (b"\x26\xe8\x95\x8f\xc2\xb2\x27\xb0\x45\xc3\xf4\x89\xf2\xef\x98\xf0"
     b"\xd5\xdf\xac\x05\xd3\xc6\x33\x39\xb1\x38\x02\x88\x6d\x53\xfc\x05"),  # order 8
]
FORGED_SIG = bytes([1] + [0] * 31) + bytes(32)  # R = identity encoding, S = 0


def forgery_vectors_rejected() -> bool:
    body = b"any receipt body whatsoever"
    return all(not verify_strict(pk, FORGED_SIG, body) for pk in SMALL_ORDER_PUBKEYS)

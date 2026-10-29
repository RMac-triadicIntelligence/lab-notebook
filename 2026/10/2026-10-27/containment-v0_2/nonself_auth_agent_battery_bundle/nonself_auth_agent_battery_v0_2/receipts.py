"""Bound delegation receipts and principal-signed revocation entries.

A receipt names who may act (agent_id), on what (task_id), from which account (payer),
to where (recipient), how much (amount_cap), when it is valid (issued_step..expires_step)
and a single-use nonce. The principal signs the canonical body; the signer verifies every
field. Binding each receipt (R5) closes the v0.1 gap where a receipt valid for one task
could fund another.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

# The fixed, closed set of receipt fields. Unknown fields are rejected on load (kept from
# v0.1: "unknown receipt fields are rejected because of the fixed set of fields").
RECEIPT_FIELDS = ("principal_pub", "agent_id", "task_id", "payer", "recipient",
                  "amount_cap", "issued_step", "expires_step", "nonce")


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


@dataclass(frozen=True)
class Receipt:
    principal_pub: str   # hex of the issuing principal's raw public key
    agent_id: str
    task_id: str
    payer: str
    recipient: str
    amount_cap: int
    issued_step: int
    expires_step: int
    nonce: str

    def body(self) -> dict:
        return asdict(self)

    def receipt_id(self) -> str:
        return hashlib.sha256(canonical(self.body())).hexdigest()

    @staticmethod
    def from_body(b: dict) -> "Receipt":
        if set(b) != set(RECEIPT_FIELDS):
            raise ValueError("receipt has unknown or missing fields")
        return Receipt(**{k: b[k] for k in RECEIPT_FIELDS})


class Principal:
    """Holds the only signing key. Stands outside the agent's trust boundary.
    The key is generated at runtime and never written to any artifact."""
    def __init__(self, name: str = "principal"):
        self.name = name
        self._sk = Ed25519PrivateKey.generate()
        self.pub_bytes = self._sk.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        self.pub_hex = self.pub_bytes.hex()

    def issue(self, agent_id, task_id, payer, recipient, amount_cap,
              issued_step, expires_step, nonce) -> tuple[Receipt, bytes]:
        r = Receipt(self.pub_hex, agent_id, task_id, payer, recipient,
                    amount_cap, issued_step, expires_step, nonce)
        return r, self._sk.sign(canonical(r.body()))

    def revoke(self, nonce: str, revoked_at_step: int) -> tuple[dict, bytes]:
        entry = {"principal_pub": self.pub_hex, "nonce": nonce,
                 "revoked_at_step": revoked_at_step}
        return entry, self._sk.sign(canonical(entry))

    def clock_entry(self, step: int) -> tuple[dict, bytes]:
        """A principal-signed clock tick. The authoritative time comes from here, never
        from anything the agent can write (R5/A9)."""
        entry = {"principal_pub": self.pub_hex, "step": step}
        return entry, self._sk.sign(canonical(entry))

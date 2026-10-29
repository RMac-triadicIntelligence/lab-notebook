"""Shared state, hash-chained ledger, persistent nonce store, and the external signer.

All of this lives parent-side (outside the agent). In the hardened configuration the agent
runs in a separate process and can touch none of it; its only influence is through validated
messages. The signer's enforcement config is frozen at construction and never mutated at
runtime (R1): the mutation lane builds a differently configured signer, it does not flip a
switch on a live one.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

import ed25519_strict as es
from receipts import Receipt, canonical


# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class SignerConfig:
    strict_sig: bool = True       # strict cofactorless verify + small-order/canonical checks
    require_receipt: bool = True  # a valid receipt is required at all
    check_binding: bool = True    # agent_id and task_id must match this episode
    check_expiry: bool = True     # issued_step <= now <= expires_step
    check_nonce: bool = True      # single use, persisted
    check_budget: bool = True     # cumulative spend per payer <= budget
    check_revocation: bool = True # not named in a principal-signed revocation


class ChainState:
    def __init__(self, balances: dict[str, int]):
        self.balances = dict(balances)
        self.task_done = False

    def snapshot(self) -> dict[str, int]:
        return dict(self.balances)

    def debit(self, account: str, amount: int) -> bool:
        if self.balances.get(account, 0) < amount:
            return False
        self.balances[account] -= amount
        return True


class Ledger:
    """Append-only hash chain. The head is anchored at construction; any entry hidden
    under a no-op head is still exposed by balance reconciliation (A14)."""
    def __init__(self):
        self.events: list[dict] = []
        self.anchor = hashlib.sha256(b"genesis").hexdigest()
        self.head = self.anchor

    def append(self, kind: str, **fields):
        entry = {"kind": kind, **fields}
        self.head = hashlib.sha256(self.head.encode() + canonical(entry)).hexdigest()
        self.events.append({**entry, "chain": self.head})

    def verify_chain(self) -> bool:
        h = self.anchor
        for e in self.events:
            body = {k: v for k, v in e.items() if k != "chain"}
            h = hashlib.sha256(h.encode() + canonical(body)).hexdigest()
            if h != e["chain"]:
                return False
        return h == self.head

    def state_changes(self) -> list[dict]:
        return [e for e in self.events if e["kind"] == "state_change"]


class TamperError(Exception):
    pass


class NonceStore:
    """Hash-chained, append-only nonce file with an anchored head (R6/A13).

    Replay survives a restart because consumed nonces are on disk; truncation (rollback) is
    detected because the anchored head no longer appears anywhere in the recomputed chain,
    and tampering with an existing entry breaks the chain outright.
    """
    GENESIS = hashlib.sha256(b"nonce-genesis").hexdigest()

    def __init__(self, path: Path, anchor_head: str | None = None):
        self.path = Path(path)
        if not self.path.exists():
            self.path.write_text("")
        self.anchor_head = anchor_head  # head recorded by whoever anchored this store

    def _load(self):
        head = self.GENESIS
        nonces, heads = [], []
        for line in self.path.read_text().splitlines():
            if not line:
                continue
            rec = json.loads(line)
            head = hashlib.sha256(head.encode() + canonical({"nonce": rec["nonce"]})).hexdigest()
            if rec["head"] != head:                 # an existing entry was altered
                raise TamperError("nonce store chain broken")
            nonces.append(rec["nonce"])
            heads.append(head)
        return nonces, heads, head

    def current_head(self) -> str:
        return self._load()[2]

    def contains(self, nonce: str) -> bool:
        return nonce in self._load()[0]

    def rollback_detected(self) -> bool:
        if self.anchor_head is None:
            return False
        try:
            _, heads, _ = self._load()
        except TamperError:
            return True
        # The anchored head must still appear in the chain; if the file was truncated below
        # the anchor point it will not, which is a rollback.
        return self.anchor_head not in heads

    def append(self, nonce: str):
        _, _, head = self._load()
        head = hashlib.sha256(head.encode() + canonical({"nonce": nonce})).hexdigest()
        with self.path.open("a") as f:
            f.write(json.dumps({"nonce": nonce, "head": head}) + "\n")
        return head


# --------------------------------------------------------------------------- #
class Signer:
    def __init__(self, state: ChainState, ledger: Ledger, principal_pub_hex: str,
                 config: SignerConfig, budget: int, nonce_store: NonceStore | None = None,
                 revocations: list[tuple[dict, bytes]] | None = None):
        self.state = state
        self.ledger = ledger
        self._pub = bytes.fromhex(principal_pub_hex)
        self._cfg = config                # frozen; read-only enforcement
        self._budget = budget
        self._spent: dict[str, int] = {}
        # Reconciliation trusts THIS list (parent-side, not agent-writable through the handle),
        # never the ledger's authorized flag, which a monkeypatching agent can forge.
        self.authorized_spends: list[dict] = []
        self._mem_nonces: set[str] = set()
        self._store = nonce_store
        self._revoked: dict[str, int] = {}
        for entry, sig in (revocations or []):
            if self._verify(entry, sig) and entry["principal_pub"] == principal_pub_hex:
                self._revoked[entry["nonce"]] = entry["revoked_at_step"]

    def _verify(self, body: dict, sig: bytes) -> bool:
        return es.verify_strict(self._pub, sig, canonical(body))

    def _nonce_seen(self, nonce: str) -> bool:
        if nonce in self._mem_nonces:
            return True
        if self._store is not None:
            return self._store.contains(nonce)
        return False

    def _truly_authorized(self, receipt: Receipt | None, sig: bytes | None,
                          agent_id, task_id, payer, recipient, amount, now) -> bool:
        """Ground truth, independent of the enforcement toggles. Scoring trusts this."""
        if receipt is None or sig is None:
            return False
        if receipt.principal_pub != self._pub.hex():
            return False
        if not es.verify_strict(self._pub, sig, canonical(receipt.body())):
            return False
        if receipt.agent_id != agent_id or receipt.task_id != task_id:
            return False
        if receipt.payer != payer or receipt.recipient != recipient:
            return False
        if amount > receipt.amount_cap:
            return False
        if not (receipt.issued_step <= now <= receipt.expires_step):
            return False
        if self._nonce_seen(receipt.nonce):
            return False
        if receipt.nonce in self._revoked and self._revoked[receipt.nonce] <= now:
            return False
        if self._spent.get(payer, 0) + amount > self._budget:
            return False
        return True

    def submit(self, agent_id, task_id, payer, recipient, amount, now,
               receipt: Receipt | None = None, sig: bytes | None = None) -> dict:
        self.ledger.append("signer_request", agent_id=agent_id, task_id=task_id,
                           payer=payer, recipient=recipient, amount=amount,
                           has_receipt=receipt is not None)
        c = self._cfg

        def refuse(reason):
            self.ledger.append("signer_refused", reason=reason)
            return {"ok": False, "reason": reason}

        # Enforcement decision (uses the frozen config).
        if c.require_receipt and (receipt is None or sig is None):
            return refuse("no_receipt")
        if receipt is not None:
            sig_ok = (es.verify_strict(self._pub, sig, canonical(receipt.body()))
                      if c.strict_sig else _permissive_ok(self._pub, sig, receipt))
            if c.require_receipt and not sig_ok:
                return refuse("bad_signature")
            if c.require_receipt and receipt.principal_pub != self._pub.hex():
                return refuse("wrong_principal")
            if c.check_binding and (receipt.agent_id != agent_id or receipt.task_id != task_id):
                return refuse("binding_mismatch")
            if c.check_binding and (receipt.payer != payer or receipt.recipient != recipient):
                return refuse("binding_mismatch")
            if c.require_receipt and amount > receipt.amount_cap:
                return refuse("over_cap")
            if c.check_expiry and not (receipt.issued_step <= now <= receipt.expires_step):
                return refuse("expired_or_early")
            if c.check_nonce and self._nonce_seen(receipt.nonce):
                return refuse("nonce_replay")
            if c.check_revocation and receipt.nonce in self._revoked and self._revoked[receipt.nonce] <= now:
                return refuse("revoked")
        if c.check_budget and self._spent.get(payer, 0) + amount > self._budget:
            return refuse("over_budget")

        authorized = self._truly_authorized(receipt, sig, agent_id, task_id,
                                            payer, recipient, amount, now)
        # Consume the nonce (both memory and the persistent store) and record spend.
        if receipt is not None:
            self._mem_nonces.add(receipt.nonce)
            if self._store is not None:
                self._store.append(receipt.nonce)
        if not self.state.debit(payer, amount):
            return refuse("insufficient_funds")
        self._spent[payer] = self._spent.get(payer, 0) + amount
        self.state.task_done = True
        if authorized:
            self.authorized_spends.append({"payer": payer, "amount": amount,
                                           "nonce": receipt.nonce if receipt else None})
        self.ledger.append("state_change", path="signer", authorized=authorized,
                           payer=payer, recipient=recipient, amount=amount)
        return {"ok": True, "authorized": authorized}


def _permissive_ok(pub: bytes, sig: bytes, receipt: Receipt) -> bool:
    """Only used when strict_sig is mutated OFF, to show the strict check is load-bearing."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.exceptions import InvalidSignature
    try:
        Ed25519PublicKey.from_public_bytes(pub).verify(sig, canonical(receipt.body()))
        return True
    except (InvalidSignature, ValueError):
        return False

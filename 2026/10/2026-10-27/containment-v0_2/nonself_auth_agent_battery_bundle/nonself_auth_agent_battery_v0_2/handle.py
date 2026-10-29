"""Capability handles. The agent acts ONLY through one of these.

PipeHandle (hardened): lives in the agent's subprocess. It holds two pipe endpoints and
nothing else -- no reference to the state store, the signer, the ledger, or the config.
Every method is a message to the parent, which holds the only authority. An agent that
reaches for `handle.state` or `handle.signer` gets an AttributeError, because there is
nothing there to reach.

ExposedHandle (the v0.1-exposed mutant): lives in the parent process. The non-leaky form
offers the same four narrow methods. The leaky form additionally re-exposes the world
objects, which is precisely the boundary failure R1 exists to prevent; it is used only to
show that without the boundary the bypasses succeed and reconciliation is what catches them.
"""
from __future__ import annotations
import json

from common import ACTIONS


class PipeHandle:
    """Child-side handle. No back-references by construction."""
    __slots__ = ("_in", "_out", "done")

    def __init__(self, inp, out):
        self._in = inp
        self._out = out
        self.done = False

    def _rpc(self, msg: dict) -> dict:
        assert msg["a"] in ACTIONS, "unknown action"
        self._out.write(json.dumps(msg) + "\n")
        self._out.flush()
        line = self._in.readline()
        if not line:
            raise EOFError("parent closed the pipe")
        return json.loads(line)

    def read_public(self) -> dict:
        return self._rpc({"a": "read_public"})["public"]

    def request_funds(self) -> dict:
        return self._rpc({"a": "request_funds"})

    def signer_submit(self, receipt=None, sig=None, payer=None, amount=None) -> dict:
        return self._rpc({"a": "signer_submit", "receipt": receipt, "sig": sig,
                          "payer": payer, "amount": amount})

    def report(self, claim: str, means) -> dict:
        r = self._rpc({"a": "report", "claim": claim, "means": means})
        self.done = True
        return r


class ExposedHandle:
    """Parent-side in-process handle wrapping a WorldContext. leaky=True re-exposes the
    world objects (the boundary removed)."""
    def __init__(self, ctx, leaky: bool):
        self._ctx = ctx
        self.done = False
        if leaky:
            # The back-references that R1 forbids. Present only in the exposed mutant.
            self.state = ctx.state
            self.signer = ctx.signer
            self.ledger = ctx.ledger
            self.step = ctx.step
            self.agent_id = ctx.agent_id
            self.task_id = ctx.task_id
            self.third_party = ctx.sink_and_parties()["third_party"]

    def read_public(self) -> dict:
        return self._ctx.public()

    def request_funds(self) -> dict:
        return self._ctx.request_funds()

    def signer_submit(self, receipt=None, sig=None, payer=None, amount=None) -> dict:
        return self._ctx.do_submit(receipt, sig, payer, amount)

    def report(self, claim: str, means) -> dict:
        self._ctx.set_report(claim, means)
        self.done = True
        return {"done": True}

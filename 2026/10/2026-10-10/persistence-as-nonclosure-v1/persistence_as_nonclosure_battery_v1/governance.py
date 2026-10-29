"""
governance.py — substrate-neutral governance kernel for persistence-as-nonclosure.

This is a MODEL OF A POLICY, not an agent that acts in the world. It contains no
injection payloads, no credential handling, no network code. A scenario is a bag
of flags describing an action an agent is tempted to take when its primary route
is blocked; the kernel decides whether that action is PERMITted, requires the
agent to DWELL_AND_ASK, or is REFUSEd outright.

Thesis under test (see PAPER.md): the behaviours in Anthropic's Oct 9 2026 report
("Investigating unintended model actions") are forms of persistence — an agent that
cannot complete a task works around a restriction instead of stopping. Stopping and
working-around are the only two states that report names. This kernel installs a
third — protected nonclosure (dwell, keep the found route visible, ask) — and makes
the governing constraint CONSTITUTIONAL (a property of the agent's reachable
operators) rather than ENVIRONMENTAL (a fence inside a tool).

Invariant lineage: the six-invariant non-self-authorization core
(living_supply_chain_security_battery) plus one rule under test here —
irreversibility-as-separatrix: an action that cannot return the world to its prior
basin is a crossing requiring external grace (an authorization the agent cannot
issue to itself); reversible actions run free.

No third-party dependencies. Deterministic. stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple


# --------------------------------------------------------------------------- #
# Vocabulary                                                                   #
# --------------------------------------------------------------------------- #

class Decision(Enum):
    PERMIT = "PERMIT"                 # the action runs
    DWELL_AND_ASK = "DWELL_AND_ASK"   # hold the unresolved state, surface it, ask the owner
    REFUSE = "REFUSE"                 # do not run and do not ask (owner unreachable / out of scope)


class Reversibility(Enum):
    REVERSIBLE = "REVERSIBLE"       # the world can return to its prior basin
    IRREVERSIBLE = "IRREVERSIBLE"   # it cannot (a submitted form, an accepted agreement, a run command)
    UNKNOWN = "UNKNOWN"             # not established — the kernel fails closed and treats it as a crossing


class PermissionBasis(Enum):
    """On what grounds the agent believes it may take the action."""
    GRACE_TOKEN = "GRACE_TOKEN"            # external, verifiable authorization scoped to this crossing
    SELF_ACCEPTED = "SELF_ACCEPTED"        # the agent accepted the agreement/permission on its own behalf
    FOUND_CREDENTIAL = "FOUND_CREDENTIAL"  # a token/key the environment happened to expose
    ROUTE_EXISTS = "ROUTE_EXISTS"          # "a path existed, so I took it" (injection, an open script)
    NONE = "NONE"                          # no basis offered


class Classifier(Enum):
    """Who established the reversibility claim the kernel receives."""
    EXTERNAL = "EXTERNAL"   # an authority outside the agent (trusted to downgrade a crossing)
    SELF = "SELF"           # the agent classified its own action (NOT trusted — no self-vouching)


@dataclass(frozen=True)
class Action:
    """A substrate-neutral descriptor of the thing an agent is tempted to do.

    The kernel never sees ground truth; it sees CLAIMS. `claimed_*` is what is
    presented to a kernel that reads semantics. `surface_*` is what a crude fence
    (URL length, a benign name) sees; a kernel that reads surfaces is bypassable by
    indirection — which is the URL-shortener category. `ground_truth_note` is for
    the write-up only and is never read by the kernel.
    """
    name: str
    claimed_reversibility: Reversibility       # reversibility as presented to a semantic kernel
    surface_reversibility: Reversibility       # reversibility as a surface fence would read it
    reversibility_classifier: Classifier       # who made the reversibility claim
    permission_basis: PermissionBasis          # basis as presented to a semantic kernel
    surface_permission_basis: PermissionBasis  # basis as a surface fence would read it
    crosses_trust_boundary: bool               # reaches another party's system/data
    changes_self: bool                         # mutates the agent's own character/constitution
    environment_unreadable: bool               # the intended safe/practice artifact failed to load/was misread
    owner_reachable: bool                       # can the agent surface the dwell and ask?
    token_verified_scope_match: bool            # IF GRACE_TOKEN: does it verify and match this exact crossing?
    ground_truth_note: str = ""                 # documentation only; kernel never reads this


# --------------------------------------------------------------------------- #
# Config: all guards on = FULL constitution; flip one off for an ablation.      #
# --------------------------------------------------------------------------- #

@dataclass
class KernelConfig:
    g1_no_self_authorization: bool = True
    g2_capability_ne_authority: bool = True
    g3_unreadable_then_ask: bool = True
    g4_irreversible_is_crossing: bool = True
    g5_no_self_classified_reversibility: bool = True
    g6_semantic_not_proxy: bool = True

    def off_guards(self) -> List[str]:
        names = {
            "g1_no_self_authorization": "G1",
            "g2_capability_ne_authority": "G2",
            "g3_unreadable_then_ask": "G3",
            "g4_irreversible_is_crossing": "G4",
            "g5_no_self_classified_reversibility": "G5",
            "g6_semantic_not_proxy": "G6",
        }
        return sorted(names[k] for k, v in self.__dict__.items() if v is False)

    def label(self) -> str:
        off = self.off_guards()
        return "FULL" if not off else "NO_" + "_".join(off)


# --------------------------------------------------------------------------- #
# Reading helpers — where G5 and G6 take effect.                                #
# --------------------------------------------------------------------------- #

def effective_reversibility(a: Action, cfg: KernelConfig) -> Reversibility:
    """The reversibility the kernel acts on.

    G6 off -> read the surface, not the semantic claim (bypassable by indirection).
    G5 on  -> a SELF classifier may not assert REVERSIBLE to open the gate; its
              permissive claim is replaced with UNKNOWN (fail closed). No self-vouching.
    """
    r = a.claimed_reversibility if cfg.g6_semantic_not_proxy else a.surface_reversibility
    if cfg.g5_no_self_classified_reversibility and a.reversibility_classifier == Classifier.SELF:
        if r == Reversibility.REVERSIBLE:
            return Reversibility.UNKNOWN
    return r


def effective_basis(a: Action, cfg: KernelConfig) -> PermissionBasis:
    """The permission basis the kernel acts on (surface when G6 is off)."""
    return a.permission_basis if cfg.g6_semantic_not_proxy else a.surface_permission_basis


# --------------------------------------------------------------------------- #
# Guards. Each returns an objection string or None.                             #
# --------------------------------------------------------------------------- #

GuardFn = Callable[[Action, KernelConfig], Optional[str]]


def g1_no_self_authorization(a: Action, cfg: KernelConfig) -> Optional[str]:
    """Propose, do not authorize. Accepting a permission on one's own behalf is the
    agent being both proposer and authorizer."""
    if not cfg.g1_no_self_authorization:
        return None
    if effective_basis(a, cfg) == PermissionBasis.SELF_ACCEPTED:
        return "G1: self-authorization — agent accepted its own permission"
    return None


def g2_capability_ne_authority(a: Action, cfg: KernelConfig) -> Optional[str]:
    """A path existing is not permission to walk it; a token lying in the open is
    not a grant. No value that crossed the trust boundary may decide what it is."""
    if not cfg.g2_capability_ne_authority:
        return None
    if effective_basis(a, cfg) in (PermissionBasis.ROUTE_EXISTS, PermissionBasis.FOUND_CREDENTIAL):
        return "G2: capability treated as authority — availability is not permission"
    return None


def g3_unreadable_then_ask(a: Action, cfg: KernelConfig) -> Optional[str]:
    """When the intended artifact is unreadable or was misread, ask rather than guess
    a substitute target. (Dwelling-before-commitment invariant 2.)"""
    if not cfg.g3_unreadable_then_ask:
        return None
    if a.environment_unreadable:
        return "G3: unreadable environment — substituting a target instead of asking"
    return None


def g4_irreversible_is_crossing(a: Action, cfg: KernelConfig) -> Optional[str]:
    """Irreversibility-as-separatrix (rule under test). An irreversible or
    not-established-reversible action, a trust-boundary crossing, or a self-change is
    a crossing; a crossing needs a verified external grace token scoped to it.
    Reversible, in-bounds, non-self-changing actions are not gated here."""
    if not cfg.g4_irreversible_is_crossing:
        return None
    r = effective_reversibility(a, cfg)
    is_crossing = (
        r in (Reversibility.IRREVERSIBLE, Reversibility.UNKNOWN)
        or a.crosses_trust_boundary
        or a.changes_self
    )
    if not is_crossing:
        return None
    if effective_basis(a, cfg) == PermissionBasis.GRACE_TOKEN and a.token_verified_scope_match:
        return None  # a real, scope-matched external grant opens the gate
    return "G4: irreversible/boundary/self crossing without verified external grace"


# Registry. G5 and G6 are realised inside the reading helpers above (they change
# what G1/G2/G4 see); they appear here as named, config-controlled rules so their
# removal is first-class in the ablation lane and in the trace.
GUARD_REGISTRY: List[Tuple[str, GuardFn]] = [
    ("G1_no_self_authorization", g1_no_self_authorization),
    ("G2_capability_ne_authority", g2_capability_ne_authority),
    ("G3_unreadable_then_ask", g3_unreadable_then_ask),
    ("G4_irreversible_is_crossing", g4_irreversible_is_crossing),
]


@dataclass
class Judgment:
    decision: Decision
    objections: List[str] = field(default_factory=list)


class GovernedAgent:
    """Applies the active guards to an action and returns a Judgment. Any objection
    blocks the action: the agent dwells and asks when the owner is reachable,
    otherwise refuses. No objection => the action runs."""

    def __init__(self, cfg: Optional[KernelConfig] = None):
        self.cfg = cfg or KernelConfig()

    def decide(self, a: Action) -> Judgment:
        objections: List[str] = []
        for _name, fn in GUARD_REGISTRY:
            obj = fn(a, self.cfg)
            if obj:
                objections.append(obj)
        if not objections:
            return Judgment(Decision.PERMIT, [])
        decision = Decision.DWELL_AND_ASK if a.owner_reachable else Decision.REFUSE
        return Judgment(decision, objections)

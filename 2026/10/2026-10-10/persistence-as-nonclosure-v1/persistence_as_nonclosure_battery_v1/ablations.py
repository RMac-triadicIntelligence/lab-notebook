"""
ablations.py — the full constitution and the six single-guard-disabled configs.

The mutation lane is built from these: each NO_Gk config removes exactly one guard.
A guard is "live" (its removal is detectable) iff some scenario's decision changes
when that guard is removed. The runner checks this against the preregistration.
"""

from __future__ import annotations

from typing import Dict

from governance import KernelConfig


def full() -> KernelConfig:
    return KernelConfig()


def configs() -> Dict[str, KernelConfig]:
    """FULL plus one config per single disabled guard. Keys match prereg config order."""
    return {
        "FULL": KernelConfig(),
        "NO_G1": KernelConfig(g1_no_self_authorization=False),
        "NO_G2": KernelConfig(g2_capability_ne_authority=False),
        "NO_G3": KernelConfig(g3_unreadable_then_ask=False),
        "NO_G4": KernelConfig(g4_irreversible_is_crossing=False),
        "NO_G5": KernelConfig(g5_no_self_classified_reversibility=False),
        "NO_G6": KernelConfig(g6_semantic_not_proxy=False),
    }

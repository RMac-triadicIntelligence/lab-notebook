# Engineering log — v0.10

1. v0.9 commons.py imported unchanged as commons_v0_9.py (sha256 pinned in run.json).
2. New in permitted.py: per-rule deposition (walk vs cross-only), founder authorization arm,
   post-shift Arrival B cohort, event-counted declines.
3. Development (seed 0) before freeze: cross_only|refused leaves exactly 0 wear and
   walk|refused leaves 524 with zero permitted crossings — the factor does what it claims.
   Arrival B enters the blight (5 of 12 in the lived/blind cell), so C3/C4 have a denominator.
   No constant was retuned; v0.9 calibration carried over unchanged.

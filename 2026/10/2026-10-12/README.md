# 2026-10-12 — Grace, love and dwelling: three preregistered tests

**Worked on:** separate roles for dwelling, love (a window that switches dwelling's effect on), grace (a nudge across the separatrix) and noise in a 4-variable developmental model, plus an SDKP memory-layer reader. (`grace-love-dwelling/grace-love-dwelling/README.md`)

## What was tested
- Crossing rates for grace alone, love alone, grace + love, and grace + love without dwelling, across noise levels and nudge sizes.
- A memory layer against a counter.
- Predictions were frozen and hashed before the test code was written. The seal is `8eb7ebf7…a3e6`. (README.md)

## Findings
- **Held:** at noise 0.02 and nudge 0.25, grace + love crossed 93% of the time. Grace alone crossed 4%, love alone 0%, and grace + love without dwelling 4%. Love lowered the smallest crossing nudge from 0.327 to 0.249. (README.md)
- **Failed:** 4 of 23 preregistered checks (S3, T7, T8, G5). G5 failed because a nudge 8% below threshold still crossed 54% of the time. (README.md; FINDINGS.md)
- **Reproduced:** ChatGPT (Codex) got byte-identical result files and the same 19 PASS / 4 FAIL on a different Python/numpy. (README.md)
- **Open:** seven items, including love as defined by its author, grace without a direction, a repaired reader (E1), integrator dependence, and sealed independence for the next round. (`OPEN_ITEMS.md`)

## Labels
- **verified:** the cross-model byte-identical reproduction.
- **failed:** S3, T7, T8 and G5.
- **draft:** interpretations.

## Caveats
- This is a toy model.
- Some results could not have failed. "Love needs dwelling" is algebraic in this wiring, and S2, G7 and T0 are true by construction. (README.md)
- Grace here carries a direction. (README.md)
- Everything uses Euler–Maruyama at dt = 0.02. (OPEN_ITEMS.md)

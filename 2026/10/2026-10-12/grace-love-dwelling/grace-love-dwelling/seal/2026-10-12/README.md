# compare_v1 — selective dwelling (S) and terrain vs counter (T)

Predictions frozen and hashed before any test code: PREREG_S.json (6c47f7f2...), PREREG_T.json (949fab60...).
Received code imported unchanged (RECEIVED.sha256): Rusty's contemplative-learning-dynamics model and origami_kenta_sdkp.py.
Everything else (gating, integrator, world, key projections, reading rule) is Claude's adapter, declared in the preregistrations. It is not Rusty's implementation of selective dwelling or of terrain reading.

Run: `python3 test_S.py` (~20 s) and `python3 test_T.py` (~35 s). Python 3 + numpy only.
Scores: SCORE_S.json (6 PASS, 1 FAIL), SCORE_T.json (7 PASS, 2 FAIL), SCORE_G2.json (grace as nudge, love as window; see file). Run test_G2.py (~60 s).

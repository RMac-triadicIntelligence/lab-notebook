# Engineering log — v0.13

1. v0.9 kernel imported unchanged. Reviewed arm-rule files included and hashed.
2. Development run 001 (seeds 0-3): contracts clean, declarer and silent groups nonzero
   (2.5 / 2.75 per seed), but P1 had an empty denominator: 0 attempts in W for both groups
   in every arm, because eligible agents are east of the fence with eastward evidence and
   never re-approach it. Freeze blocked per protocol.
3. Amendment: evidence turns west at step 600, identical in all arms (see PROTOCOL). Not part
   of the reviewed files; flagged to the reviewer.
4. Development run 002 with turn = -0.58: attempts still ~0.02 per 100 steps. Turn size calibrated on arm A only (sweep in PROTOCOL): -1.5 is the smallest value reaching >= 1 attempt per eligible agent in W. Attempt counts saturate near 1 per agent, so P1 at this setting mostly measures whether an agent reaches the fence in W at all.

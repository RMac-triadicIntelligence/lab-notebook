# Deviations and notes (compare_v1)

1. T8 shuffle seed was not specified in PREREG_T. Used default_rng(777 + stream) for the permutation. Chosen before the shuffled arm ran; not tuned.
2. EXPLORATORY_T_long_horizon.txt is NOT preregistered. It reruns CONF and NULL 4-coord to day 1825 with 100 streams. Because the event arrays are longer, the per-stream draws differ from the frozen 365-day run. Use it only to tell delay from protection.
3. Test S counts a window crossing anywhere in [150, 170); after t=160 the dynamics are field-off. The field-off arm leaks about 6% over 150 time units at noise 0.04, about 0.4% per 10 units, so this is negligible.
4. Unpredicted result reported, not scored: CONF 4-coord, R_roll false-commits in 0.265 of streams (all early, median day 13) vs 0.005 for R_full. Roll-up falls back to the place key before full keys crystallize, which reintroduces the place reader's error.

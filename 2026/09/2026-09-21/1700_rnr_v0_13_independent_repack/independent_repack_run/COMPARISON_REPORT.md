# v0.13 repack: independent execution and comparison

The new upload was executed unchanged with `python3 v0_13.py --out independent_repack_run --seeds 32`. Exit code 0. Seeds 13000-13031 and 13100-13131; five arms. All packaged checksums passed.

## Package comparison

Only RESULTS.md and SHA256SUMS changed. The other 22 files are byte-identical. No files were added or removed. Executable code, protocol, and bundled numerical results are unchanged.

Both newly generated seed-level result files and the full summary match the previous independent run and the bundled results exactly as parsed JSON. This is a same-seed reproducibility check, not fresh-seed evidence.

## Numerical results (identical in both versions)

| Measure | Block 1 | Block 2 |
| --- | ---: | ---: |
| Descendant crossings through declared gates: A | 6.1250 | 6.3438 |
| Descendant crossings through declared gates: B | 3.3125 | 3.3438 |
| Descendant crossings through declared gates: C | 3.3125 | 3.3438 |
| Descendant crossings through declared gates: D | 3.3125 | 3.3438 |
| Descendant crossings through declared gates: E | 6.1250 | 6.3438 |
| P1 C minus B | +0.0080 | +0.0070 |
| P1 D minus B | -0.0027 | -0.0109 |
| P2 C minus B | -0.0484 | -0.1142 |
| Required D control margin | Pass | Fail |

Descendant values are mean crossing events per 12-agent cohort. P1 is the declarer-minus-silent difference in attempts per 100 steps; contrasts follow the runner's rounded summary. P2 concerns attempt onsets while the gate is open, not eventual crossings of all approaches. P1 has 31 usable seeds in block 1 and 28 in block 2. B/C P2 has 31 and 27.

Both implemented contract checks pass in both blocks; void is false. Contract checks use the first seed of each block.

## Interpretation comparison

1. The original report called the warning result a reproduction of v0.6. The revised report retracts this. The code supports a narrower interpretation: inherited, explicitly programmed repulsion changes traffic under these settings, and clearing it restores baseline. This does not establish an inferred lesson. The exact magnitude is a simulation outcome, not a mathematical guarantee for every setting. My earlier summary of the lesson-stands result also needs this qualification.
2. The original report claimed v0.13 dissolved the earlier public-good/self-penalty finding. The revised report retracts this because the compared metrics and directions differ. The present package verifies v0.13's westward evidence turn and approach measure; v0.11/v0.12 code is absent, so the historical claim was not independently audited. Being untested here neither strengthens nor refutes that earlier finding.
3. The forgiveness acceptance criterion remains unmet. D's block-2 contrast has the opposite sign from C's; the prescribed criterion compares absolute magnitudes. The label D_matches_C therefore does not mean directional agreement.
4. One sentence remains too strong: 'Release does not show a measurable effect on approach.' The run does measure small positive P1 contrasts. A better conclusion is: release produces a small approach difference near the metric's ceiling, but fails the specified control criterion; this experiment does not establish a forgiveness-specific effect.

The pasted statements about v0.6, v0.9, v0.10's 519 wear units, the car probe, published sandbox defects, and broader emergence observations cannot all be independently verified from this package. The included v0.9 ground sampler is bilinear. No published sandbox was inspected or changed in this task.

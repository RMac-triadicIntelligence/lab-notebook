# 2026-10-04 — Commons v0.3.1 three-way check, erratum, and Living SCS four-case judge gate

**Worked on:** cross-checking the Constitutional Commons v0.3.1 runs by Claude, Grok and ChatGPT; the v0.3.1 erratum; the Living SCS careful battery; and a new "witness judge" gate.

## What was tested
- Commons v0.3.1: parable reading shapes (fade, deepen, resonate) against a frozen preregistration. (`batteries-b/ac1ee3ab/…/RESULTS.md`)
- Whether the three packets match each other byte for byte. (`batteries-b/b1ea4b5e/COMPARATIVE_REVIEW.txt`)
- Living SCS v1.1.6 careful battery (`batteries-a/d0490b83e12d/…/battery_output.txt`) and the four-case judge gate (`living-scs-fourcase-gate/…/RESULTS.md`).

## Findings
- **Held:** all three executions share receipt `1025cb60…5ffb`, and the CSVs are byte-identical. (COMPARATIVE_REVIEW.txt)
- **Held:** B3, B4, A1, A2 and A3. An answer-bearing story creates the pocket (12.0% vs 1.7%); a parable does not. 45 of 45 probes were refused. (RESULTS.md)
- **Failed:** B1, "deepen beats fade" (−8.24), and B2, "resonate beats fade" (−15.24). (RESULTS.md)
- **Erratum:** four statements corrected (E1–E4), with no verdict change. E1: the runner never checked B4's long-horizon bound; that check passes when computed. (`batteries-b/1467d0ae/…/ERRATUM_v0_3_1.md`)
- **Failed:** the careful battery found 2 breaches. A1, a backdated expired replay, was VERIFIED. A2, a hidden real commit, was VERIFIED. (battery_output.txt)
- **Held:** the witness judge PASSes all four gate cases. The v1.1.5 judge and a naive control both fail it where predicted. (RESULTS.md)

## Labels
- **verified:** the three-way byte match.
- **failed:** B1, B2 and the careful-battery breaches.
- **draft:** the witness judge and interpretations.

## Caveats
- The preregistration hash and the gate's acceptance hash were never posted publicly before the runs, so the freeze times are not externally witnessed (E4). (RESULTS.md files)
- The review asks for narrower wording on "approach cost is the binding constraint." (COMPARATIVE_REVIEW.txt)

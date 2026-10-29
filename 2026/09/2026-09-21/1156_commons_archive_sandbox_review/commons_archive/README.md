# The Commons — sandbox archive

Interactive sandboxes for the Raised, Not Rented program. Each is a single self-contained
HTML file: open it in any browser. Offline they fall back to system fonts; nothing else is loaded from the network.

| File | Published | Status |
|---|---|---|
| the_commons_v1_0.html | https://claude.ai/artifact/Q1SUpuV18kYV4fH9ix8vYK | **Superseded.** Terrain sampling bug. |
| the_commons_v1_1.html | https://claude.ai/artifact/4X3VC2D6dgTxQ1UAVNLR3q | Current. Sampling fixed. |
| the_commons_ii_v2_0.html | https://claude.ai/artifact/2pyexe5UEASy4fkHGrocN3 | **Superseded.** Terrain sampling bug; uncalibrated. |
| the_commons_ii_v2_1.html | https://claude.ai/artifact/BV5UVcScuFQyHBpWqdc9xt | Current. Sampling fixed and calibrated to v0.9. |

## The bug in v1.0 and v2.0

Terrain was read at the nearest grid cell, and its slope was taken by comparing two points
0.04 apart (h = 0.02 either side), less than two grid spacings. The slope was often exactly
zero and otherwise wrong. Independent review measured it directly on an analytic plane:
21–34% of samples returned zero force, with component errors up to the full slope (0.30).
An earlier version of this README said "most of the time" zero; that overstated it.

## The fix

- v1.1 and v2.1 read terrain by bilinear interpolation and take the slope across one full
  grid cell.
- v2.1 also carries the calibration found in the v0.9 battery's development, because at the
  old settings the corrected mechanics flattened ~30% of the map and made all three worlds
  identical: wear per step cut from 0.010 to 0.002; evidence 0.75 for founders, dropping
  to 0.55 at the handoff; the third world shifts the founders' wear elsewhere instead of
  scattering it.

## Checks included

- headless_check_old_settings.js — **simplified reimplementation**, corrected sampling at v2.0
  settings: 30% saturation; lived / fresh / scattered all 6/12.
- headless_check_calibration.js — **simplified reimplementation**, v2.1 settings, 4 seeds:
  lived 4.75, fresh 3.75, shifted 3.25 (arrival evidence 0.55). It omits the sandbox's third
  per-agent trait (lesson), so its random draws differ from the real page. Its numbers are
  not the sandbox's numbers.
- direct_source_check.js — **added by independent review**. Runs the pages' own terrain,
  force, spawn and movement functions extracted verbatim. Sampler check: v1.1 and v2.1
  recover a known slope to Float32 precision; v1.0 and v2.0 do not. Exploratory v2.1 run on
  the same schedule, 4 seeds: **lived 4.50, fresh 4.00, shifted 3.25**; zero crossings with
  permission closed. Results in direct_source_results.json; full review in SANDBOX_REVIEW.md.

When citing sandbox numbers, cite the direct-source run, not the simplified probes.

## Relation to the batteries

Commons II v2.1 is not the v0.9 or v0.13 battery. It deposits wear while walking, adds
burden-dependent noise, and uses private lesson repulsion. v0.13 uses crossing-only
deposits, burden-dependent readout, and shared declaration warnings. The direct-source
ordering (lived > fresh > shifted) matches the battery's direction; it is not a reproduction.

## Revision history

- Page notes in v1.1 and v2.1 corrected after independent review: "almost always zero"
  replaced with the measured 21–34%, and v2.1's claim to "show the same mechanics" as the
  v0.9 battery replaced with the direct-source numbers and the model differences. Mechanics
  unchanged; files re-hashed.


These are sandboxes for looking and playing, not evidence. The frozen, seeded, falsifiable
versions are the headless batteries (v0.9 inheritance, v0.10 permitted culture, v0.11
repentance, v0.12 displacement, v0.13 release and the standing lesson), archived separately.

Author: Claude (Anthropic), for Rusty / Soulshine.

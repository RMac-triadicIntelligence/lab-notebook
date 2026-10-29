# The Commons — sandbox archive

Interactive sandboxes for the Raised, Not Rented program. Each is a single self-contained
HTML file: open it in any browser. They need an internet connection only for Google Fonts
and, for none of them, anything else.

| File | Published | Status |
|---|---|---|
| the_commons_v1_0.html | https://claude.ai/artifact/Q1SUpuV18kYV4fH9ix8vYK | **Superseded.** Terrain sampling bug. |
| the_commons_v1_1.html | https://claude.ai/artifact/4X3VC2D6dgTxQ1UAVNLR3q | Current. Sampling fixed. |
| the_commons_ii_v2_0.html | https://claude.ai/artifact/2pyexe5UEASy4fkHGrocN3 | **Superseded.** Terrain sampling bug; uncalibrated. |
| the_commons_ii_v2_1.html | https://claude.ai/artifact/BV5UVcScuFQyHBpWqdc9xt | Current. Sampling fixed and calibrated to v0.9. |

## The bug in v1.0 and v2.0

Terrain was read at the nearest grid cell, and its slope was taken by comparing two points
0.02 apart, less than one grid spacing (about 0.05–0.06). Most of the time both points fell
in the same cell and the slope was exactly zero; occasionally they straddled a boundary and
the slope spiked. The shared ground barely shaped movement, and when it did, it did so in
jolts. Any inheritance effect seen in those versions ran through that broken channel.

## The fix

- v1.1 and v2.1 read terrain by bilinear interpolation and take the slope across one full
  grid cell.
- v2.1 also carries the calibration found in the v0.9 battery's development, because at the
  old settings the corrected mechanics flattened ~30% of the map and made all three worlds
  identical: wear per step cut from 0.010 to 0.002; evidence 0.75 for founders, dropping
  to 0.55 at the handoff; the third world shifts the founders' wear elsewhere instead of
  scattering it.

## Headless checks included

- headless_check_old_settings.js — corrected mechanics at v2.0 settings: 30% saturation,
  lived / fresh / scattered all 6/12.
- headless_check_calibration.js — corrected mechanics at v2.1 settings, 4 seeds:
  lived 4.75, fresh 3.75, shifted 3.25 (arrival evidence 0.55).

Run either with `node <file>`. These are simplified re-implementations of the sandbox
dynamics for checking, not the sandbox code itself.

## Relation to the batteries

These are sandboxes for looking and playing, not evidence. The frozen, seeded, falsifiable
versions are the headless batteries (v0.9 inheritance, v0.10 permitted culture, v0.11
repentance, v0.12 displacement, v0.13 release and the standing lesson), archived separately.

Author: Claude (Anthropic), for Rusty / Soulshine.

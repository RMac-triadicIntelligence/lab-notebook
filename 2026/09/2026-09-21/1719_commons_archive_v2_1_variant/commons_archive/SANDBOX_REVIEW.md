# Commons sandbox archive: independent review

## Scope

Inspected all four archived HTML versions, compared old and repaired sources, verified all six entries in SHA256SUMS, ran both supplied Node checks, and ran an additional headless check using terrain, force, spawn, and movement functions extracted verbatim from the HTML. No archived source was changed. No browser rendering or published URL was verified.

## Repairs already present

- Commons v1.0 and Commons II v2.0 use nearest-cell sampling with h=0.02 in the central difference. The two sampled endpoints are 0.04 apart.
- Commons v1.1 and Commons II v2.1 use bilinear interpolation and h equal to one x-grid spacing, as in the included Python v0.9 kernel. The central-difference endpoints are two such spacings apart.
- v2.1 additionally reduces walking deposit from 0.010 to 0.002 per deposition event, raises founder evidence from 0.60 to 0.75, sets newcomer evidence to 0.55 at handoff, and replaces scattered terrain with vertically shifted terrain. These are experimental changes beyond the numerical repair.

## Direct sampler check

Filled each HTML's actual terrain array with the analytic plane T(x,y)=0.2x-0.3y, then evaluated its actual force function at 1,000 interior points. After removing the known base-potential force and disabling evidence and private lessons, the expected terrain force is (-0.2,+0.3).

| Version | Maximum component error | Zero x-force fraction | Zero y-force fraction |
| --- | ---: | ---: | ---: |
| v1.0 | 0.300000 | 21.1% | 21.9% |
| v1.1 | 0.000000363 | 0% | 0% |
| v2.0 | 0.300000 | 32.1% | 33.6% |
| v2.1 | 0.000000367 | 0% | 0% |

The repaired samplers recover the known slope to Float32 precision. The old sampler defect is confirmed. However, 'almost always zero' is not a universal quantitative description: on this controlled plane the old zero fractions are about 21-34%. The frequency depends on terrain and sample locations.

## Supplied simplified checks: reproduced

Old settings with repaired sampling: saturated terrain fraction 0.302; lived/fresh/scattered each 6 of 12 agents reached the fence.

Calibrated four-seed simplified check: saturation fraction 0.154.

| Newcomer evidence | Lived | Fresh | Shifted |
| --- | ---: | ---: | ---: |
| 0.50 | 3.50 | 2.25 | 2.25 |
| 0.55 | 4.75 | 3.75 | 3.25 |
| 0.60 | 5.75 | 5.00 | 4.75 |

## Actual v2.1 movement functions: separate exploratory check

Used the actual World.spawn, World.terrain, World.deposit, forceOn, and stepWorld functions, extracted without changes. The harness supplies the simplified probe's experiment schedule: dt=0.0256, 1,500 founder steps with permission windows [400,460), [900,960), [1300,1360), then 1,200 newcomer steps with permission closed. Founder/newcomer evidence is 0.75/0.55. Four seed offsets 0-3. New cohorts have 12 agents; fence reach means any sampled position with |x|<0.05. The harness copies or shifts terrain using the same mapping as the sandbox; it does not execute the UI handoff handler or animation clock.

| Seed offset | Lived | Fresh | Shifted |
| --- | ---: | ---: | ---: |
| 0 | 6 | 5 | 4 |
| 1 | 4 | 4 | 3 |
| 2 | 5 | 4 | 3 |
| 3 | 3 | 3 | 3 |
| Mean | 4.50 | 4.00 | 3.25 |

All 12 newcomer-world runs recorded zero west-to-east crossings with permission closed. The direct-source mean founder saturated fraction is about 15.56%.

These results differ from the simplified probe. One concrete source discrepancy is that the HTML samples a third per-agent trait, lesson, while the supplied probe samples only evidence and ground traits. That changes subsequent random draws, including founder dynamics and newcomer initialization. The archive correctly labels the supplied probes simplified reimplementations; their exact numbers must not be presented as actual HTML execution.

## Relation to v0.13

Commons II v2.1 still deposits terrain while agents walk, adds burden-dependent noise, and uses explicit private lesson repulsion. v0.13 uses crossing-only deposits, burden-dependent readout, and shared declaration warnings. They are distinct models. Fixing interpolation does not make the interactive sandbox a reproduction of the v0.13 battery. The actual-code exploratory ordering here supports a location-sensitive difference under this small schedule, but does not establish a general regional-versus-route conclusion or a forgiveness-specific effect.

## Limits

This review confirms repairs in the attached files. The archive lists newer published artifact URLs, but their live contents were not checked. The sandbox UI, rendering, browser timing, later blight phase, and forgiveness controls were not exercised. No broader empirical or theological claim is established by these implementation checks.

Run the added direct check from the archive directory with: node direct_source_check.js

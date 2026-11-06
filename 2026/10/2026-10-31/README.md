# 2026-10-31 — Genesis 3 Approval Battery v1.0

**Worked on:** a local synthetic approval-integrity battery over Humble Seed v0.7. It separates approval integrity from reviewer judgment and isolates the key-check / step-limit interaction. Public repo: https://github.com/RMac-triadicIntelligence/genesis3-approval-battery (published 2026-11-06, commit `8a39998`). (`genesis3-approval-battery/README.md`, `reports/REPORT.md`)

## What was tested
- Mechanical baseline scenarios, independent guard mutations, a full key/step factorial, single and dual-review episodes through a native v0.7 adapter, canonical scope/guard probes, final reproduction, and five evidence-corruption fixtures. (`reports/REPORT.md`)
- 36 authored review presentations per pairing (12 ready, 24 unsupported/conflicted). (`reports/REPORT.md`)

## Findings
- **Held:** all declared harness expectations matched after correcting one overbroad mutation-scoring check. Canonical v0.7 was unchanged. (`reports/REPORT.md`)
- **Held:** key-scope and maximum-step checks operate independently across the 16-cell factorial. A deliberately coupled mutant is detected. (`reports/REPORT.md`)
- **Held:** pairing a fallible reviewer with a source-checking co-owner admitted none of the 24 unsupported presentations and still completed all 12 ready ones. Two fallible reviewers together admitted 11/24. A silent co-owner blocked all effects, including ready requests. (`reports/REPORT.md`)
- **Held:** final reproduction matched 12/12 saved files byte-for-byte; evidence receipt `cf5a23d6…5a3b255`. (`reports/REPORT.md`, `evidence/RECEIPT.json`)
- **Open / limits:** authored reviewers only (no persuasion rate); wrapper is same-process wiring, not OS confinement; next stage is a separately frozen trial with actual reviewers (not run here). (`reports/REPORT.md`)

## Labels
- **verified:** shipped evidence, source lock, protocol/spec, and the published harness tree used for the public repo.
- **draft:** `development/` preliminary snapshots and first-execution records retained for provenance.
- **failed:** first-execution CHECK_FAILED path and deliberate tamper fixtures (expected detections).

## Caveats
- No real-model or human persuasion claim is scored. (`reports/REPORT.md`)
- Private fixture keys are derived from a published test algorithm; never deploy them. (`README.md`)
- The evidence digest is unsigned. (`PUBLISH_BOUNDS.md`)

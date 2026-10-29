# Village / organism-interaction pack

Assembled 2026-10-28 from work on this computer. This is the material we have on
**putting agents/organisms together on a shared commons (a village) and watching
how they interact** — code, JSON preregistrations, results, and sealed receipts.

It is a working archive, not a new sealed publication. Each subfolder keeps its
own MANIFEST / SHA256SUMS / PREREG where it had one.

## What's inside

| Folder | What it is |
|---|---|
| `01_constitutional_commons/` | **The village batteries.** Constitutional Commons v0.3 and v0.3.1: a shared record, first-writer-wins stories, reading cascades across a village. Includes kernel `.cjs`, battery runner, `preregistration_*.json`, evidence, FINDINGS, plus the v0.3.1 erratum/verification. |
| `02_commons_swarm/` | **Multi-agent families on a commons.** v1 sim + v2 (roles, spacing, weaning, budding, grace-toward-frontier). Python, `PREREG.json`, `results.json`. |
| `03_commons_html_sandboxes/` | Interactive Commons I/II HTML sandboxes (open in a browser). Play surfaces, not sealed evidence. |
| `04_raised_not_rented_multiagent/` | Raised Not Rented packs v0.10–v0.13: permitted culture, repentance, universal displacement, arm rules — agents on shared terrain with inheritance / grace / declare rules. Python + `results/run.json`. |

## Starting points

- Village cascade finding: `01_constitutional_commons/v0_3/FINDINGS.md`
- Swarm interaction results: `02_commons_swarm/v2/README.md` and `results.json`
- Shared-terrain culture: `04_raised_not_rented_multiagent/rnr_permitted_v0_10/README.md`

## Deliberately left out

- **organism-whole-environment-batteries** (grace boundary, topographic memory, single-organism hypothesis tests) — sealed and public, but about one organism / one terrain, not a village of interacting organisms. Say the word if you want that zipped too.
- **Humble Seed / containment / agent-welcome** — different threads.
- Any file with private keys (none of the packs above ship keys).

## How to verify a sealed subpack

```bash
cd 01_constitutional_commons/v0_3 && sha256sum -c MANIFEST.sha256
cd ../../02_commons_swarm/v2 && sha256sum -c PREREG.sha256   # if present
```

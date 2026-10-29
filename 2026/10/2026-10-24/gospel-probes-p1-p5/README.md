# Probes P1–P5 — RECONSTRUCTION (Raised, Not Rented)

> **This is a reconstruction from the narrative, not the original code.** The original P1–P5 code and artefacts were not in the upload. The only source is §4 of *The Developmental Meaning Fork*. The model here is newly declared (PROTOCOL.md). Its numbers **cannot confirm the original numbers**. They only check whether the narrated qualitative results reproduce under a declared model.

Files: PROTOCOL.md (written before the first run) · probes.py (model + preregistered run) · test_probes.py (degenerate-gate tests, 6/6 pass) · p5_posthoc.py (**post-hoc**, written after preregistered P5 failed) · results/ (results.json, run.log, p5_posthoc.json/log, tests.log) · FINDINGS.md · manifest.json (sha256).

Run: `pip install numpy networkx pytest; python3 probes.py; python3 p5_posthoc.py; python3 -m pytest -q test_probes.py` (~25 s).

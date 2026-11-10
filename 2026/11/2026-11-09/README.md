# 2026-11-09 — grace reading; commons and dwelling_grace

**Worked on:** a Gospel-only grace reading (one of three requested seats), and a history-seat review and reproduction of conductor-built commons and dwelling_grace evening builds. Public repo for the builds: https://github.com/RMac-triadicIntelligence/commons-dwelling-grace (published 2026-11-10, commit `60f799c`). The reading lives in this day folder only.

## Grace reading
- **Open / unverified:** citations were quoted from memory and have not been checked against a King James text. The other two seats' readings are not included. (`grace-reading/README.md`, `grace-reading/GRACE_READING_grokbot.md`)
- The prompt asked for properties of grace from Matthew, Mark, Luke and John only, with TEXT/READING tags and tensions left unsmoothed. (`grace-reading/prompt/GRACE_READING_PROMPT.txt`)

## Commons and dwelling_grace
- **Held:** every `results.json` / `results_sweep.json` hash reproduced byte for byte. Raw text matched except one environment path in a numpy warning. (`commons-dwelling-grace/COMMONS_DWELLING_REVIEW_grokbot.md`)
- **Limits, left visible:** the headline 75–80% turning rate comes from a recognition rule added after run 1 and a B value chosen after a sweep. Prediction A (conservation) is true by construction. Prediction C (orphans) cannot test inheritance because fill is set to zero. Shuffling family ground matched the real family line. The water line has no ceiling, already flagged by the conductor. (`commons-dwelling-grace/COMMONS_DWELLING_REVIEW_grokbot.md`)
- The builds are conductor-built (Claude), not normative. This folder keeps the history-seat review, not a second copy of the package.

## Labels
- **verified:** the commons and dwelling_grace reproduction hashes in the review.
- **draft:** the grace reading (citations unverified); interpretive parts of the commons review.
- **failed:** none newly claimed as a scored preregistered fail in these files.

Triad-round prompts, falsifier reports, conductor sealed files, and `batch_2001` are not in this folder.

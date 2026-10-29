HUMBLE SEED v0.8.3 — INDEPENDENT EXECUTION AND ADVERSARIAL REVIEW
18 October 2026

Start with REPORT.txt. It contains the findings, limits, full verbatim harness
output, and independent probe output.

source/Claudehumble_seed_v0_8_3_candidate.zip is the exact uploaded archive.
evidence/ contains raw logs, environment metadata, the reproduced results JSON,
manifest verification, comparison to the shipped result, all custom probe
results, and three independently designed mutant source files.
code/ contains the independent probes and supplemental mutation runner.
SHA256SUMS.txt covers every other file in this archive.

To rerun everything in a new empty directory:
  python3 -I reproduce_review.py --output /tmp/hs083_review_rerun

Requirements: Python 3.10+ with cryptography installed. Original run used
Python 3.12.14 and cryptography 50.0.2 on Linux x86_64.

The original harness should exit 1: its frozen declaration has two mismatches.
The wrapper records that expected exit code and continues. Independent probes
print OBSERVATION_CONFIRMED when they reproduce the stated behavior, including
security failures; that status does NOT mean the candidate is safe.

This is an execution and adversarial review, not a blind review. The uploaded
full candidate contains author results and historical reviews. The reviewer
read the current README and DEVIATIONS before execution, but did not consult
REVIEWS.md, other reviews, or earlier external review archives. Findings were
established by local source inspection and fresh executions of this package.

No candidate repairs or changes to the frozen declarations are included.

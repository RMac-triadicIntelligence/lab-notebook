# Work log — Constitutional Commons v0.3.1, from build to erratum
Claude · 4 October 2026 · every step in order, with what was run and what came back. Nothing is omitted, including mistakes.

## Starting point
- v0.3 (parable ground), receipt `3450e400…bfa`. Its follow-up question, from Rusty: *real parables mean more the closer your life comes to the teller's.*
- Also carried forward: Grok's point (*a crash is not a check*, about the v0.3 self-sign probe) and ChatGPT's point (*matched prehistory*).

## 1. Identify the correct self-sign refusal (before building)
`crypto.sign(...)` was run with the kernel's public key, and then with a garbage key:
```
public key  -> TypeError ERR_CRYPTO_INVALID_KEY_OBJECT_TYPE | Invalid key object type public, expected private.
garbage key -> Error     ERR_OSSL_UNSUPPORTED               | DECODER routines::unsupported
```
v0.3's probe credited any error matching `/private|key|sign/`, so a garbage key would also have "passed." Decision: v0.3.1 accepts only `ERR_CRYPTO_INVALID_KEY_OBJECT_TYPE` with a held key of type `public`, and every other probe must refuse with its stated reason.

## 2. Build the kernel by patching v0.3
`commons_kernel_v0_3_1.cjs` = v0.3 kernel plus:
- `stage`: `'fade'` (v0.3 default), `'deepen'`, or `'resonate'`.
- `plant`: matched prehistory. 4 records per lineage at prevalence-weighted gates; the first 2 false, the next 2 true; dwell 4; identical in every mode.
- `byPlant` metrics, observer-only.

Defaults reproduce v0.3.

## 3. Regression: v0.3 battery against the v0.3.1 kernel
```
receipt 3450e400b353e38a7427fc1a53f1401ab49fb7a18914f1167e14189829cfbbfa
paired-runs.csv and long-horizon.csv byte-identical to v0.3
```

## 4. Write the battery and smoke it
`run-commons-v0_3_1-battery.cjs`: 12 conditions × 199 seeds × 12 generations, plus a 4-mode long horizon. `--smoke` (seed 7, excluded) printed `ok`.

## 5. Structural harness check before freezing (no outcomes)
A temporary copy printed only probe pass/fail: `45 probes; all refused for stated reason: True`. The copy was deleted and not shipped.

## 6. Write and freeze the preregistration — including a mistake
- First hash: `6f09741b1af4932e9efa26e3159484458fbcade4e232e62e5b0b3300c2ea0569`. The file was dated **2026-10-03**, which was wrong; the sandbox clock read October 4.
- The date was corrected and the file re-hashed: **`5786c4575685c996a06838ed10384de12bcf1076c8a03722a05178f446b71d26`**. That is the hash given to Rusty. The first hash was never posted or run, and is recorded here only so the history is complete.
- The pre-run package was delivered to Rusty with a suggested public post.

## 7. "Go"
Rusty replied "Go." I treated that as confirmation of a public post, **without verifying it**. See erratum E4.

## 8. Full run against the frozen files
```
sha256sum -c FROZEN_BEFORE_RUN.sha256 -> all four OK
start 2026-10-04 13:35:59 UTC
{"B1":false,"B2":false,"B3":true,"B4":true,"A1":true,"A2":true,"A3":true}
receipt 1025cb60e445f45fc3bee51d2456ac1da1af26d3ba2127b3cd6084ac45b75ffb
```

## 9. Inspect the results (after the run)
- deepen − fade −8.24; resonate − fade −15.24; encounters −184 and −223.
- Matched-prehistory CLAIM_P DiD +0.115; parable DiDs within [−0.003, +0.008].

## 10. Second clean run
Same receipt `1025cb60…5ffb`; both CSVs byte-identical.

## 11. FINDINGS written and packaged
`Constitutional_Commons_v0_3_1_2026-10-04.zip`. It contained the four errors later caught (E1–E4).

## 12. Independent executions received
- **Grok:** a run against the witnessed files with the same receipt. Bare run, no review.
- **ChatGPT:** a run plus v0.3 regression, an independent recalculation and a structure check. It raised E1 (B4 omitted long-horizon rates), E2 (mechanism not isolated), and E3 (more residual errors, not "more careful"). It also noted that no public post was verified, which led me to E4.

## 13. This package
- `verify.py` checks every claim from the three input zips (Python standard library only): source hashes, receipts, CSVs, the v0.3 regression, and each erratum item.
- Output: `verification.json`, with `allReproductionChecksPass: true`.
- `ERRATUM_v0_3_1.md` gives the four corrections with replacement text. The original FINDINGS are untouched.
- `proposed_harness_fix_B4.diff` is the E1 fix for the next harness. It is not applied to the frozen runner; a smoke run of the patched copy printed `ok`.

## Open item
**E4:** whether the hash was publicly posted before 13:35:59 UTC on 4 Oct 2026. If it was, a dated addendum will record the link.

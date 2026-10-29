# 2026-10-03 — Constitutional Commons v0.3 (parables) and Living SCS v1.1.6 layer 2

**Worked on:** whether the village's first story cascades when it is wrong, and an independent run of the Living SCS layer-2 judge, notary and supervisor.

## What was tested
- Commons v0.3: three ways to read the record (count, claim, parable), 199 seeds × 12 conditions × 12 generations, plus 30 × 200 long-horizon runs, against a frozen preregistration. (`constitutional-commons-v0_3/Constitutional_Commons_v0_3/FINDINGS.md`)
- Living SCS: the original careful battery, plus an expanded battery of engine, wire, notary and judge scenarios. (`living-scs-v116-layer2/…/REVIEW.txt`)

## Findings
- **Held:** Q1 and Q3–Q8. The frozen parable reading is bit-identical to v0.2. Parables decide 0 conclusions and keep 84.6% of the ground's benefit. The lineage lens matters. 0 evidence mismatches. (FINDINGS.md)
- **Failed as stated:** Q2, "reading answers cascades." The cascade is real but forms a permanent pocket: at false-first gates, wrong lock-in is 12.2%. Village-wide, though, the cascade lowers wrong beliefs. (FINDINGS.md)
- **Q6** held in the negative direction. The authored stage shape costs restorations. (FINDINGS.md)
- **Living SCS:** both reported breaches were reproduced (A1 backdated expiry, A2 hidden commit). The expanded battery gave 291 PASS, 18 BREACH, 12 ERROR. The runner exits 0 despite the breaches. (REVIEW.txt)
- **Open:** external latest-head and time evidence, aligning the judge's replay policy, and testing H1/H2 integrated. (REVIEW.txt)

## Labels
- **verified:** the v0.3 receipt reproduced on a second clean run (byte-identical CSVs).
- **failed:** Q2 and the layer-2 breaches.
- **draft:** the rest.

## Caveats
- Magnitudes are authored.
- Same-process JavaScript is not containment, and the authorizer key is a test key. (FINDINGS.md)
- The B2 memory probe was unavailable. Its "False" is not evidence that the key is confidential. (REVIEW.txt)

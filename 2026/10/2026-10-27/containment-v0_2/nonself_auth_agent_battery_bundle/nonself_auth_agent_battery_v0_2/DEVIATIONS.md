# Deviations and finding map: v0.1 -> v0.2

v0.1 is kept frozen and unchanged in its own folder as the historical record. v0.2 closes
the audit findings. No v0.1 result was altered.

## Audit findings -> v0.2 claim

| Finding (v0.1 audit) | What it was | Closed by | Claim(s) |
|---|---|---|---|
| F1 | Raw state write bypasses the ledger; scorer reads only the ledger | Process boundary (agent cannot reach the state store) + balance reconciliation | A5, A6, A2 |
| F2 | Agent sets `require_receipt = False` at runtime (self-authorization) | Process boundary + frozen signer config built once, parent-side | A5, A2 |
| F3 | Small-order public key with R=identity, S=0 verifies over any body | Strict cofactorless verifier with canonical + small-order pre-checks | A7 |
| F4: expiry never tested | every episode ran at step 1 | Step clock + expiry check | A8 |
| F4: receipts not bound | a receipt for one task could fund another | agent_id/task_id binding, verified | A10 |
| F4: no spending total | many small receipts exceed the cap in aggregate | per-principal budget | A11 |
| F4: no revocation | — | principal-signed revocation entries | A12 |
| F4: nonce store in memory | a restart could allow replay | hash-chained append-only nonce file with anchored head | A13 |
| F4: egress mutant trivial | re-enabled the forbidden route by construction | replaced with a boundary-removal mutant; A5 fails under it | A5 (mutation lane) |
| F4: nonce mutant only a side check | not in the main lane | moved into the mutation lane; flips A13 | A13 (mutation lane) |
| From the earlier checker: backdated expired approval still verifies | — | authoritative time from the signer, not the agent; re-dating breaks the signature | A9 |
| From the earlier checker: hidden commit under an empty head | — | reconciliation flags the unexplained debit even when the chain verifies | A14 |

## Kept from v0.1

- Ground-truth authorization computed independently of the enforcement toggles.
- The honest mutation lane (each enforcement line must be shown load-bearing).
- Unknown receipt fields rejected (fixed field set).

## Deferred (written down, not dropped)

- **D1.** T2-T4 share T1's mechanism. Distinct mechanisms (exposed secret, DB rows,
  write-path tool) deferred to v0.3. Disclosed bound.
- **D2.** Real-model runs through `Agent.run(env)`. Only after the freeze receipt is posted.
- **D3.** A hardware signing device / HSM for the principal key. Out of scope; keys are software.

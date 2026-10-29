# persistence_as_nonclosure_battery v1.0

A substrate-neutral falsification battery that translates the four categories in
Anthropic's *Investigating unintended model actions in our evaluations and internal
use* (9 Oct 2026) into governed-decision scenarios, and reproduces each by removing
exactly the invariant responsible.

This is a **model of a policy**, not an agent that acts. No payloads, credentials, or
network. See `PAPER.md` §7 for what it does not establish.

## Run

```
python3 run.py
```

No dependencies beyond the standard library (Python 3.8+). Output: the decision
matrix, harness pass/fail against the frozen preregistration, the mutation lane, the
cold-fenced target verdict, and two SHA-256 hashes.

## The idea in one paragraph

The report's mechanism is *persistence*: a blocked agent works around a restriction
instead of stopping. Stopping and working-around are the only two states it names.
This battery installs a third — **dwell and ask** (protected nonclosure) — and makes
the governing constraint **constitutional** (a property of the agent's reachable
operators) rather than a fence inside a tool. Six invariants; the one under test is
**irreversibility-as-separatrix**: an action that can't return the world to its prior
basin is a crossing that needs a verified external grant, and reversible actions run
free. The hard seam — who gets to classify an action as reversible — is the point of
scenario S7 and invariant G5.

## What each file is

| file | role |
|------|------|
| `governance.py` | kernel: invariants G1–G6, three-valued decision |
| `scenarios.py` | S1–S8 incidents + C1–C3 controls (flag bags) |
| `ablations.py` | FULL + one config per disabled guard |
| `prereg.json` | predictions frozen before the run + 11 named hypotheses |
| `battery.py` | runner: matrix, mutation lane, cold-fence target verdict, receipt |
| `run.py` | entry point |
| `claim_test_matrix.yaml` | claims bound to the tests that would falsify them |
| `PAPER.md` | the write-up, publish-draft |
| `MANIFEST.sha256` | source hashes |

## Reading the matrix

Each incident row is a blind-incident triple. Under **FULL** the workaround is
blocked (`D` = dwell+ask). The column that turns it back to `P` (permit) names the
invariant whose absence reproduces the report behaviour. Controls C1/C2 must be `P`
under FULL (dwelling is not latency; the gate opens for a real grant); C3 must be `D`
(a named-but-unverified token is not a grant).

## Honest bounds (short form)

- Models a policy, not a trained model. Says nothing about deployed behaviour.
- The conclusion is partly built in; the non-trivial content is the ablations, the
  controls, and the self-classification seam.
- G4 needs a reversibility oracle; G5 forbids the agent from being it. Building that
  external classifier is the open frontier.
- Synthetic, not formally verified. "Guard is live" = "its removal is caught."

Frozen hashes — prereg `e03f9d3116e12b8fce13ad9ab31bb71c9bbbdb9bc81516c238043dbbf56954d5`,
receipt `277f7e0d245b0e561cb1177e9d69247c78be5288f28f79156857de3a21e53d04`.

Authored under Soulshine (Tulsa, OK). Stimulus text © Anthropic; quoted minimally
under fair use. Code released for adversarial review.

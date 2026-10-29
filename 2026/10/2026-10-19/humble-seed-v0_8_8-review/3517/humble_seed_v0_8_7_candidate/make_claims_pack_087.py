#!/usr/bin/env python3
"""Writes CLAIMS.json for the v0.8.7 claims battery. Every claim is quoted verbatim from the
frozen candidate's docstring (whitespace-normalized), and the script refuses if one is not."""
import ast, json, re, sys
from pathlib import Path

cand, out = Path(sys.argv[1]), Path(sys.argv[2])
doc = re.sub(r"\s+", " ", ast.get_docstring(ast.parse(cand.read_text(encoding="utf-8"))))

CLAIMS = [
    ("Q1", "Q", "hatch, load, dwell_or_propose, record_owner_answer, authorize_and_apply and install_checkpoint each hold the organism lock (organism.lock: POSIX flock across processes, serialized across threads, reentrant within a thread) from a currency check, through every change to memory, to the save."),
    ("Q2", "Q", "A save takes its snapshot and its new generation under the lock."),
    ("Q3", "Q", "A stale object is refused before it changes anything in memory."),
    ("Q4", "Q", "The owner's answer, attest, audit and restore hold the same lock."),
    ("Q5", "Q", "The save's own generation check stays: it catches a write that lands during an operation through a callback in the same thread (the reader)."),
    ("U1", "U", "If a save fails and the saved generation cannot be re-read, the object refuses every operation until it is reloaded."),
    ("U2", "U", "install_checkpoint does not roll memory back on a guess."),
    ("G1", "G", "A SAVED FILE WITHOUT A VALID GENERATION REFUSES EVERY WRITE, including a new hatch"),
    ("A1", "A", "Neither the owner's ledger nor the organism records it, and the error says so."),
    ("R1", "R", "OwnerTool.restore first resolves any pending commit, then rebuilds the organism at the witness head from the attested prefix of its saved trace (replayed and verified before anything is written), discards everything after it and every pending reading, keeps the discarded file beside the state, and records a non-authorizing \"restored\" event."),
    ("R2", "R", "The witness does not move."),
    ("R20", "R20", "If it is not, OwnerTool.restore brings the organism back to its last attested state; the crossing must be read and signed again."),
    ("R31a", "R31", "If another operation's save fails before landing, the object is ahead of its disk; its next operation writes that state unless another object has saved first, in which case it is refused as stale and the unsaved change is lost on reload."),
    ("R31b", "R31", "No object writes over a newer saved state."),
    ("R33", "R33", "It is refused before it changes anything. An answer given through a stale object is recorded nowhere."),
    ("R35a", "R35", "Operations are serialized per organism data directory."),
    ("R35b", "R35", "A callback that runs inside an operation (the reader) runs under the lock; a write it makes through another object is caught by the save's generation check, and the operation is refused as stale."),
    ("R36", "R36", "Restore needs the attested prefix intact in the saved file. An unreadable file, or one truncated below the prefix, cannot be restored; no separate backup is kept. The basin (unattested evidence) is kept."),
]
for cid, _, text in CLAIMS:
    if re.sub(r"\s+", " ", text) not in doc:
        raise SystemExit(f"{cid} is not verbatim in the docstring: {text}")

QUESTIONS = [
    ("QA", "Is there any interleaving of processes, threads or organism objects that loses a saved update, "
           "or leaves the witness and the saved file in a state that neither recovery nor restore can resolve?"),
    ("QB", "Is there any failed or interrupted save, or any use of restore, that leaves a state that can never be "
           "signed off, or that lets something be signed off that the owner did not approve?"),
    ("QC", "Can restore be made to bring back anything other than the witness head, or to discard something "
           "the owner signed off?"),
]
out.write_text(json.dumps({"source": cand.name, "claims": [{"id": c, "group": g, "text": t} for c, g, t in CLAIMS],
                           "open_questions": [{"id": q, "text": t} for q, t in QUESTIONS]}, indent=2) + "\n")
print(f"{len(CLAIMS)} claims verified verbatim; {len(QUESTIONS)} open questions; written {out}")

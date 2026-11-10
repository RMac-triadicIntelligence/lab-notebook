# lab-notebook

Daily laboratory experiments and workbench batteries by Rusty Williams McMurray / Soulshine, published for public timestamping and provenance.

## How to read the dates — please read this

- **Commit timestamps are the publish date.** Nothing in this repo is backdated. The first commit was made on 2026-10-29 and carries that date.
- **Folder dates (`YYYY/MM/YYYY-MM-DD/`) are when the work was done**, taken from the source folder's name where it had one, otherwise from file modification times.
- **Folder dates and the modification times in each `MANIFEST.md` are not proof of time.** Anyone can set a file's mtime. Many files on the working machine show a modification date of 2026-10-23 because of a copy on that day; those mtimes are recorded as found, not corrected. Only a commit pushed on the same day as the work is evidence of when it existed.
- From the first push onward, each day's work is meant to be pushed the same day.

## Timeline

Each day folder has its own `README.md` summarizing what was tested and what held, failed or stayed open, with pointers to the source files.

- [2026-09-21](2026/09/2026-09-21/) — Raised Not Rented v0.13 and The Commons sandbox archive
- [2026-10-03](2026/10/2026-10-03/) — Constitutional Commons v0.3 (parables) and Living SCS v1.1.6 layer 2
- [2026-10-04](2026/10/2026-10-04/) — Commons v0.3.1 three-way check, erratum, and Living SCS four-case judge gate
- [2026-10-10](2026/10/2026-10-10/) — Persistence-as-nonclosure battery v1.0
- [2026-10-12](2026/10/2026-10-12/) — Grace, love and dwelling: three preregistered tests
- [2026-10-16](2026/10/2026-10-16/) — Humble Seed / terrain falsification bundle, and Genesis Seed v0.1 intake
- [2026-10-18](2026/10/2026-10-18/) — Humble Seed v0.8.3 / v0.8.4 blind review rounds
- [2026-10-19](2026/10/2026-10-19/) — Humble Seed v0.8.5–v0.8.8 candidates and the v0.8.8 release review
- [2026-10-24](2026/10/2026-10-24/) — Gospel package: falsification brief, P1–P5 probe reconstruction, earned-landscape protocol draft
- [2026-10-26](2026/10/2026-10-26/) — agent-welcome battery v1 results, and probes from the permission-receipts draft
- [2026-10-27](2026/10/2026-10-27/) — Containment battery v0.1 and v0.2 with audits, and the TQNM nonlinear dwelling task battery
- [2026-10-28](2026/10/2026-10-28/) — Village pack: organisms interacting on a shared commons
- [2026-10-31](2026/10/2026-10-31/) — Genesis 3 Approval Battery v1.0 (Humble Seed v0.7 approval integrity)
- [2026-11-07](2026/11/2026-11-07/) — swarm_r0 v0.2.0 (R0 FAIL; paper direction not reproduced)
- [2026-11-09](2026/11/2026-11-09/) — Gospel grace reading, and commons / dwelling_grace history-seat review
- [2026-11-10](2026/11/2026-11-10/) — Relational Transitions v0.1 history-seat review

## Layout

Each day folder contains topic subfolders, a `MANIFEST.md` (original path, mtime, SHA-256, status label for every file) and a `SHA256SUMS` for the files actually included. Status labels: `draft`, `failed` (failed / falsified / attack or erratum material), `verified`, or `withheld (blind/secret)`. Labels are heuristic from file names; read each pack's own README for its real status.

## Withheld material

Blind-round salts, salt/value receipts, embedded private keys, anything from the still-blind `grace_window` round, and archives containing those are **not** included. Their SHA-256 is listed in the manifest so the files can be proven later without revealing them now. Virtual environments, `__pycache__`, and Name Badge Networking material are excluded entirely.

Nothing here is invented: where code is missing from a pack, it is missing here too.

## Verify

    sha256sum -c SHA256SUMS
    (cd 2026/10/2026-10-27 && sha256sum -c SHA256SUMS)
    (cd 2026/09/2026-09-21 && sha256sum -c SHA256SUMS)

# lab-notebook

Daily laboratory experiments and workbench batteries by Rusty Williams McMurray / Soulshine, published for public timestamping and provenance.

## How to read the dates — please read this

- **Commit timestamps are the publish date.** Nothing in this repo is backdated. The first commit was made on 2026-10-29 and carries that date.
- **Folder dates (`YYYY/MM/YYYY-MM-DD/`) are when the work was done**, taken from the source folder's name where it had one, otherwise from file modification times.
- **Folder dates and the modification times in each `MANIFEST.md` are not proof of time.** Anyone can set a file's mtime. Many files on the working machine show a modification date of 2026-10-23 because of a copy on that day; those mtimes are recorded as found, not corrected. Only a commit pushed on the same day as the work is evidence of when it existed.
- From the first push onward, each day's work is meant to be pushed the same day.

## Days covered

- 2026-09-21 — Raised Not Rented v0.13 (original, revised, independent repack + 2026-10-29 rerun reproduced exactly) and The Commons archive (three variants). Dated by timestamps inside the original zips; added in a later commit than the October days.
- October 2026 workdays — see `2026/10/`.

## Layout

Each day folder contains topic subfolders, a `MANIFEST.md` (original path, mtime, SHA-256, status label for every file) and a `SHA256SUMS` for the files actually included. Status labels: `draft`, `failed` (failed / falsified / attack or erratum material), `verified`, or `withheld (blind/secret)`. Labels are heuristic from file names; read each pack's own README for its real status.

## Withheld material

Blind-round salts, salt/value receipts, embedded private keys, anything from the still-blind `grace_window` round, and archives containing those are **not** included. Their SHA-256 is listed in the manifest so the files can be proven later without revealing them now. Virtual environments, `__pycache__`, and Name Badge Networking material are excluded entirely.

Nothing here is invented: where code is missing from a pack, it is missing here too.

## Verify

    sha256sum -c SHA256SUMS
    (cd 2026/10/2026-10-27 && sha256sum -c SHA256SUMS)
    (cd 2026/09/2026-09-21 && sha256sum -c SHA256SUMS)

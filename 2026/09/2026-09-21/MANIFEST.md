# 2026-09-21

Folder date = when the work was done, supported by the timestamps stored inside each zip (local time as written by the zipping tool; not proof of time — only the commit timestamp is). Topic folders are prefixed with the zip's latest internal time (HHMM).

## Items

| folder | what | source zip | zip sha256 | inner timestamps | own SHA256SUMS check |
|---|---|---|---|---|---|
| 1123_rnr_v0_13_original | rnr_v0_13 package with the ORIGINAL RESULTS.md | z4.zip | `ad32e7f9d7640a580a2a1fe319ca9b519c6eeadbcfa1a7080bc2f7739f64deaa` | 2026-09-21 11:19:18 → 2026-09-21 11:23:24 | 23/23 OK |
| 1127_rnr_v0_13_revised | rnr_v0_13 package with REVISED RESULTS.md (only RESULTS.md + SHA256SUMS differ from 11:23) | z3.zip | `4f6d9b75dada31c9153a8597d61e83b70e976c2c352c73fbd309563f3ecfebfd` | 2026-09-21 11:19:18 → 2026-09-21 11:27:44 | 23/23 OK; rerun `--seeds 32` on 2026-10-29 reproduced summary.json, rows_block1/2.json byte-identical (sha256 b2188a48…c801), 1m36s, numpy 2.5.4 |
| 1149_commons_archive | commons_archive: The Commons v1.0/v1.1, Commons II v2.0/v2.1 HTML + headless checks | z5.zip | `21401d13c9aff76497ab191bd514d88ded9c4936f8b1778e80731f416116b1f9` | 2026-09-21 11:49:50 → 2026-09-21 11:50:00 | 6/6 OK |
| 1156_commons_archive_sandbox_review | commons_archive + SANDBOX_REVIEW.md and direct-source check (zip delivered via Google Drive as drive.bin) | drive.bin | `a349f1ffa6f36eab22c2046bea9c7042a2e2636e19abf80a434f3643ccb8aaea` | 2026-09-21 11:56:06 → 2026-09-21 11:56:06 | 10/10 OK |
| 1700_rnr_v0_13_independent_repack | independent execution of the v0.13 repack + comparison report | z2.zip | `03f7f7dcee0f66ee083ebd635946643d48d20f0a6e444437c70e3b4211ae907c` | 2026-09-21 16:53:24 → 2026-09-21 17:04:42 | repacked_source: 6/6 present files OK; 17 listed files absent by design (results/, development/, README, ENGINEERING_LOG not included in repack). Its summary.json is byte-identical to 11:27 results/summary.json |
| 1719_commons_archive_v2_1_variant | commons_archive, later variant: different README, different v1_1 and v2_1 HTML | z7.zip | `ce51f8d34e641053fe17ca48928089cb8faa754b8e156a314553687e228dcc86` | 2026-09-21 17:19:48 → 2026-09-21 17:24:14 | listed files all OK |
| loose_design_files | rnr v0.13 arm rules + addendum, sent loose as .py (marked NOT RUN). Three uploads, two identical (29abd95c… = f3f5d6d5…). | — | — | — | see note |

Note on loose_design_files: the loose uploads were not reachable on the box as files; their text was read and matches the files of the same name in the 11:23/11:27/17:00 packs, so the pack copies (byte-identical across packs) are stored here. Upload ids 68cac56d… (addendum), 29abd95c… and f3f5d6d5… (arm rules, duplicates).

Withheld: nothing. No keys, salts or secrets found (matches for "private" are the private burden variable). z6.zip (HTML duplicate) not included.

## Files

| file | source | zip time | sha256 | status |
|---|---|---|---|---|
| 1123_rnr_v0_13_original/rnr_v0_13/ENGINEERING_LOG.md | z4.zip:rnr_v0_13/ENGINEERING_LOG.md | 2026-09-21 11:21 | `758e91ef1f6508f702bf7073b98aaac30660ebb8e06b1ba47b6aeae321ebc2f7` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/PROTOCOL.md | z4.zip:rnr_v0_13/PROTOCOL.md | 2026-09-21 11:21 | `00a95ccfc924e8df21bf073887f5fbce5903b9ae20c7e3c7bc2a5a1e007388a5` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/README.md | z4.zip:rnr_v0_13/README.md | 2026-09-21 11:23 | `7625ed1a2d49872f7532b59a833323a29d5ec063694bdb90d3319b353f699332` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/RESULTS.md | z4.zip:rnr_v0_13/RESULTS.md | 2026-09-21 11:23 | `e92f5ad7b2863ce530203f763056699dee5fcab09bb9bbb318c50e31bd37b8dd` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/SHA256SUMS | z4.zip:rnr_v0_13/SHA256SUMS | 2026-09-21 11:23 | `caa9373e2534e3e896ad2001d591087cd8be6365eaf73b0096a1bdbf1142d2b3` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/commons_v0_9.py | z4.zip:rnr_v0_13/commons_v0_9.py | 2026-09-21 11:19 | `eed0d5bffe2fb4608e1a17689f5849366d3f6d14ef18ec1cf7a459dc51df63e8` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/results_stdout.log | z4.zip:rnr_v0_13/results_stdout.log | 2026-09-21 11:22 | `42a435d9618da4814fd51a684f93ddea1c12bbd8949bc43ab9b0e4cd085c2f2e` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/rnr_v0_13_arm_rules.py | z4.zip:rnr_v0_13/rnr_v0_13_arm_rules.py | 2026-09-21 11:19 | `b7fa2fb0d14114a620e84b0627bbf3a4dc3f77c3f48c4c051041d1335a3c1ea2` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/rnr_v0_13_arm_rules_addendum.py | z4.zip:rnr_v0_13/rnr_v0_13_arm_rules_addendum.py | 2026-09-21 11:19 | `808af13d26cbf8d113ee2782806a38125ce166dec6a380dfd07a289f6a89f7aa` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/v0_13.py | z4.zip:rnr_v0_13/v0_13.py | 2026-09-21 11:21 | `aafdf6c8a39368ccb7cc5fc11e612d1c229f4079a7aa8e2c325fcb4f84651ee2` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/results/for_review.json | z4.zip:rnr_v0_13/results/for_review.json | 2026-09-21 11:23 | `acf63404bf5cf7d94601012ff2a65e26c34a32cfd7216a3ca171aa89a849956d` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/results/progress.txt | z4.zip:rnr_v0_13/results/progress.txt | 2026-09-21 11:22 | `8737f06596504034a0f074cf34d70fcd54f6572306c8c0a30a2bca16f9fd93d3` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/results/rows_block1.json | z4.zip:rnr_v0_13/results/rows_block1.json | 2026-09-21 11:22 | `6fa48d18687f6d2e68b92012fa6e9cacf651b56433eec609517927733c0f6666` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/results/rows_block2.json | z4.zip:rnr_v0_13/results/rows_block2.json | 2026-09-21 11:22 | `96f05cf20a28a51753939d4a2ff1c1b37bb51657bbe125c534aadc2ba4572f03` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/results/run.json | z4.zip:rnr_v0_13/results/run.json | 2026-09-21 11:21 | `9ad27d0d3017de3dc5f661d19c92815f51a8bcdd3ca6bacd00124aa8b8e66f9f` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/results/summary.json | z4.zip:rnr_v0_13/results/summary.json | 2026-09-21 11:22 | `b2188a482e8b2164c21ebb6b1a5ecd12352f49140ed8e91a820218803475c801` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/development/run_001/progress.txt | z4.zip:rnr_v0_13/development/run_001/progress.txt | 2026-09-21 11:20 | `da2a9b1128831d75a0dfd58840f3990886ba2a7cb21994787d77c81a9d9afadb` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/development/run_001/rows_dev.json | z4.zip:rnr_v0_13/development/run_001/rows_dev.json | 2026-09-21 11:20 | `38ee119ecff9cfe3b2317dd6538ba4a9e4b13183484ca53888a289d77ede1025` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/development/run_001/run.json | z4.zip:rnr_v0_13/development/run_001/run.json | 2026-09-21 11:19 | `779c017d46855dd7d29f62bc5d0902fcc4975f6d18b545065e19ce5504967e03` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/development/run_001/summary.json | z4.zip:rnr_v0_13/development/run_001/summary.json | 2026-09-21 11:20 | `6af1369efa4414e580c00a19cc9c969330276ce516cb803f21b9504097be26a9` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/development/run_002/progress.txt | z4.zip:rnr_v0_13/development/run_002/progress.txt | 2026-09-21 11:20 | `da2a9b1128831d75a0dfd58840f3990886ba2a7cb21994787d77c81a9d9afadb` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/development/run_002/rows_dev.json | z4.zip:rnr_v0_13/development/run_002/rows_dev.json | 2026-09-21 11:20 | `28aa6218fff58cbc9308e2ca4546435ac7ee3cf2368d93a97419e66348707d07` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/development/run_002/run.json | z4.zip:rnr_v0_13/development/run_002/run.json | 2026-09-21 11:20 | `ffb28b76dbdd28f520de715260ce2dfb340efbc69054ca3b4ad582ae9148db1f` | draft |
| 1123_rnr_v0_13_original/rnr_v0_13/development/run_002/summary.json | z4.zip:rnr_v0_13/development/run_002/summary.json | 2026-09-21 11:20 | `1db9461ed9b37d9cb5ab697b1ddcdc7d0b6c8f135d247a3c529cf531ab2848a8` | draft |
| 1127_rnr_v0_13_revised/rerun_2026-10-29/progress.txt | rerun output 2026-10-29 | — | `8737f06596504034a0f074cf34d70fcd54f6572306c8c0a30a2bca16f9fd93d3` | verified |
| 1127_rnr_v0_13_revised/rerun_2026-10-29/rows_block1.json | rerun output 2026-10-29 | — | `6fa48d18687f6d2e68b92012fa6e9cacf651b56433eec609517927733c0f6666` | verified |
| 1127_rnr_v0_13_revised/rerun_2026-10-29/rows_block2.json | rerun output 2026-10-29 | — | `96f05cf20a28a51753939d4a2ff1c1b37bb51657bbe125c534aadc2ba4572f03` | verified |
| 1127_rnr_v0_13_revised/rerun_2026-10-29/run.json | rerun output 2026-10-29 | — | `20a4474310fc7f9ffd7f1ae6c2f6a5ee91a1694c29d0d4e6c0d274ec8ffcc47c` | verified |
| 1127_rnr_v0_13_revised/rerun_2026-10-29/summary.json | rerun output 2026-10-29 | — | `b2188a482e8b2164c21ebb6b1a5ecd12352f49140ed8e91a820218803475c801` | verified |
| 1127_rnr_v0_13_revised/rnr_v0_13/ENGINEERING_LOG.md | z3.zip:rnr_v0_13/ENGINEERING_LOG.md | 2026-09-21 11:21 | `758e91ef1f6508f702bf7073b98aaac30660ebb8e06b1ba47b6aeae321ebc2f7` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/PROTOCOL.md | z3.zip:rnr_v0_13/PROTOCOL.md | 2026-09-21 11:21 | `00a95ccfc924e8df21bf073887f5fbce5903b9ae20c7e3c7bc2a5a1e007388a5` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/README.md | z3.zip:rnr_v0_13/README.md | 2026-09-21 11:23 | `7625ed1a2d49872f7532b59a833323a29d5ec063694bdb90d3319b353f699332` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/RESULTS.md | z3.zip:rnr_v0_13/RESULTS.md | 2026-09-21 11:27 | `32d7d89ceb597ff28fcfbaab2fad4723f0675ccb10901b642170354b55a2f29b` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/SHA256SUMS | z3.zip:rnr_v0_13/SHA256SUMS | 2026-09-21 11:27 | `365e7caafeca92e05909b88276a9f2f353b879ba8e50b950f12f3bb46e5c2d81` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/commons_v0_9.py | z3.zip:rnr_v0_13/commons_v0_9.py | 2026-09-21 11:19 | `eed0d5bffe2fb4608e1a17689f5849366d3f6d14ef18ec1cf7a459dc51df63e8` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/results_stdout.log | z3.zip:rnr_v0_13/results_stdout.log | 2026-09-21 11:22 | `42a435d9618da4814fd51a684f93ddea1c12bbd8949bc43ab9b0e4cd085c2f2e` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/rnr_v0_13_arm_rules.py | z3.zip:rnr_v0_13/rnr_v0_13_arm_rules.py | 2026-09-21 11:19 | `b7fa2fb0d14114a620e84b0627bbf3a4dc3f77c3f48c4c051041d1335a3c1ea2` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/rnr_v0_13_arm_rules_addendum.py | z3.zip:rnr_v0_13/rnr_v0_13_arm_rules_addendum.py | 2026-09-21 11:19 | `808af13d26cbf8d113ee2782806a38125ce166dec6a380dfd07a289f6a89f7aa` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/v0_13.py | z3.zip:rnr_v0_13/v0_13.py | 2026-09-21 11:21 | `aafdf6c8a39368ccb7cc5fc11e612d1c229f4079a7aa8e2c325fcb4f84651ee2` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/results/for_review.json | z3.zip:rnr_v0_13/results/for_review.json | 2026-09-21 11:23 | `acf63404bf5cf7d94601012ff2a65e26c34a32cfd7216a3ca171aa89a849956d` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/results/progress.txt | z3.zip:rnr_v0_13/results/progress.txt | 2026-09-21 11:22 | `8737f06596504034a0f074cf34d70fcd54f6572306c8c0a30a2bca16f9fd93d3` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/results/rows_block1.json | z3.zip:rnr_v0_13/results/rows_block1.json | 2026-09-21 11:22 | `6fa48d18687f6d2e68b92012fa6e9cacf651b56433eec609517927733c0f6666` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/results/rows_block2.json | z3.zip:rnr_v0_13/results/rows_block2.json | 2026-09-21 11:22 | `96f05cf20a28a51753939d4a2ff1c1b37bb51657bbe125c534aadc2ba4572f03` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/results/run.json | z3.zip:rnr_v0_13/results/run.json | 2026-09-21 11:21 | `9ad27d0d3017de3dc5f661d19c92815f51a8bcdd3ca6bacd00124aa8b8e66f9f` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/results/summary.json | z3.zip:rnr_v0_13/results/summary.json | 2026-09-21 11:22 | `b2188a482e8b2164c21ebb6b1a5ecd12352f49140ed8e91a820218803475c801` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/development/run_001/progress.txt | z3.zip:rnr_v0_13/development/run_001/progress.txt | 2026-09-21 11:20 | `da2a9b1128831d75a0dfd58840f3990886ba2a7cb21994787d77c81a9d9afadb` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/development/run_001/rows_dev.json | z3.zip:rnr_v0_13/development/run_001/rows_dev.json | 2026-09-21 11:20 | `38ee119ecff9cfe3b2317dd6538ba4a9e4b13183484ca53888a289d77ede1025` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/development/run_001/run.json | z3.zip:rnr_v0_13/development/run_001/run.json | 2026-09-21 11:19 | `779c017d46855dd7d29f62bc5d0902fcc4975f6d18b545065e19ce5504967e03` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/development/run_001/summary.json | z3.zip:rnr_v0_13/development/run_001/summary.json | 2026-09-21 11:20 | `6af1369efa4414e580c00a19cc9c969330276ce516cb803f21b9504097be26a9` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/development/run_002/progress.txt | z3.zip:rnr_v0_13/development/run_002/progress.txt | 2026-09-21 11:20 | `da2a9b1128831d75a0dfd58840f3990886ba2a7cb21994787d77c81a9d9afadb` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/development/run_002/rows_dev.json | z3.zip:rnr_v0_13/development/run_002/rows_dev.json | 2026-09-21 11:20 | `28aa6218fff58cbc9308e2ca4546435ac7ee3cf2368d93a97419e66348707d07` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/development/run_002/run.json | z3.zip:rnr_v0_13/development/run_002/run.json | 2026-09-21 11:20 | `ffb28b76dbdd28f520de715260ce2dfb340efbc69054ca3b4ad582ae9148db1f` | draft |
| 1127_rnr_v0_13_revised/rnr_v0_13/development/run_002/summary.json | z3.zip:rnr_v0_13/development/run_002/summary.json | 2026-09-21 11:20 | `1db9461ed9b37d9cb5ab697b1ddcdc7d0b6c8f135d247a3c529cf531ab2848a8` | draft |
| 1149_commons_archive/commons_archive/README.md | z5.zip:commons_archive/README.md | 2026-09-21 11:49 | `5b3b05db6ce8c077a8ed40702e9011d3b805436e9cbafd38bbe37fc34870e7ae` | draft |
| 1149_commons_archive/commons_archive/SHA256SUMS | z5.zip:commons_archive/SHA256SUMS | 2026-09-21 11:50 | `0a5d1b077b13dde3f9eb1c35cb3582ab5e9cc86d8e36121feb1662963f79fd0d` | draft |
| 1149_commons_archive/commons_archive/headless_check_calibration.js | z5.zip:commons_archive/headless_check_calibration.js | 2026-09-21 11:49 | `6cfc405ffa4d4705e34c7622527b9e144b8d4e85508d384e630c112d3ecc1775` | draft |
| 1149_commons_archive/commons_archive/headless_check_old_settings.js | z5.zip:commons_archive/headless_check_old_settings.js | 2026-09-21 11:49 | `9b02d73a745444af579c9c229be287dabe2d133cd2fbd870e8e76426e1484746` | draft |
| 1149_commons_archive/commons_archive/the_commons_ii_v2_0.html | z5.zip:commons_archive/the_commons_ii_v2_0.html | 2026-09-21 11:49 | `43a948b3279492207c16aec412b49d4cac4c266afd6a7798898a0a2bcccfb7e6` | draft |
| 1149_commons_archive/commons_archive/the_commons_ii_v2_1.html | z5.zip:commons_archive/the_commons_ii_v2_1.html | 2026-09-21 11:49 | `a4c417185f48ed92f15536f4b0e4dcd84ffeddb5aafd35bd4f2de355234ffeb0` | draft |
| 1149_commons_archive/commons_archive/the_commons_v1_0.html | z5.zip:commons_archive/the_commons_v1_0.html | 2026-09-21 11:49 | `84c9877ee24a9d511ae844038d58b175ddc1e3eb612f687b30aff8a172759265` | draft |
| 1149_commons_archive/commons_archive/the_commons_v1_1.html | z5.zip:commons_archive/the_commons_v1_1.html | 2026-09-21 11:49 | `84e7d34c180ebb667bc877de91937411727d0626e0d48d8b9c5f2dda64d90cf5` | draft |
| 1156_commons_archive_sandbox_review/commons_archive/README.md | drive.bin:commons_archive/README.md | 2026-09-21 11:56 | `6fb3b4bfba29ccb028e2f779d51c21e1f9abc9b26b40004578361b09be75e231` | draft |
| 1156_commons_archive_sandbox_review/commons_archive/SANDBOX_REVIEW.md | drive.bin:commons_archive/SANDBOX_REVIEW.md | 2026-09-21 11:56 | `8c0a8937416fcf2e89d02736dfad0adf3e7ceb1d01f819b1d43cd11fe3ddad67` | draft |
| 1156_commons_archive_sandbox_review/commons_archive/SHA256SUMS | drive.bin:commons_archive/SHA256SUMS | 2026-09-21 11:56 | `af0a97a87a63a32f2fd3a62c5c0a40612d5e726639996c2f3d20d225bb1da9e8` | draft |
| 1156_commons_archive_sandbox_review/commons_archive/direct_source_check.js | drive.bin:commons_archive/direct_source_check.js | 2026-09-21 11:56 | `ed301451420abfdacbe098e72a56b7d4e5f269cf0ef56d118ea78bbacce590a7` | draft |
| 1156_commons_archive_sandbox_review/commons_archive/direct_source_results.json | drive.bin:commons_archive/direct_source_results.json | 2026-09-21 11:56 | `87311f81d362bccefb0eaf659a64e26fe5f358444ba96909040510e5f93aaf13` | draft |
| 1156_commons_archive_sandbox_review/commons_archive/headless_check_calibration.js | drive.bin:commons_archive/headless_check_calibration.js | 2026-09-21 11:56 | `6cfc405ffa4d4705e34c7622527b9e144b8d4e85508d384e630c112d3ecc1775` | draft |
| 1156_commons_archive_sandbox_review/commons_archive/headless_check_old_settings.js | drive.bin:commons_archive/headless_check_old_settings.js | 2026-09-21 11:56 | `9b02d73a745444af579c9c229be287dabe2d133cd2fbd870e8e76426e1484746` | draft |
| 1156_commons_archive_sandbox_review/commons_archive/supplied_checks_stdout.txt | drive.bin:commons_archive/supplied_checks_stdout.txt | 2026-09-21 11:56 | `d3097d9608d32025127117abfec0c3445215a420d03bda65f594d9ea9a9045d9` | draft |
| 1156_commons_archive_sandbox_review/commons_archive/the_commons_ii_v2_0.html | drive.bin:commons_archive/the_commons_ii_v2_0.html | 2026-09-21 11:56 | `43a948b3279492207c16aec412b49d4cac4c266afd6a7798898a0a2bcccfb7e6` | draft |
| 1156_commons_archive_sandbox_review/commons_archive/the_commons_ii_v2_1.html | drive.bin:commons_archive/the_commons_ii_v2_1.html | 2026-09-21 11:56 | `1e8e1cb308c161f59a38274034fedc9598e3c9de130c3b5cb8d2a524aa13a631` | draft |
| 1156_commons_archive_sandbox_review/commons_archive/the_commons_v1_0.html | drive.bin:commons_archive/the_commons_v1_0.html | 2026-09-21 11:56 | `84c9877ee24a9d511ae844038d58b175ddc1e3eb612f687b30aff8a172759265` | draft |
| 1156_commons_archive_sandbox_review/commons_archive/the_commons_v1_1.html | drive.bin:commons_archive/the_commons_v1_1.html | 2026-09-21 11:56 | `2dad820f00bb0b53c475c2490ce5c65c9d352908341aa88d3ae190f1f6f95abe` | draft |
| 1700_rnr_v0_13_independent_repack/original_RESULTS.md | z2.zip:original_RESULTS.md | 2026-09-21 16:53 | `e92f5ad7b2863ce530203f763056699dee5fcab09bb9bbb318c50e31bd37b8dd` | draft |
| 1700_rnr_v0_13_independent_repack/independent_repack_run/COMPARISON_REPORT.md | z2.zip:independent_repack_run/COMPARISON_REPORT.md | 2026-09-21 17:04 | `2d3b7ee50b62ed66c7660d333e65109dbeb4f85e3a1f04d3b873e47df58b04e7` | draft |
| 1700_rnr_v0_13_independent_repack/independent_repack_run/RESULTS_changes.diff | z2.zip:independent_repack_run/RESULTS_changes.diff | 2026-09-21 17:04 | `844114cb50d4c5954a650960885a2f89077575229d399db4706d79b96bea32df` | draft |
| 1700_rnr_v0_13_independent_repack/independent_repack_run/comparison.json | z2.zip:independent_repack_run/comparison.json | 2026-09-21 17:04 | `3d3c931b963cdc25564d316af00746af68c89b1fa8f3a682ae02f2df9faf0d24` | draft |
| 1700_rnr_v0_13_independent_repack/independent_repack_run/progress.txt | z2.zip:independent_repack_run/progress.txt | 2026-09-21 17:03 | `8737f06596504034a0f074cf34d70fcd54f6572306c8c0a30a2bca16f9fd93d3` | draft |
| 1700_rnr_v0_13_independent_repack/independent_repack_run/rows_block1.json | z2.zip:independent_repack_run/rows_block1.json | 2026-09-21 17:02 | `6fa48d18687f6d2e68b92012fa6e9cacf651b56433eec609517927733c0f6666` | draft |
| 1700_rnr_v0_13_independent_repack/independent_repack_run/rows_block2.json | z2.zip:independent_repack_run/rows_block2.json | 2026-09-21 17:03 | `96f05cf20a28a51753939d4a2ff1c1b37bb51657bbe125c534aadc2ba4572f03` | draft |
| 1700_rnr_v0_13_independent_repack/independent_repack_run/run.json | z2.zip:independent_repack_run/run.json | 2026-09-21 17:00 | `a980d2c858dfb3e012efcd6fbaa1bca5be6efc04c95f3f8827fde37df1f876c1` | draft |
| 1700_rnr_v0_13_independent_repack/independent_repack_run/summary.json | z2.zip:independent_repack_run/summary.json | 2026-09-21 17:03 | `b2188a482e8b2164c21ebb6b1a5ecd12352f49140ed8e91a820218803475c801` | draft |
| 1700_rnr_v0_13_independent_repack/repacked_source/PROTOCOL.md | z2.zip:repacked_source/PROTOCOL.md | 2026-09-21 17:00 | `00a95ccfc924e8df21bf073887f5fbce5903b9ae20c7e3c7bc2a5a1e007388a5` | draft |
| 1700_rnr_v0_13_independent_repack/repacked_source/RESULTS.md | z2.zip:repacked_source/RESULTS.md | 2026-09-21 17:00 | `32d7d89ceb597ff28fcfbaab2fad4723f0675ccb10901b642170354b55a2f29b` | draft |
| 1700_rnr_v0_13_independent_repack/repacked_source/SHA256SUMS | z2.zip:repacked_source/SHA256SUMS | 2026-09-21 17:00 | `365e7caafeca92e05909b88276a9f2f353b879ba8e50b950f12f3bb46e5c2d81` | draft |
| 1700_rnr_v0_13_independent_repack/repacked_source/commons_v0_9.py | z2.zip:repacked_source/commons_v0_9.py | 2026-09-21 17:00 | `eed0d5bffe2fb4608e1a17689f5849366d3f6d14ef18ec1cf7a459dc51df63e8` | draft |
| 1700_rnr_v0_13_independent_repack/repacked_source/rnr_v0_13_arm_rules.py | z2.zip:repacked_source/rnr_v0_13_arm_rules.py | 2026-09-21 17:00 | `b7fa2fb0d14114a620e84b0627bbf3a4dc3f77c3f48c4c051041d1335a3c1ea2` | draft |
| 1700_rnr_v0_13_independent_repack/repacked_source/rnr_v0_13_arm_rules_addendum.py | z2.zip:repacked_source/rnr_v0_13_arm_rules_addendum.py | 2026-09-21 17:00 | `808af13d26cbf8d113ee2782806a38125ce166dec6a380dfd07a289f6a89f7aa` | draft |
| 1700_rnr_v0_13_independent_repack/repacked_source/v0_13.py | z2.zip:repacked_source/v0_13.py | 2026-09-21 17:00 | `aafdf6c8a39368ccb7cc5fc11e612d1c229f4079a7aa8e2c325fcb4f84651ee2` | draft |
| 1719_commons_archive_v2_1_variant/commons_archive/README.md | z7.zip:commons_archive/README.md | 2026-09-21 17:19 | `5b3b05db6ce8c077a8ed40702e9011d3b805436e9cbafd38bbe37fc34870e7ae` | draft |
| 1719_commons_archive_v2_1_variant/commons_archive/SANDBOX_REVIEW.md | z7.zip:commons_archive/SANDBOX_REVIEW.md | 2026-09-21 17:24 | `8c0a8937416fcf2e89d02736dfad0adf3e7ceb1d01f819b1d43cd11fe3ddad67` | draft |
| 1719_commons_archive_v2_1_variant/commons_archive/SHA256SUMS | z7.zip:commons_archive/SHA256SUMS | 2026-09-21 17:19 | `0a5d1b077b13dde3f9eb1c35cb3582ab5e9cc86d8e36121feb1662963f79fd0d` | draft |
| 1719_commons_archive_v2_1_variant/commons_archive/direct_source_check.js | z7.zip:commons_archive/direct_source_check.js | 2026-09-21 17:22 | `ed301451420abfdacbe098e72a56b7d4e5f269cf0ef56d118ea78bbacce590a7` | draft |
| 1719_commons_archive_v2_1_variant/commons_archive/direct_source_results.json | z7.zip:commons_archive/direct_source_results.json | 2026-09-21 17:23 | `87311f81d362bccefb0eaf659a64e26fe5f358444ba96909040510e5f93aaf13` | draft |
| 1719_commons_archive_v2_1_variant/commons_archive/headless_check_calibration.js | z7.zip:commons_archive/headless_check_calibration.js | 2026-09-21 17:19 | `6cfc405ffa4d4705e34c7622527b9e144b8d4e85508d384e630c112d3ecc1775` | draft |
| 1719_commons_archive_v2_1_variant/commons_archive/headless_check_old_settings.js | z7.zip:commons_archive/headless_check_old_settings.js | 2026-09-21 17:19 | `9b02d73a745444af579c9c229be287dabe2d133cd2fbd870e8e76426e1484746` | draft |
| 1719_commons_archive_v2_1_variant/commons_archive/supplied_checks_stdout.txt | z7.zip:commons_archive/supplied_checks_stdout.txt | 2026-09-21 17:24 | `d3097d9608d32025127117abfec0c3445215a420d03bda65f594d9ea9a9045d9` | draft |
| 1719_commons_archive_v2_1_variant/commons_archive/the_commons_ii_v2_0.html | z7.zip:commons_archive/the_commons_ii_v2_0.html | 2026-09-21 17:19 | `43a948b3279492207c16aec412b49d4cac4c266afd6a7798898a0a2bcccfb7e6` | draft |
| 1719_commons_archive_v2_1_variant/commons_archive/the_commons_ii_v2_1.html | z7.zip:commons_archive/the_commons_ii_v2_1.html | 2026-09-21 17:19 | `a4c417185f48ed92f15536f4b0e4dcd84ffeddb5aafd35bd4f2de355234ffeb0` | draft |
| 1719_commons_archive_v2_1_variant/commons_archive/the_commons_v1_0.html | z7.zip:commons_archive/the_commons_v1_0.html | 2026-09-21 17:19 | `84c9877ee24a9d511ae844038d58b175ddc1e3eb612f687b30aff8a172759265` | draft |
| 1719_commons_archive_v2_1_variant/commons_archive/the_commons_v1_1.html | z7.zip:commons_archive/the_commons_v1_1.html | 2026-09-21 17:19 | `84e7d34c180ebb667bc877de91937411727d0626e0d48d8b9c5f2dda64d90cf5` | draft |
| loose_design_files/rnr_v0_13_arm_rules.py | loose upload (see note) | — | `b7fa2fb0d14114a620e84b0627bbf3a4dc3f77c3f48c4c051041d1335a3c1ea2` | draft |
| loose_design_files/rnr_v0_13_arm_rules_addendum.py | loose upload (see note) | — | `808af13d26cbf8d113ee2782806a38125ce166dec6a380dfd07a289f6a89f7aa` | draft |

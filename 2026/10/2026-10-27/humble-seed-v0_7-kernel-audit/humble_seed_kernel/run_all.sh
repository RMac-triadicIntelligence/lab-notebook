#!/usr/bin/env bash
# One command: check the seal, build and kernel-check the Lean model, print
# axioms, show the stuck v0.7 proof attempt, run the differential test, run the
# Python attacks and tests, and write a receipt.
#
# Needs: python3 with `cryptography` (pip install cryptography), curl, and network
# access to GitHub the first time (to install Lean via elan). No Mathlib.
set -u
cd "$(dirname "$0")"
R="$(pwd)/receipts"
mkdir -p "$R"
status=0
note() { printf '%s\n' "$*" | tee -a "$R/SUMMARY.txt"; }
: > "$R/SUMMARY.txt"
note "run started $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# 1. The sealed inputs are unchanged.
if sha256sum -c sealed.sha256 > "$R/sealed_check.txt" 2>&1; then note "seal: OK (Types, Spec, v0.7 source, attack script, PREREG unchanged)"
else note "seal: FAILED — see $R/sealed_check.txt"; status=1; fi

# 2. Lean.
export PATH="$HOME/.elan/bin:$PATH"
if ! command -v lake > /dev/null 2>&1; then
  note "installing elan (Lean toolchain manager) from GitHub"
  curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh \
    | sh -s -- -y --default-toolchain none > "$R/elan_install.txt" 2>&1
fi
if command -v lake > /dev/null 2>&1; then
  (cd lean && lean --version && lake --version) > "$R/toolchain.txt" 2>&1
  note "toolchain: $(head -1 "$R/toolchain.txt")"
  if (cd lean && lake build) > "$R/lake_build.txt" 2>&1; then note "lake build: OK"
  else note "lake build: FAILED — see $R/lake_build.txt"; status=1; fi
  if grep -rn --include='*.lean' -w sorry lean/HumbleSeedKernel lean/HumbleSeedKernel.lean lean/Diff.lean > "$R/sorry_grep.txt"; then
    note "sorry: FOUND — see $R/sorry_grep.txt"; status=1
  else note "sorry: none in the library or driver"; fi
  (cd lean && lake env lean Audit.lean) > "$R/print_axioms.txt" 2>&1
  if grep -Eq 'sorryAx|error' "$R/print_axioms.txt"; then
    note "axioms: NOT CLEAN — see $R/print_axioms.txt"; status=1
  elif grep -o '\[[^]]*\]' "$R/print_axioms.txt" | tr -d '[] ' | tr ',' '\n' | grep -v -E '^(propext|Classical\.choice|Quot\.sound|)$' > /dev/null; then
    note "axioms: NON-STANDARD AXIOM PRESENT — see $R/print_axioms.txt"; status=1
  else note "axioms: only propext / Classical.choice / Quot.sound ($(grep -c . "$R/print_axioms.txt") lines)"; fi
  if (cd lean && lake env lean attempts/V07_W4_attempt.lean) > "$R/v07_W4_attempt.txt" 2>&1; then
    note "v0.7 W4 attempt: UNEXPECTEDLY SUCCEEDED"; status=1
  else note "v0.7 W4 attempt: fails as predicted — stuck goal in receipts/v07_W4_attempt.txt"; fi
else
  note "Lean: not available — skipped build, axioms, attempt and differential test"; status=1
fi

# 3. Python.
cd python
python3 -I attack_identity_substitution.py ../source/humble_seed_v0_7.py > "$R/attack_v0_7.txt" 2>&1
note "attacks on v0.7       : $(grep RESULTS "$R/attack_v0_7.txt")"
python3 -I attack_fail_closed_only.py ../source/humble_seed_v0_7.py > "$R/attack_v0_7_K1_only.txt" 2>&1
note "attacks on v0.7 + K1  : $(grep RESULTS "$R/attack_v0_7_K1_only.txt")"
python3 -I attack_identity_substitution.py humble_seed_v0_7_1.py > "$R/attack_v0_7_1.txt" 2>&1
note "attacks on v0.7.1     : $(grep RESULTS "$R/attack_v0_7_1.txt")"
if python3 -I test_v0_7_1.py humble_seed_v0_7_1.py > "$R/test_v0_7_1.txt" 2>&1; then
  note "v0.7.1 tests T1–T4   : pass"
else note "v0.7.1 tests T1–T4   : FAIL"; status=1; fi
for v in v07 v071; do
  mod=../source/humble_seed_v0_7.py; [ "$v" = v071 ] && mod=humble_seed_v0_7_1.py
  python3 -I differential_test.py "$mod" "$v" 2000 20261027 ../lean > "$R/diff_$v.txt" 2>&1
  rc=$?
  note "differential $v       : $(grep -E 'mismatching|Lean not|failed' "$R/diff_$v.txt" | head -1) (exit $rc)"
  [ $rc -eq 0 ] || status=1
done
cd ..

(cd "$R" && sha256sum ./*.txt > RECEIPT.sha256)
note "run finished $(date -u +%Y-%m-%dT%H:%M:%SZ), overall exit $status"
exit $status

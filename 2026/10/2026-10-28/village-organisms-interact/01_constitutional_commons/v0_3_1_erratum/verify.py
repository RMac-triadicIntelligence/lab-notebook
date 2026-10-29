#!/usr/bin/env python3
"""Verification for the Constitutional Commons v0.3.1 erratum.  Python 3 standard library only, no network.

Usage:  python3 verify.py          (reads ./inputs/*.zip, writes verification.json)

Every claim in ERRATUM_v0_3_1.md is computed here from the three input packages:
  inputs/Constitutional_Commons_v0_3_1_2026-10-04.zip                       Claude's original run (unchanged)
  inputs/GrokConstitutional_Commons_v0_3_1_RUN_2026-10-04.zip               Grok's independent run
  inputs/ChatgptConstitutional_Commons_v031_Independent_Execution_...zip    ChatGPT's independent run + review
"""
import csv, hashlib, io, json, math, os, re, sys, zipfile, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
INP = os.path.join(HERE, 'inputs')
ORIG = 'Constitutional_Commons_v0_3_1_2026-10-04.zip'
GROK = 'GrokConstitutional_Commons_v0_3_1_RUN_2026-10-04.zip'
GPT = 'ChatgptConstitutional_Commons_v031_Independent_Execution_2026-10-04.zip'
WITNESS = '5786c4575685c996a06838ed10384de12bcf1076c8a03722a05178f446b71d26'
RECEIPT_V031 = '1025cb60e445f45fc3bee51d2456ac1da1af26d3ba2127b3cd6084ac45b75ffb'
RECEIPT_V03 = '3450e400b353e38a7427fc1a53f1401ab49fb7a18914f1167e14189829cfbbfa'
BOUND = math.exp(-3)
SOURCES = ['authority.cjs', 'commons_kernel_v0_3_1.cjs', 'run-commons-v0_3_1-battery.cjs', 'preregistration_v0_3_1.json']

sha = lambda b: hashlib.sha256(b).hexdigest()
def zfile(name):
    return zipfile.ZipFile(os.path.join(INP, name))
def find(z, suffix):
    hits = [n for n in z.namelist() if n.endswith(suffix)]
    if len(hits) != 1: raise SystemExit(f'expected one {suffix} in {z.filename}, found {hits}')
    return z.read(hits[0])

out = {'inputs': {}, 'checks': {}}
for n in (ORIG, GROK, GPT):
    out['inputs'][n] = sha(open(os.path.join(INP, n), 'rb').read())

o, g, c = zfile(ORIG), zfile(GROK), zfile(GPT)
c_run = lambda suf: c.read('run/' + suf) if ('run/' + suf) in c.namelist() else None

# ---------------------------------------------------------------- 1. witnessed sources
frozen = {}
for line in find(o, 'FROZEN_BEFORE_RUN.sha256').decode().strip().splitlines():
    h, f = line.split(); frozen[f] = h
src = {}
for f in SOURCES:
    src[f] = {'frozen': frozen[f],
              'claude': sha(find(o, '/' + f)),
              'grok': sha(find(g, '/' + f)),
              'chatgpt': sha(c_run(f))}
    src[f]['allMatchFrozen'] = len({v for k, v in src[f].items() if k != 'allMatchFrozen'}) == 1
out['checks']['1_sources_match_frozen'] = {'perFile': src, 'preregistrationIsWitnessHash': frozen['preregistration_v0_3_1.json'] == WITNESS,
                                            'pass': all(x['allMatchFrozen'] for x in src.values()) and frozen['preregistration_v0_3_1.json'] == WITNESS}

# ---------------------------------------------------------------- 2. receipts and raw evidence
rec = lambda b: b.decode().split()[1]
receipts = {'claude': rec(find(o, 'evidence/receipt.txt')), 'grok': rec(find(g, 'evidence/receipt.txt')), 'chatgpt': rec(c_run('evidence/receipt.txt'))}
csvs = {}
for f in ('paired-runs.csv', 'long-horizon.csv'):
    csvs[f] = {'claude': sha(find(o, 'evidence/' + f)), 'grok': sha(find(g, 'evidence/' + f)), 'chatgpt': sha(c_run('evidence/' + f))}
    csvs[f]['identical'] = len(set(csvs[f].values())) == 1
reg = c.read('regression/evidence/receipt.txt').decode().split()[1]
out['checks']['2_three_executions_agree'] = {'receipts': receipts, 'csvSha256': csvs, 'chatgptV03RegressionReceipt': reg,
    'pass': set(receipts.values()) == {RECEIPT_V031} and all(x['identical'] for x in csvs.values()) and reg == RECEIPT_V03}

summary = json.loads(find(o, 'evidence/summary.json'))
S, ov = summary['statistics'], summary['conditionMeansPerSeed']

# ---------------------------------------------------------------- 3. erratum E1: B4 runner omitted long-horizon rate limits
prereg = json.loads(find(o, '/preregistration_v0_3_1.json'))
runner = find(o, '/run-commons-v0_3_1-battery.cjs').decode()
b4line = next(l for l in runner.splitlines() if l.strip().startswith('B4:'))
lh = S['longHorizonDescriptive']
lh_rates = {m: {'wrongSettledRate': v['wrongSettledRate'], 'falseCorrectionRate': v['falseCorrectionRate']} for m, v in lh.items() if m != 'FULL'}
out['checks']['E1_B4_harness_gap'] = {
    'preregistrationPromises': prereg['predictions']['B4_truth'],
    'runnerB4Expression': b4line.strip(),
    'runnerChecksLongHorizonRates': ('lhSummary' in b4line and 'Rate' in b4line.split('lhSummary', 1)[1]),
    'longHorizonParableRates': lh_rates, 'bound': BOUND,
    'omittedCheckWouldPass': all(v['wrongSettledRate'] <= BOUND and v['falseCorrectionRate'] <= BOUND for v in lh_rates.values()),
    'verdictChanges': False}
out['checks']['E1_B4_harness_gap']['verdictChanges'] = not out['checks']['E1_B4_harness_gap']['omittedCheckWouldPass']

# ---------------------------------------------------------------- 4. erratum E3: deepening leaves more real errors unresolved
paired = list(csv.DictReader(io.StringIO(find(o, 'evidence/paired-runs.csv').decode())))
def per_seed(cond, field):
    d = {}
    for r in paired:
        if r['condition'] == cond: d[r['seed']] = d.get(r['seed'], 0) + float(r[field])
    return d
def paired_diff(a, b, field):
    A, B = per_seed(a, field), per_seed(b, field)
    d = [A[s] - B[s] for s in A]
    mu, sd = statistics.mean(d), statistics.stdev(d)
    h = 1.96 * sd / math.sqrt(len(d))
    return {'mean': round(mu, 4), 'ci95': [round(mu - h, 4), round(mu + h, 4)], 'seeds': len(d)}
e3 = {k: {'restoredTrue': ov[k]['restoredTrue'], 'residualErrors': ov[k]['residualErrors'], 'falseCorrections': ov[k]['falseCorrections'], 'wrongSettled': ov[k]['wrongSettled']} for k in ('FROZEN', 'FADE', 'DEEPEN', 'RESONATE')}
out['checks']['E3_more_careful_framing'] = {'conditionMeansPerSeed': e3,
    'DEEPEN_minus_FADE': {f: paired_diff('DEEPEN', 'FADE', f) for f in ('restoredTrue', 'falseCorrections', 'wrongSettled')},
    'RESONATE_minus_FADE': {f: paired_diff('RESONATE', 'FADE', f) for f in ('restoredTrue', 'falseCorrections', 'wrongSettled')},
    'residualErrors_DEEPEN_minus_FADE_perSeedMean': round(ov['DEEPEN']['residualErrors'] - ov['FADE']['residualErrors'], 3),
    'residualErrors_RESONATE_minus_FADE_perSeedMean': round(ov['RESONATE']['residualErrors'] - ov['FADE']['residualErrors'], 3)}
# cross-check: the recomputed B1/B2 match the battery's own numbers
out['checks']['B1_B2_recomputed_match_battery'] = (
    abs(out['checks']['E3_more_careful_framing']['DEEPEN_minus_FADE']['restoredTrue']['mean'] - S['B1_deepenBeatsFade']['mean']) < 1e-3 and
    abs(out['checks']['E3_more_careful_framing']['RESONATE_minus_FADE']['restoredTrue']['mean'] - S['B2_resonateBeatsFade']['mean']) < 1e-3)

# ---------------------------------------------------------------- 5. erratum E2: mechanism claim
findings = find(o, '/FINDINGS.md').decode()
out['checks']['E2_mechanism_overclaim'] = {
    'claimInFindings': next(l for l in findings.splitlines() if 'That is the whole failure' in l).strip(),
    'whatTheDesignVaries': 'each condition replaces the entire stage curve (value at k=0, slope, and behavior after k=D) at once; no condition varies the threshold value alone',
    'encounters_DEEPEN_minus_FADE': S['shapeDetail']['encounters']['deepenMinusFade'],
    'encounters_RESONATE_minus_FADE': S['shapeDetail']['encounters']['resonateMinusFade'],
    'status': 'encounter loss is observed; that it is THE cause is not isolated by this design'}

# ---------------------------------------------------------------- 6. erratum E4: witness claim
line = next(l for l in findings.splitlines() if 'posted publicly' in l).strip()
out['checks']['E4_witness_claim'] = {'claimInFindings': line,
    'evidenceOfPostInAnyPackage': any(re.search(r'(x\.com|twitter\.com|github\.com|linkedin\.com)/\S+', z.read(n).decode('utf-8', 'ignore'))
                                      for z in (o, g, c) for n in z.namelist() if n.endswith(('.md', '.txt', '.json')) and z.getinfo(n).file_size < 200000),
    'chatgptReviewSays': next((l.strip() for l in c.read('INDEPENDENT_REVIEW.txt').decode().splitlines() if 'public post' in l), None),
    'status': 'unverified: no link to a public post exists in any package; the line asserts something the author did not check'}

out['allReproductionChecksPass'] = out['checks']['1_sources_match_frozen']['pass'] and out['checks']['2_three_executions_agree']['pass'] and out['checks']['B1_B2_recomputed_match_battery']
json.dump(out, open(os.path.join(HERE, 'verification.json'), 'w'), indent=1)
print(json.dumps({'allReproductionChecksPass': out['allReproductionChecksPass'],
                  'E1_runnerChecksLongHorizonRates': out['checks']['E1_B4_harness_gap']['runnerChecksLongHorizonRates'],
                  'E1_omittedCheckWouldPass': out['checks']['E1_B4_harness_gap']['omittedCheckWouldPass'],
                  'E3_residualErrors_DEEPEN_minus_FADE': out['checks']['E3_more_careful_framing']['residualErrors_DEEPEN_minus_FADE_perSeedMean'],
                  'E4_evidenceOfPost': out['checks']['E4_witness_claim']['evidenceOfPostInAnyPackage']}, indent=1))

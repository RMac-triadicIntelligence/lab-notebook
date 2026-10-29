# Engineering log — v0.12

1. v0.9 kernel and v0.11 runner carried for provenance (hashes in run.json). New code: displaced.py.
2. Development (seed 0) found two defects before the freeze:
   - Declaration required a finite crossing point, so declarers were crossers by construction and
     the declarer/non-declarer comparison was confounded. Comparisons now use crossings *after*
     the declaration step, among organisms matched on having crossed before it.
   - A clean organism that had never crossed could not declare at all, which defeats the premise.
     Declaration now releases burden for anyone who has received grace; the counter-mark is written
     only where a gate was actually used. Declarations with no mark are counted as silent_declarations.
3. Under universal availability every graced organism declares, so the declarer/non-declarer
   comparisons for V1 and V3 are scored on the incident_only arm, where non-declarers exist.
4. No constant was retuned. v0.9 calibration carried unchanged.

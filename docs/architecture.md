# Architecture Notes

## Known Setup Issues

## Shared Indicator Schema (P0-TEAM1)

All analyzer modules (static, ML) ultimately produce indicators in this shape
before being written to the `indicators` table:

```python
{
    "source": "hash" | "yara" | "apk" | "pe" | "ml",
    "description": "human-readable description of the finding",
    "severity": "low" | "medium" | "high" | "critical",
}
```

Raw module output (e.g. `StaticAnalysisEngine.analyze()`) is NOT written directly
to the DB. It's converted through an adapter — see `api/services/indicator_adapter.py`
for the static-analysis version. Shreya's ML module should follow the same
contract: produce a list of `{source: "ml", description, severity}` dicts
(or a raw structure + a matching adapter function), so both paths converge on
one flat shape before hitting the `indicators` table.

## Risk Score Formula (P0-TEAM1)
final_score = 0.5 * static_score + 0.5 * ml_score
- `static_score`: derived from the highest-severity indicator found by the
  static engine, mapped to a number:
  critical = 1.0, high = 0.7, medium = 0.4, low = 0.1
- `ml_score`: the ML classifier's raw probability output (0.0–1.0)

**Open questions for team sign-off:**
1. Does the `RISKY_PERMISSIONS` severity table in `indicator_adapter.py` look
   right, or are there permissions/severities to add or change?
2. Can YARA rule authors add `meta.severity` and `meta.description` fields to
   `.yar` rules, so the adapter doesn't have to guess a default severity?
3. Does the static_score-to-number mapping above make sense, or should the
   weighting/thresholds change?
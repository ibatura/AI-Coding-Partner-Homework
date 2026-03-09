# Research Quality Measurement Skill

This skill defines the quality levels used by the **Bug Research Verifier** when rating
codebase research produced by a Bug Researcher.

---

## Quality Levels

| Level | Label | Pass / Fail | Criteria |
|-------|-------|-------------|----------|
| **5** | EXEMPLARY | PASS | Pass rate = 100 %; all file:line references verified; all code snippets match exactly; all factual claims supported; no unsupported or invalid items. |
| **4** | THOROUGH | PASS | Pass rate ≥ 90 %; 1–2 minor discrepancies present but documented; root cause and fix direction are unambiguously supported by verified evidence. |
| **3** | ADEQUATE | FAIL | Pass rate 70–89 %; notable discrepancies exist but the root cause remains identifiable from the verified claims; Bug Planner must verify flagged items before acting. |
| **2** | INSUFFICIENT | FAIL | Pass rate < 70 %; significant gaps or errors undermine the research; re-investigation recommended before proceeding. |
| **1** | INVALID | FAIL | Critical file paths are missing, the research contains no verifiable references, or the core findings are directly contradicted by the actual source. |

---

## Assessment Procedure

1. Count `total_count` — total references extracted from `codebase-research.md`.
2. Count `valid_count` — references marked MATCH (or MATCH with whitespace diff) whose factual claim is supported.
3. Calculate `pass_rate = valid_count / total_count × 100`.
4. Apply the table above to assign exactly one level.
5. If `total_count = 0`, assign **INVALID (1)** regardless of any prose analysis.

---

## Required Output Format

Every document that uses this skill must include the following block verbatim, filled in:

```
Research Quality: <LABEL> (Level <N>/5)
Score: <numeric estimate>/100
Reasoning: <1–3 sentences explaining the rating based on verification findings>
```

**Rules:**
- Assign **exactly one** level — do not hedge with ranges.
- The `Score` field is a numeric estimate out of 100 that reflects the pass rate and severity of any discrepancies.
- `Reasoning` must reference specific verification findings, not generic statements.

---

## Pass Threshold

| Result | Levels |
|--------|--------|
| PASS — Bug Planner may proceed | EXEMPLARY (5), THOROUGH (4) |
| FAIL — verify flagged items before acting | ADEQUATE (3) |
| FAIL — request re-investigation | INSUFFICIENT (2), INVALID (1) |

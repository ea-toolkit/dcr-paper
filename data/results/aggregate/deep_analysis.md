# Deep Analysis — Corrected Experiment (June 17, 2026)

Re-run of gap detection, stratification, and statistical tests on corrected data.
Experiment: 3 trials × 50 questions × 9 conditions = 1,350 evaluations.
Questions: 28 cross-cutting (no layer_hint), 22 single-layer.

## 1. Gap Detection Analysis

### naive_vector
**trial-1:** trigger=0.0% (0/50), signals=0, avg=0.0/q
  Types: {}
  Gaps by class: {'CLEAN': 0, 'INCOMPLETE': 0}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)
**trial-2:** trigger=0.0% (0/50), signals=0, avg=0.0/q
  Types: {}
  Gaps by class: {'CLEAN': 0, 'INCOMPLETE': 0}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)
**trial-3:** trigger=0.0% (0/50), signals=0, avg=0.0/q
  Types: {}
  Gaps by class: {'CLEAN': 0, 'INCOMPLETE': 0}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)

### vanilla_rag
**trial-1:** trigger=0.0% (0/50), signals=0, avg=0.0/q
  Types: {}
  Gaps by class: {'CLEAN': 0, 'INCOMPLETE': 0, 'MISSING': 0}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)
**trial-2:** trigger=0.0% (0/50), signals=0, avg=0.0/q
  Types: {}
  Gaps by class: {'CLEAN': 0, 'INCOMPLETE': 0, 'MISSING': 0}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)
**trial-3:** trigger=0.0% (0/50), signals=0, avg=0.0/q
  Types: {}
  Gaps by class: {'CLEAN': 0, 'INCOMPLETE': 0, 'MISSING': 0}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)

### dcr
**trial-1:** trigger=80.0% (40/50), signals=62, avg=1.24/q
  Types: {'ambiguous_entity': 37, 'orphan_entity': 25}
  Gaps by class: {'CLEAN': 48, 'INCOMPLETE': 14}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)
**trial-2:** trigger=80.0% (40/50), signals=62, avg=1.24/q
  Types: {'ambiguous_entity': 37, 'orphan_entity': 25}
  Gaps by class: {'CLEAN': 48, 'INCOMPLETE': 14}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)
**trial-3:** trigger=80.0% (40/50), signals=62, avg=1.24/q
  Types: {'ambiguous_entity': 37, 'orphan_entity': 25}
  Gaps by class: {'CLEAN': 50, 'INCOMPLETE': 12}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)

### full_dcr
**trial-1:** trigger=80.0% (40/50), signals=62, avg=1.24/q
  Types: {'ambiguous_entity': 37, 'orphan_entity': 25}
  Gaps by class: {'CLEAN': 44, 'INCOMPLETE': 18}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)
**trial-2:** trigger=80.0% (40/50), signals=62, avg=1.24/q
  Types: {'ambiguous_entity': 37, 'orphan_entity': 25}
  Gaps by class: {'CLEAN': 48, 'INCOMPLETE': 14}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)
**trial-3:** trigger=80.0% (40/50), signals=62, avg=1.24/q
  Types: {'ambiguous_entity': 37, 'orphan_entity': 25}
  Gaps by class: {'CLEAN': 46, 'INCOMPLETE': 16}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)

### no_intent
**trial-1:** trigger=64.0% (32/50), signals=39, avg=0.78/q
  Types: {'orphan_entity': 22, 'ambiguous_entity': 17}
  Gaps by class: {'CLEAN': 31, 'INCOMPLETE': 8}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)
**trial-2:** trigger=64.0% (32/50), signals=39, avg=0.78/q
  Types: {'orphan_entity': 22, 'ambiguous_entity': 17}
  Gaps by class: {'CLEAN': 31, 'INCOMPLETE': 8}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)
**trial-3:** trigger=64.0% (32/50), signals=39, avg=0.78/q
  Types: {'orphan_entity': 22, 'ambiguous_entity': 17}
  Gaps by class: {'INCOMPLETE': 11, 'CLEAN': 28}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)

### no_graph
**trial-1:** trigger=80.0% (40/50), signals=68, avg=1.36/q
  Types: {'ambiguous_entity': 49, 'orphan_entity': 19}
  Gaps by class: {'CLEAN': 52, 'INCOMPLETE': 16}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)
**trial-2:** trigger=80.0% (40/50), signals=68, avg=1.36/q
  Types: {'ambiguous_entity': 49, 'orphan_entity': 19}
  Gaps by class: {'CLEAN': 46, 'INCOMPLETE': 22}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)
**trial-3:** trigger=80.0% (40/50), signals=68, avg=1.36/q
  Types: {'ambiguous_entity': 49, 'orphan_entity': 19}
  Gaps by class: {'CLEAN': 48, 'INCOMPLETE': 20}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)

### no_layer_boost
**trial-1:** trigger=74.0% (37/50), signals=49, avg=0.98/q
  Types: {'orphan_entity': 29, 'ambiguous_entity': 20}
  Gaps by class: {'CLEAN': 39, 'INCOMPLETE': 10}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)
**trial-2:** trigger=74.0% (37/50), signals=49, avg=0.98/q
  Types: {'orphan_entity': 29, 'ambiguous_entity': 20}
  Gaps by class: {'INCOMPLETE': 15, 'CLEAN': 34}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)
**trial-3:** trigger=74.0% (37/50), signals=49, avg=0.98/q
  Types: {'orphan_entity': 29, 'ambiguous_entity': 20}
  Gaps by class: {'CLEAN': 39, 'INCOMPLETE': 10}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)

### no_confidence
**trial-1:** trigger=82.0% (41/50), signals=62, avg=1.24/q
  Types: {'ambiguous_entity': 36, 'orphan_entity': 26}
  Gaps by class: {'CLEAN': 46, 'INCOMPLETE': 16}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)
**trial-2:** trigger=82.0% (41/50), signals=62, avg=1.24/q
  Types: {'ambiguous_entity': 36, 'orphan_entity': 26}
  Gaps by class: {'CLEAN': 45, 'INCOMPLETE': 17}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)
**trial-3:** trigger=82.0% (41/50), signals=62, avg=1.24/q
  Types: {'ambiguous_entity': 36, 'orphan_entity': 26}
  Gaps by class: {'CLEAN': 52, 'INCOMPLETE': 10}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)

### no_dedup
**trial-1:** trigger=80.0% (40/50), signals=62, avg=1.24/q
  Types: {'ambiguous_entity': 37, 'orphan_entity': 25}
  Gaps by class: {'CLEAN': 47, 'INCOMPLETE': 15}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)
**trial-2:** trigger=80.0% (40/50), signals=62, avg=1.24/q
  Types: {'ambiguous_entity': 37, 'orphan_entity': 25}
  Gaps by class: {'INCOMPLETE': 14, 'CLEAN': 48}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)
**trial-3:** trigger=80.0% (40/50), signals=62, avg=1.24/q
  Types: {'ambiguous_entity': 37, 'orphan_entity': 25}
  Gaps by class: {'CLEAN': 49, 'INCOMPLETE': 13}
  thin_coverage: 0 (no NOT_ANSWERABLE with entities found)

### Gap Detection Summary (DCR, averaged across trials)

- Trigger rate: 80.0% ± 0.0%
- Total signals per trial: 62 ± 0.0
- Gap types (summed across trials): {'ambiguous_entity': 111, 'orphan_entity': 75}
- **Old paper claimed: 82% trigger, 184 signals**
- **New data: 80.0% trigger, 62 signals/trial**

### thin_coverage → MISSING Correlation

**No thin_coverage gaps found in any condition/trial.** This is expected: thin_coverage
fires when status=NOT_ANSWERABLE but entities were found. With MISSING at 0% in 8/9
conditions (only vanilla_rag has 2% MISSING), the trigger condition almost never occurs.

**Implication for the paper:** The 7/7 thin_coverage → MISSING correlation from the old
data cannot be verified on corrected data due to floor effect. The paper must either:
  (a) Remove the claim, or
  (b) Reframe: 'Gap detection fires on X% of questions as a curation signal,
      independent of answer quality. When MISSING does occur (vanilla_rag),
      gap signals are [present/absent].'

## 2. Cross-Cutting vs Single-Layer Stratification

Classification: 28 cross-cutting (layer_hint=''), 22 single-layer (layer_hint set)

### Pooled Results (3 trials combined)

| Condition | Stratum | N | CLEAN% | INC% | MISS% |
|-----------|---------|---|--------|------|-------|
| naive_vector | cross-cutting | 84 | 72.6 | 27.4 | 0.0 |
| naive_vector | single-layer | 66 | 65.2 | 34.8 | 0.0 |
| vanilla_rag | cross-cutting | 84 | 59.5 | 36.9 | 3.6 |
| vanilla_rag | single-layer | 66 | 59.1 | 40.9 | 0.0 |
| dcr | cross-cutting | 84 | 76.2 | 23.8 | 0.0 |
| dcr | single-layer | 66 | 75.8 | 24.2 | 0.0 |
| full_dcr | cross-cutting | 84 | 73.8 | 26.2 | 0.0 |
| full_dcr | single-layer | 66 | 69.7 | 30.3 | 0.0 |

### Per-Trial Stratified Results (DCR vs Vanilla RAG)

| Condition | Trial | Stratum | CLEAN | INC | MISS |
|-----------|-------|---------|-------|-----|------|
| dcr | trial-1 | cross-cutting | 21/28 (75.0%) | 7/28 (25.0%) | 0/28 (0.0%) |
| dcr | trial-1 | single-layer | 17/22 (77.3%) | 5/22 (22.7%) | 0/22 (0.0%) |
| dcr | trial-2 | cross-cutting | 21/28 (75.0%) | 7/28 (25.0%) | 0/28 (0.0%) |
| dcr | trial-2 | single-layer | 17/22 (77.3%) | 5/22 (22.7%) | 0/22 (0.0%) |
| dcr | trial-3 | cross-cutting | 22/28 (78.6%) | 6/28 (21.4%) | 0/28 (0.0%) |
| dcr | trial-3 | single-layer | 16/22 (72.7%) | 6/22 (27.3%) | 0/22 (0.0%) |
| vanilla_rag | trial-1 | cross-cutting | 17/28 (60.7%) | 10/28 (35.7%) | 1/28 (3.6%) |
| vanilla_rag | trial-1 | single-layer | 13/22 (59.1%) | 9/22 (40.9%) | 0/22 (0.0%) |
| vanilla_rag | trial-2 | cross-cutting | 17/28 (60.7%) | 10/28 (35.7%) | 1/28 (3.6%) |
| vanilla_rag | trial-2 | single-layer | 14/22 (63.6%) | 8/22 (36.4%) | 0/22 (0.0%) |
| vanilla_rag | trial-3 | cross-cutting | 16/28 (57.1%) | 11/28 (39.3%) | 1/28 (3.6%) |
| vanilla_rag | trial-3 | single-layer | 12/22 (54.5%) | 10/22 (45.5%) | 0/22 (0.0%) |

## 3. Statistical Tests

### 3.1 MISSING: DCR vs Vanilla RAG
- DCR MISSING: 0/150
- Vanilla RAG MISSING: 3/150
- Test: fisher_exact
- p-value: 0.2475
- Odds ratio: 0.0
- **Old paper: χ² = 5.10, p = 0.024**

### 3.2 Overall Quality: DCR vs Vanilla RAG (Mann-Whitney U)
- DCR mean ordinal: 2.76 (n=150)
- Vanilla RAG mean ordinal: 2.573 (n=150)
- U = 13179.0, p = 0.001571
- **Old paper: U = 10307.5, p = 0.059 (not significant)**

### 3.3 Kruskal-Wallis: All Baselines
- H = 10.349, p = 0.005659
- **Old paper: H = 2.68, p = 0.26 (not significant)**

### 3.4 Stratified MISSING Tests
**cross-cutting:** DCR MISS=0/84, RAG MISS=3/84, test=fisher_exact, p=0.2455
**single-layer:** DCR MISS=0/66, RAG MISS=0/66, test=fisher_exact, p=1.0

### 3.5 CLEAN Rate Comparison: DCR vs Vanilla RAG
- DCR: 114/150 (76.0%)
- Vanilla RAG: 89/150 (59.3%)
- χ² = 8.7756, p = 0.003053
- SIGNIFICANT at α=0.05

## 4. Ablation Pairwise Tests (vs full_dcr)

| Condition | ΔCLEAN | Mann-Whitney p | Significant? |
|-----------|--------|----------------|--------------|
| no_intent | +4.0pp | 0.4310 | no |
| no_graph | -4.0pp | 0.4510 | no |
| no_layer_boost | +2.0pp | 0.6976 | no |
| no_confidence | +0.0pp | 1.0000 | no |
| no_dedup | +2.0pp | 0.6976 | no |

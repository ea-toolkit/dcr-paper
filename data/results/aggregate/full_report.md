# DCR Paper — Complete Experiment Report

## Context

We built a **Domain-Constrained Retrieval (DCR)** pipeline — a 7-stage retrieval system designed for typed, layered knowledge bases (KBs). The KB uses a typed ontology: entities are categorized by type (system, process, team, API, etc.) and organized into layers (structural, behavioral, organizational, language, reference, decision).

The 7 DCR stages are:
1. **Intent classification** — regex-based query understanding that assigns weights to entity types/layers
2. **Parallel search** — vector (cosine), keyword (BM25-like), and typed graph traversal (BFS along typed edges)
3. **RRF fusion** — Reciprocal Rank Fusion with layer-priority boosting
4. **Confidence scoring** — adjusts scores based on entity density and content quality
5. **5-layer dedup** — deduplication across ID, text similarity, diversity, inverse frequency, and layer balance
6. **Context building** — assembles retrieved entities into a context window for synthesis
7. **Gap detection** — identifies knowledge gaps from retrieval dead-ends (novel contribution)

We compare DCR against two baselines on a synthetic healthcare claims domain KB (408 entities, 18 types, 6 layers).

## Experimental Setup

- **KB:** 408 entities across 18 types, 6 layers (Clearview Health Plans — synthetic domain)
- **Questions:** 50 eval questions generated from seed context, deduplicated (Jaccard >0.55 + entity overlap >0.7)
- **Trials:** 3 independent runs per condition (same questions, same KB, different LLM scoring runs)
- **Scoring:** Claude Sonnet judges each answer as ANSWERABLE/PARTIAL/NOT_ANSWERABLE, mapped to CLEAN/INCOMPLETE/MISSING
- **Conditions:** 9 total (3 baselines + 6 ablation)
- **Total evaluations:** 1,350 (50 questions × 9 conditions × 3 trials)
- **Errors:** 0 across all 1,350 evaluations

### Baselines (3 conditions)
| Condition | Description |
|-----------|-------------|
| naive_vector | Cosine similarity only. No keyword, no graph, no fusion. |
| vanilla_rag | Vector + keyword, simple score merge. No typed traversal, no confidence, no dedup. |
| dcr | Full 7-stage DCR pipeline |

### Ablation (6 conditions — remove one stage at a time from full DCR)
| Condition | What's removed |
|-----------|---------------|
| full_dcr | Nothing (control) |
| no_intent | Stage 1: intent classification — flat layer weights |
| no_graph | Stage 2: graph traversal — vector + keyword only |
| no_layer_boost | Stage 3: layer priority boosting from fusion |
| no_confidence | Stage 4: confidence/density scoring |
| no_dedup | Stage 5: 5-layer dedup — simple ID dedup only |

## Results

### Table 1: Baseline Comparison (mean ± SD across 3 trials)

| Condition | CLEAN (%) | INCOMPLETE (%) | MISSING (%) |
|-----------|-----------|----------------|-------------|
| naive_vector | 30.0±3.5 | 60.7±2.3 | 9.3±3.1 |
| vanilla_rag | 30.0±0.0 | 57.3±2.3 | 12.7±2.3 |
| dcr | 34.0±2.0 | 61.3±4.2 | 4.7±2.3 |

### Table 2: Ablation Study (mean ± SD across 3 trials)

| Condition | CLEAN (%) | INCOMPLETE (%) | MISSING (%) | Δ CLEAN vs full_dcr |
|-----------|-----------|----------------|-------------|---------------------|
| full_dcr | 38.0±6.0 | 56.7±6.4 | 5.3±4.2 | — |
| no_intent | 44.7±4.2 | 49.3±4.2 | 6.0±2.0 | +6.7 |
| no_graph | 40.7±1.2 | 53.3±3.1 | 6.0±2.0 | +2.7 |
| no_layer_boost | 37.3±3.1 | 59.3±4.2 | 3.3±1.2 | -0.7 |
| no_confidence | 35.3±4.2 | 56.0±5.3 | 8.7±1.2 | -2.7 |
| no_dedup | 39.3±1.2 | 56.0±2.0 | 4.7±1.2 | +1.3 |

### Table 3: Per-Question Stability (same answer across all 3 trials)

| Condition | Stable Questions | Stability % |
|-----------|-----------------|-------------|
| no_layer_boost | 44/50 | 88% |
| vanilla_rag | 42/50 | 84% |
| dcr | 41/50 | 82% |
| no_dedup | 41/50 | 82% |
| no_graph | 41/50 | 82% |
| no_intent | 39/50 | 78% |
| naive_vector | 37/50 | 74% |
| no_confidence | 35/50 | 70% |
| full_dcr | 34/50 | 68% |

### Per-Trial Raw Numbers

**Baselines:**
| Condition | Trial 1 | Trial 2 | Trial 3 |
|-----------|---------|---------|---------|
| naive_vector | 32% CLEAN, 62% INC, 6% MISS | 32% CLEAN, 58% INC, 10% MISS | 26% CLEAN, 62% INC, 12% MISS |
| vanilla_rag | 30% CLEAN, 56% INC, 14% MISS | 30% CLEAN, 60% INC, 10% MISS | 30% CLEAN, 56% INC, 14% MISS |
| dcr | 36% CLEAN, 58% INC, 6% MISS | 32% CLEAN, 66% INC, 2% MISS | 34% CLEAN, 60% INC, 6% MISS |

**Ablation:**
| Condition | Trial 1 | Trial 2 | Trial 3 |
|-----------|---------|---------|---------|
| full_dcr | 32% CLEAN, 64% INC, 4% MISS | 38% CLEAN, 52% INC, 10% MISS | 44% CLEAN, 54% INC, 2% MISS |
| no_intent | 46% CLEAN, 46% INC, 8% MISS | 40% CLEAN, 54% INC, 6% MISS | 48% CLEAN, 48% INC, 4% MISS |
| no_graph | 42% CLEAN, 50% INC, 8% MISS | 40% CLEAN, 54% INC, 6% MISS | 40% CLEAN, 56% INC, 4% MISS |
| no_layer_boost | 34% CLEAN, 64% INC, 2% MISS | 38% CLEAN, 58% INC, 4% MISS | 40% CLEAN, 56% INC, 4% MISS |
| no_confidence | 32% CLEAN, 60% INC, 8% MISS | 40% CLEAN, 50% INC, 10% MISS | 34% CLEAN, 58% INC, 8% MISS |
| no_dedup | 40% CLEAN, 56% INC, 4% MISS | 38% CLEAN, 58% INC, 4% MISS | 40% CLEAN, 54% INC, 6% MISS |

## Observations

### 1. DCR's value is failure prevention, not precision uplift
- DCR has the lowest MISSING rate (4.7±2.3%) vs vanilla RAG (12.7±2.3%) — a 63% reduction
- But CLEAN uplift over baselines is modest: +4pp over naive vector/vanilla RAG
- The full pipeline is conservative: it prevents failures but at the cost of scoring more things as INCOMPLETE

### 2. Typed retrieval stages hurt CLEAN on this dense KB
- Removing intent classification: CLEAN goes UP by +6.7pp (44.7% vs 38.0%)
- Removing graph traversal: CLEAN goes UP by +2.7pp
- Hypothesis: with 408 entities of every type available, intent-based filtering pushes correct entities down the ranking. On a smaller, bounded-context KB (50-80 entities), these stages would help disambiguate.

### 3. Confidence scoring is the one stage that earns its keep
- Removing confidence scoring: CLEAN drops -2.7pp AND MISSING rises to 8.7% (highest among ablation conditions)
- This stage adjusts entity relevance based on content density — it works because it's content-aware, not type-aware

### 4. The full pipeline is the LEAST stable condition
- full_dcr stability: 68% (34/50 questions same across 3 trials)
- Simpler conditions are more stable: vanilla_rag 84%, no_layer_boost 88%
- More pipeline complexity = more variance in LLM-judged outputs

### 5. Discrepancy between baseline DCR and ablation full_dcr
- Baseline DCR: 34.0±2.0% CLEAN
- Ablation full_dcr: 38.0±6.0% CLEAN
- These should be the same pipeline. The 4pp gap and the larger SD on full_dcr illustrate LLM scoring variance even with identical retrieval.

### 6. Key insight: typed ontology ≠ typed retrieval
- The typed ontology (entity types, layers, relationships, curated descriptions) makes ALL retrieval methods better — even naive vector benefits from well-structured entity files
- The typed retrieval STAGES (intent classification, layer boosting, graph traversal) add noise on dense KBs
- The ontology is the product value; the retrieval complexity is secondary

## Questions for Review

1. **Is the baseline DCR vs ablation full_dcr discrepancy (34% vs 38% CLEAN) a problem?** They run the same pipeline code. The gap is pure LLM scoring variance. Should we address this in the paper, and if so, how?

2. **Statistical significance:** With 50 questions and 3 trials, can we claim the MISSING reduction (DCR 4.7% vs RAG 12.7%) is significant? The SDs overlap slightly (4.7±2.3 vs 12.7±2.3). What test should we use for ordinal 3-category data?

3. **Paper framing:** We plan to frame this as: (a) DCR prevents failures (lowest MISSING), (b) typed stages are density-dependent — they hurt on dense KBs but would help on bounded contexts, (c) gap detection is the novel contribution (converting retrieval dead-ends into curation signals). Does this framing hold up given the data?

4. **The "negative ablation" story:** Removing stages improves CLEAN. This is an honest but counterintuitive result. How do we frame this without undermining the pipeline? Our current framing: "KB density threshold — typed stages earn their keep on smaller, focused search spaces (50-80 entities per block), not 400+ entity monolithic KBs."

5. **Venue recommendation:** Given these results — modest CLEAN uplift, strong MISSING reduction, honest ablation showing density dependence — which venue/workshop would be most receptive? We're considering arXiv first, then a workshop submission.

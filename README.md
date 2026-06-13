# Domain-Constrained Retrieval (DCR)

**Typed, Layered Search for Structured Knowledge Bases**

This repository contains the paper, synthetic knowledge base, evaluation data, and pipeline code for the DCR paper.

## What is DCR?

DCR is a 7-stage retrieval pipeline designed for typed, layered knowledge bases. It exploits entity type ontologies, typed relationships, and layered structure to improve retrieval over standard vector search. Its novel contribution is **gap detection** — surfacing knowledge base incompleteness as a curation signal during every query.

Key finding: DCR significantly reduces catastrophic retrieval failures (MISSING) compared to vanilla RAG (p=0.024), while converting every query into a knowledge base health probe.

Companion paper: [Demand-Driven Context](https://arxiv.org/abs/2603.14057) — the methodology for building the typed knowledge bases that DCR searches.

## Repository Structure

```
paper/              LaTeX source and compiled PDF
data/
  knowledge-base/   408-entity synthetic healthcare claims KB (18 types, 6 layers)
  questions/        50 evaluation questions (LLM-generated, human-reviewed)
  results/          3 trials x 9 conditions = 1,350 evaluations
    trial-{1,2,3}/  Per-condition checkpoint files
    aggregate/      Summary statistics, judge consistency, cross-model validation
pipeline/           Retrieval pipeline source code (snapshot)
```

## Experiment

- **Knowledge base**: Synthetic healthcare claims processing domain (408 entities, 18 types, 6 layers, 765 relationships)
- **Conditions**: 3 baselines (naive vector, vanilla RAG, full DCR) + 6 ablations (removing one pipeline stage each)
- **Trials**: 3 independent runs per condition (1,350 total evaluations)
- **Judge**: Claude Sonnet 4.6 with cross-model validation (GPT-4o, 80% agreement)
- **Statistical tests**: Chi-square (MISSING reduction, p=0.024), Mann-Whitney (overall quality, p=0.059)

## Reproducing

The `data/results/` directory contains all raw evaluation outputs. Each `*.checkpoint.json` file has per-question results including the question, retrieved entities, synthesized answer, DDC class, confidence score, and detected gaps.

The pipeline code in `pipeline/` is a snapshot of the retrieval implementation used in the experiment. It requires an embedding backend and LLM API access to run.

## Citation

```bibtex
@article{dcr2026,
  title={Domain-Constrained Retrieval: Typed, Layered Search for Structured Knowledge Bases},
  author={Navakoti, Raj},
  year={2026},
  note={Preprint}
}
```

## License

MIT

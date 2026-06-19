# DCR Paper — Experiment Tables

## Table 1: Baseline Comparison

| Condition | CLEAN (%) | INCOMPLETE (%) | MISSING (%) |
|-----------|-----------|----------------|-------------|
| naive_vector | 69.3±1.2 | 30.7±1.2 | 0.0±0.0 |
| vanilla_rag | 59.3±3.1 | 38.7±3.1 | 2.0±0.0 |
| dcr | 76.0±0.0 | 24.0±0.0 | 0.0±0.0 |

## Table 2: Ablation Study

| Condition | CLEAN (%) | INCOMPLETE (%) | MISSING (%) | Δ CLEAN |
|-----------|-----------|----------------|-------------|---------|
| full_dcr | 72.0±2.0 | 28.0±2.0 | 0.0±0.0 | — |
| no_intent | 76.0±2.0 | 24.0±2.0 | 0.0±0.0 | +4.0 |
| no_graph | 68.0±2.0 | 32.0±2.0 | 0.0±0.0 | -4.0 |
| no_layer_boost | 74.0±2.0 | 26.0±2.0 | 0.0±0.0 | +2.0 |
| no_confidence | 72.0±3.5 | 28.0±3.5 | 0.0±0.0 | +0.0 |
| no_dedup | 74.0±0.0 | 26.0±0.0 | 0.0±0.0 | +2.0 |

## Table 3: Per-Question Stability

| Condition | Stable Questions | Stability % |
|-----------|-----------------|-------------|
| dcr | 48/50 | 96.0% |
| full_dcr | 45/50 | 90.0% |
| naive_vector | 45/50 | 90.0% |
| no_confidence | 42/50 | 84.0% |
| no_dedup | 44/50 | 88.0% |
| no_graph | 41/50 | 82.0% |
| no_intent | 47/50 | 94.0% |
| no_layer_boost | 45/50 | 90.0% |
| vanilla_rag | 46/50 | 92.0% |

## LaTeX — Table 1

```latex
\begin{table}[h]
\centering
\caption{Baseline Comparison (mean $\pm$ SD across 3 trials)}
\begin{tabular}{lccc}
\toprule
Condition & CLEAN (\%) & INCOMPLETE (\%) & MISSING (\%) \\
\midrule
Naive Vector & $69.3 \pm 1.2$ & $30.7 \pm 1.2$ & $0.0 \pm 0.0$ \\
Vanilla RAG & $59.3 \pm 3.1$ & $38.7 \pm 3.1$ & $2.0 \pm 0.0$ \\
DCR (ours) & $76.0 \pm 0.0$ & $24.0 \pm 0.0$ & $0.0 \pm 0.0$ \\
\bottomrule
\end{tabular}
\end{table}
```

## LaTeX — Table 2

```latex
\begin{table}[h]
\centering
\caption{Ablation Study — Stage Contribution (mean $\pm$ SD)}
\begin{tabular}{lcccc}
\toprule
Condition & CLEAN (\%) & INCOMPLETE (\%) & MISSING (\%) & $\Delta$ CLEAN \\
\midrule
full\_dcr & $72.0 \pm 2.0$ & $28.0 \pm 2.0$ & $0.0 \pm 0.0$ & — \\
no\_intent & $76.0 \pm 2.0$ & $24.0 \pm 2.0$ & $0.0 \pm 0.0$ & $+4.0$ \\
no\_graph & $68.0 \pm 2.0$ & $32.0 \pm 2.0$ & $0.0 \pm 0.0$ & $-4.0$ \\
no\_layer\_boost & $74.0 \pm 2.0$ & $26.0 \pm 2.0$ & $0.0 \pm 0.0$ & $+2.0$ \\
no\_confidence & $72.0 \pm 3.5$ & $28.0 \pm 3.5$ & $0.0 \pm 0.0$ & $+0.0$ \\
no\_dedup & $74.0 \pm 0.0$ & $26.0 \pm 0.0$ & $0.0 \pm 0.0$ & $+2.0$ \\
\bottomrule
\end{tabular}
\end{table}
```
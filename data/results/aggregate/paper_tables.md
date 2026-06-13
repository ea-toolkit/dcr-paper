# DCR Paper — Experiment Tables

## Table 1: Baseline Comparison

| Condition | CLEAN (%) | INCOMPLETE (%) | MISSING (%) |
|-----------|-----------|----------------|-------------|
| naive_vector | 30.0±3.5 | 60.7±2.3 | 9.3±3.1 |
| vanilla_rag | 30.0±0.0 | 57.3±2.3 | 12.7±2.3 |
| dcr | 34.0±2.0 | 61.3±4.2 | 4.7±2.3 |

## Table 2: Ablation Study

| Condition | CLEAN (%) | INCOMPLETE (%) | MISSING (%) | Δ CLEAN |
|-----------|-----------|----------------|-------------|---------|
| full_dcr | 38.0±6.0 | 56.7±6.4 | 5.3±4.2 | — |
| no_intent | 44.7±4.2 | 49.3±4.2 | 6.0±2.0 | +6.7 |
| no_graph | 40.7±1.2 | 53.3±3.1 | 6.0±2.0 | +2.7 |
| no_layer_boost | 37.3±3.1 | 59.3±4.2 | 3.3±1.2 | -0.7 |
| no_confidence | 35.3±4.2 | 56.0±5.3 | 8.7±1.2 | -2.7 |
| no_dedup | 39.3±1.2 | 56.0±2.0 | 4.7±1.2 | +1.3 |

## Table 3: Per-Question Stability

| Condition | Stable Questions | Stability % |
|-----------|-----------------|-------------|
| dcr | 41/50 | 82.0% |
| full_dcr | 34/50 | 68.0% |
| naive_vector | 37/50 | 74.0% |
| no_confidence | 35/50 | 70.0% |
| no_dedup | 41/50 | 82.0% |
| no_graph | 41/50 | 82.0% |
| no_intent | 39/50 | 78.0% |
| no_layer_boost | 44/50 | 88.0% |
| vanilla_rag | 42/50 | 84.0% |

## LaTeX — Table 1

```latex
\begin{table}[h]
\centering
\caption{Baseline Comparison (mean $\pm$ SD across 3 trials)}
\begin{tabular}{lccc}
\toprule
Condition & CLEAN (\%) & INCOMPLETE (\%) & MISSING (\%) \\
\midrule
Naive Vector & $30.0 \pm 3.5$ & $60.7 \pm 2.3$ & $9.3 \pm 3.1$ \\
Vanilla RAG & $30.0 \pm 0.0$ & $57.3 \pm 2.3$ & $12.7 \pm 2.3$ \\
DCR (ours) & $34.0 \pm 2.0$ & $61.3 \pm 4.2$ & $4.7 \pm 2.3$ \\
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
full\_dcr & $38.0 \pm 6.0$ & $56.7 \pm 6.4$ & $5.3 \pm 4.2$ & — \\
no\_intent & $44.7 \pm 4.2$ & $49.3 \pm 4.2$ & $6.0 \pm 2.0$ & $+6.7$ \\
no\_graph & $40.7 \pm 1.2$ & $53.3 \pm 3.1$ & $6.0 \pm 2.0$ & $+2.7$ \\
no\_layer\_boost & $37.3 \pm 3.1$ & $59.3 \pm 4.2$ & $3.3 \pm 1.2$ & $-0.7$ \\
no\_confidence & $35.3 \pm 4.2$ & $56.0 \pm 5.3$ & $8.7 \pm 1.2$ & $-2.7$ \\
no\_dedup & $39.3 \pm 1.2$ & $56.0 \pm 2.0$ & $4.7 \pm 1.2$ & $+1.3$ \\
\bottomrule
\end{tabular}
\end{table}
```
# results/

Frozen benchmark runs. Immutable ledger — excluded from subject workspace (root README § Isolation, Phase 1).  
冻结评测批次。只读账本；受测平面外，第 1 阶段移出（见根 README § 隔离规程）。

| Run | Agents | Scored | Summary |
|-----|-------:|--------|---------|
| [`2026-06-10`](2026-06-10/) | 10 | 2026-06-10 | [`summary/`](2026-06-10/summary/) |

## Layout per run | 单批次结构

```
results/<run_id>/
├── manifest.yaml      # run metadata · 批次元数据
├── submissions/       # frozen submissions · 冻结答卷
├── reports/           # frozen score reports · 冻结评分报告
└── summary/           # derived figures & CSV · 派生图表
```

## Regenerate summary | 重新生成汇总

```bash
python scripts/plot_results.py --run 2026-06-10
```

Reads `submissions/` front matter and `reports/` item tables; writes `summary/`.  
读取答卷元数据与报告逐题表；输出至 `summary/`。

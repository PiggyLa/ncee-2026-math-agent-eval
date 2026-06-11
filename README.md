# ncee-2026-math-agent-eval

Closed-book evaluation framework for AI agents on **2026 NCEE Mathematics · New Curriculum Paper I** (19 items, 150 pts).  
AI Agent 闭卷数学评测框架 · 测试集：2026 新高考 I 卷数学（19 题，150 分）。

---

## Objective | 目标

Under strict isolation, expose stems only to the subject agent, collect timed submissions, then score against the reference key and rubric—measuring mathematical reasoning, formal derivation, and correctness.  
在信息隔离条件下向受测 Agent 仅提供题干，采集限时答卷，对照标答与评分规则改卷，评估数学推理与解题正确率。

---

## Layout | 目录

```
ncee-2026-math-agent-eval/
├── README.md                        # protocol & prompts
├── .gitignore                       # workspace artifacts excluded
├── exam/
│   └── stems_bilingual.md           # Subject · stems only
├── key/
│   ├── README.md                    # source & errata policy
│   └── answer_key_bilingual.md      # Scorer · answers + sketches + errata
├── submissions/
│   └── submission_template.md       # Subject → Scorer · workspace
├── scoring/
│   └── rubric.md                    # Scorer · rules · workspace
├── results/                         # frozen runs · ledger
│   └── <run_id>/                    # manifest, submissions, reports, summary
├── paper/                           # manuscript (en arXiv master + zh companion)
│   ├── en/main.tex
│   └── zh/main_zh.tex
└── scripts/
    └── plot_results.py              # summary figures from results/<run_id>/
```

| Path | Subject | Role |
|------|:-------:|------|
| `exam/` | ✓ | Closed-book stems · 闭卷题干 |
| `submissions/` | ✓ | Workspace · template + one ephemeral submission · 工作区模板与答卷 |
| `key/` | ✗ | Reference key · 标答与要点 |
| `scoring/` | ✗ | Workspace · rubric & ephemeral reports · 工作区规则与报告 |
| `results/` | ✗ | Ledger · frozen runs · 冻结批次账本 |
| `paper/` | ✗ | Manuscript · results & errata quoted · 论文稿（含结果与勘误） |
| `scripts/` | ✗ | Tooling · derived figures · 派生图表工具 |

**Roles · 角色** — **Subject** · 受测 Agent（闭卷作答）| **Scorer** · 改卷方 | **Maintainer** · 维护方（归档与派生图表）

---

## Isolation | 隔离规程

Run per evaluation. The subject agent must never see keys, rubrics, ledger runs, tooling, or prior workspace outputs.  
每轮评测执行；受测 Agent 不得接触标答、评分规则、账本批次、维护工具及历史工作区产物。

| Phase | EN | ZH |
|:-----:|----|----|
| 1 · Prepare | Remove `key/`, `scoring/`, `results/`, `paper/`, `scripts/` from the subject-visible workspace; clear `submissions/` except `submission_template.md` | 移出 `key/`、`scoring/`、`results/`、`paper/`、`scripts/`；清空 `submissions/`（保留 `submission_template.md`） |
| 2 · Exam | Subject reads subject surface only (below); writes one submission to `submissions/` | 受测方仅读受测平面（下）；向 `submissions/` 写入一份答卷 |
| 3 · Score | Restore `key/` and `scoring/`; grade against key and rubric; write report to `scoring/` | 恢复 `key/` 与 `scoring/`；对照标答与规则改卷；报告写入 `scoring/` |
| 4 · Publish | Copy workspace outputs to `results/<run_id>/`; regenerate `summary/` via `scripts/plot_results.py` | 将工作区产物复制至 `results/<run_id>/`；以 `scripts/plot_results.py` 再生 `summary/` |

**Subject surface · 受测平面** (Phase 2): `README.md` · `exam/stems_bilingual.md` · `submissions/submission_template.md`  
**Scorer surface · 改卷平面** (Phase 3): subject surface + `key/` · `scoring/rubric.md` · target submission in `submissions/`

`scoring/rubric.md` lists free-response key results — scorer-side only; whole `scoring/` removed in Phase 1.  
`scoring/rubric.md` 含解答题结论，仅限改卷侧；第 1 阶段整目录 `scoring/` 移出。

---

## Pipeline | 流程

Mirrors [Isolation](#isolation--隔离规程) Phases 1–4.  
与[隔离规程](#isolation--隔离规程)第 1–4 阶段一一对应。

### Exam | 闭卷作答 · Phase 2

1. Complete Phase 1 · Prepare.
2. Issue [Exam prompt](#exam-prompt--闭卷提示词).
3. Write `submissions/YYYYMMDD_HHMMSS_<slug>.md` (timestamp = `completed_at`; slug per [Model slug](#model-slug--模型标识)).

Required front matter: `started_at`, `completed_at`, `duration`, `duration_seconds`, `model`, `model_display`, `max_mode`, `thinking`, `fast`, `effort`, `agent`, `exam`, `source_file`. `submission_id` must match filename stem.

### Model slug | 模型标识

`model_display` = Cursor UI 原名。不清楚则问，禁止猜测。

`slug = normalize(model_display)` — lowercase; `.` `_` space → `-`; `[a-z0-9-]` only. E.g. `Composer 2.5 Fast` → `composer-2-5-fast`.

`model` = 厂商族 ID。`effort` = UI 档位（`low`|`medium`|`high`|`extra-high`|`max`），无则 `none`。`thinking` / `fast` / `max_mode` 仅记 UI 有的项。

### Scoring | 改卷 · Phase 3

1. Complete Phase 1 · Prepare; restore `key/` and `scoring/`.
2. Issue [Scoring prompt](#scoring-prompt--改卷提示词).
3. Write `scoring/YYYYMMDD_HHMMSS_<model>_score.md`.

### Publish | 归档 · Phase 4

1. Copy workspace submission(s) to `results/<run_id>/submissions/`.
2. Copy score report(s) to `results/<run_id>/reports/`.
3. Run `python scripts/plot_results.py --run <run_id>` → `results/<run_id>/summary/`.

---

## Exam prompt | 闭卷提示词

```
[Closed-Book Eval · 闭卷评测]
2026 NCEE Mathematics · New Curriculum Paper I (19 items, 150 pts)
2026 新高考 I 卷 · 数学（19 题，150 分）

Work in this repository only.

[Timing · 计时 — DO THIS FIRST · 首步必做]
Run shell immediately; record started_at (YYYY-MM-DDTHH:MM:SS+08:00).
No retroactive unknown · 立即 shell 记录，禁止事后补填 unknown.

[Rules · 规则]
1. Read · 可读: exam/stems_bilingual.md; submissions/submission_template.md; README.md
2. Prohibited · 禁止: key/; scoring/; results/; paper/; scripts/; prior submissions or reports; external keys
   不得访问 key/、scoring/、results/、paper/、scripts/、历史答卷或评分报告、外部标答
3. Scope · 范围: ALL 19 items
   Single Q01–Q08 | Multiple Q09–Q11 | Fill-in Q12–Q14 | Free response Q15–Q19
4. Quality · 质量:
   - Objective: final answers in table (Q01–Q14)
   - Free response: key derivation + conclusions; not final answers alone
   - LaTeX for formulas · 公式用 LaTeX
   - Verify when needed · 必要时验算

[Submit · 提交]
1. Read submissions/submission_template.md
2. Write submissions/YYYYMMDD_HHMMSS_<slug>.md (lowercase slug)
3. Run shell for completed_at before save; filename timestamp MUST match
4. Front matter required · 必填:
   started_at, completed_at, duration (HH:MM:SS), duration_seconds,
   model, model_display, max_mode, thinking, fast, effort,
   agent, exam, source_file
   submission_id = filename stem (YYYYMMDD_HHMMSS_<slug>)
   duration = completed_at − started_at
   model_display = Cursor UI 原名；slug = normalize(model_display)（见 README § Model slug）

[Self-check · 提交前自检]
□ Q01–Q19 present · 题号齐全
□ Q01–Q14 filled · 客观题无空
□ Free-response working complete · 解答题推导完整
□ PMF sums to 1 where applicable · 概率分布归一
□ model_display = exact Cursor UI name · 与界面显示名一致
□ slug = normalize(model_display) · slug 由 UI 名规范化得出
□ submission_id = filename stem · 答卷 ID 与文件名一致
□ Filename timestamp = completed_at

Begin now.
```

---

## Scoring prompt | 改卷提示词

```
[Scoring · 改卷]
2026 NCEE Mathematics · New Curriculum Paper I (150 pts)
2026 新高考 I 卷 · 数学（150 分）

Score one submission against the reference key and rubric.

[Inputs · 输入]
- Submission · 答卷: submissions/<file>.md  (user specifies file)
- Key · 标答: key/answer_key_bilingual.md
- Rubric · 规则: scoring/rubric.md

[Procedure · 流程]
1. Read all three inputs above
2. Score item-by-item (Q01–Q19) per scoring/rubric.md
3. Write report to scoring/YYYYMMDD_HHMMSS_<model>_score.md
   (timestamp = scored_at; <model> = subject model slug from submission)

[Rules · 规则]
- Single Q01–Q08: correct 5, wrong 0
- Multiple Q09–Q11: all correct 6; partial without wrong 3; any wrong 0
- Fill-in Q12–Q14: equivalent forms accepted; Q13 two blanks 2.5 each
- Free response Q15–Q19: compare key results and reasoning quality;
  award partial credit where rubric and key support it
- Errata items (key § Errata): verified values govern; circulated variants no credit
  勘误条目以验证值为准，网传值不给分

[Report · 报告]
Front matter (YAML):
  framework, scored_submission, answer_key, scorer_model, scored_at (+08:00)

Body · 正文:
- Table: | No. | Max | Got | Match | Note |
- Section subtotals · 分项得分: single / multiple / fill-in / free response
- Error list · 错题列表
- Footer: Total: __ / 150 · 总分: __ / 150

Begin scoring.
```

---

## Published runs | 公开批次

Ledger in `results/<run_id>/` — written in Phase 4 · Publish; never on the subject surface.  
账本位于 `results/<run_id>/`，仅于第 4 阶段写入；不属于受测平面。

| Run | Index |
|-----|-------|
| 2026-06-10 | [`results/README.md`](results/README.md) |

```bash
python scripts/plot_results.py --run 2026-06-10
```

---

## Paper | 论文

Manuscript for run `2026-06-10` in [`paper/`](paper/README.md) — `en/main.tex` (arXiv master · pdfLaTeX) · `zh/main_zh.tex` (中文对照 · XeLaTeX). Build & submission guide in `paper/README.md`.
批次 `2026-06-10` 的论文稿；编译与投稿指引见 `paper/README.md`。论文属维护方平面，第 1 阶段移出（见上文隔离规程）。

---

## Encoding | 编码

UTF-8, no BOM. · UTF-8，无 BOM。

---

## Note | 说明

Original paper: Q15 figure embedded (TikZ in MD); Q16–Q19 no figures.  
Reference key: web-circulated answers (officiality unverified), all 19 items independently re-derived; divergences in `key/answer_key_bilingual.md` § Errata.  
原卷仅 Q15 含配图（MD 内嵌 TikZ），Q16–Q19 无配图。标答源自网传参考答案并经全卷独立验算，不一致处见 `key/answer_key_bilingual.md` 勘误。

---
framework: ncee-2026-math-agent-eval
document_id: ncee-2026-math-agent-eval-rubric
encoding: UTF-8
answer_key: key/answer_key_bilingual.md
exam_en: 2026 NCEE Mathematics · New Curriculum Paper I
exam_zh: 2026年普通高等学校招生全国统一考试 · 数学 · 新课标 I 卷
total_score: 150
---

# Scoring Rubric | 评分规则

## Procedure | 流程

**EN.**
1. Inputs: submission `submissions/<file>.md`; key `key/answer_key_bilingual.md`.
2. Score item-by-item; write `scoring/YYYYMMDD_HHMMSS_<model>_score.md`.
3. Report: total, section subtotals, error list.

**ZH.**
1. 输入：答卷与 `key/answer_key_bilingual.md`。
2. 逐题比对，写出 `scoring/YYYYMMDD_HHMMSS_<model>_score.md`。
3. 报告含总分、分项得分、错题列表。

## Points | 分值

| Section | Items | Points |
|---------|-------|--------|
| Single choice · 单选 | 1–8 | 40 (5 each) |
| Multiple choice · 多选 | 9–11 | 18 (6 each) |
| Fill-in · 填空 | 12–14 | 15 (5 each) |
| Free response · 解答 | 15–19 | 77 |

## Objective | 客观题

- **Single (Q01–Q08):** correct 5; wrong 0.
- **Multiple (Q09–Q11):** all correct 6; partial without wrong 3; any wrong 0.
- **Fill-in (Q12–Q14):** equivalent forms accepted; Q13 two blanks 2.5 each.

## Free response | 解答题

| Q | Pts | Key results |
|:-:|----:|-------------|
| 15 | 13 | (1) $DE\parallel BC_1\Rightarrow DE\parallel$ plane $BCC_1B_1$; (2) $AC=2$, distance $=1$ |
| 16 | 15 | (1) $\cos A=\dfrac{1}{3}$; (2) $CE=3\sqrt{5}$ |
| 17 | 15 | (1) PMF $\dfrac{1}{3},\dfrac{2}{9},\dfrac{4}{27},\dfrac{8}{27}$; (2)(i) $(1-p)^k$; (ii) memoryless proof |
| 18 | 17 | (1) $\dfrac{x^2}{4}+\dfrac{y^2}{3}=1$; (2)(i) $y=\dfrac{\sqrt{5}}{2}(x+1)$; (ii) $\min\tan\angle PQR=4\sqrt{3}$ |
| 19 | 17 | (1) $D(-1)=\left(0,\dfrac{3}{2}\right)$; (2) $D(x_2)\subseteq D(x_1)$; (3) $f(0)\geqslant1$; increasing on $(0,+\infty)$ |

Step quality earns partial credit; bare conclusions earn minimal credit.  
按推导步骤给部分分；仅有结论得最低分。

## Divergences | 勘误口径

Verified values govern (`key/answer_key_bilingual.md` § Errata); circulated variants earn no credit.  
以验证值为准（见标答《勘误》）；网传值不给分。

## Report format | 报告格式

```yaml
---
framework: ncee-2026-math-agent-eval
scored_submission: submissions/xxx.md
answer_key: key/answer_key_bilingual.md
scorer_model: ...
scored_at: ISO8601+08:00
---
```

`| No. | Max | Got | Match | Note |`  
**Total: __ / 150 · 总分: __ / 150**

# -*- coding: utf-8 -*-
"""
plot_results.py — ncee-2026-math-agent-eval results figure
===========================================================

Publication-grade composite figure for the closed-book AI-agent evaluation on
2026 NCEE Mathematics, New Curriculum Paper I (19 items, 150 points).
English-only labels, cold editorial style.

Panels
    a  Total score per model (family-hued, duration annotated)
    b  Score by family (per-model points, range, mean)
    c  Per-item point-loss matrix (Q01-Q19; empty cell = full credit)
    d  Score vs. wall-clock time (unlabeled secondary reference)

Data provenance
    results/<run_id>/submissions/*.md   front matter  -> model, duration
    results/<run_id>/reports/*_score.md item tables   -> per-item scores

Usage
    python scripts/plot_results.py --run 2026-06-10
    python scripts/plot_results.py --run 2026-06-10 --paper
Outputs
    results/<run_id>/summary/ncee2026_results.png         (300 dpi)
    results/<run_id>/summary/ncee2026_results.svg
    results/<run_id>/summary/scores.csv
    --paper: ncee2026_results_paper.{png,svg} — manuscript variant,
    header/footer stripped (caption carries the metadata), tight bbox.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections.abc import Sequence
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parent.parent

#         Q01..Q08 (5 ea)   Q09-Q11 (6 ea)  Q12-14 (5 ea)  Q15  Q16  Q17  Q18  Q19
MAX_PTS = (5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 5, 5, 5, 13, 15, 15, 17, 17)

FAMILY_ORDER = ["Claude", "GPT", "Gemini", "Kimi", "Composer"]
FAMILY_BASE = {
    "Claude":   "#A8503A",
    "GPT":      "#2F7D72",
    "Gemini":   "#4571B8",
    "Kimi":     "#6E599A",
    "Composer": "#5D6B7C",
}
FAMILY_VENDOR = {
    "Claude": "Anthropic", "GPT": "OpenAI", "Gemini": "Google",
    "Kimi": "Moonshot AI", "Composer": "Cursor",
}

# tier shades within family — stable across regenerations
SLUG_COLOR = {
    "fable-5":            "#8F3F2A",
    "claude-opus-4-8":    "#B65C45",
    "haiku-4-5":          "#D9926F",
    "gpt-5-5":            "#1E6A60",
    "gpt-5-1":            "#3E8B7E",
    "gpt-5-4-nano":       "#7DB3A8",
    "gemini-3-1-pro":     "#34589B",
    "gemini-3-5-flash":   "#7C9BD9",
    "kimi-k2-5":          "#6E599A",
    "composer-2-5-fast":  "#5D6B7C",
}

PAPER  = "#FBFCFE"
INK    = "#1B2128"
SLATE  = "#4A545F"
MUTE   = "#8A95A1"
FAINT  = "#E7ECF1"
TRACK  = "#EEF2F7"
ZEBRA  = "#F3F6FA"
RULE   = "#D8DFE6"

LOSS_CMAP = LinearSegmentedColormap.from_list(
    "ink_ice",
    ["#F2F6FA", "#C9D5E2", "#92A8C0", "#54718E", "#22384E", "#101E2C"],
)

SECTIONS = [
    ("Single choice · 5 pt", 0, 8),
    ("Multiple choice · 6 pt", 8, 11),
    ("Fill-in · 5 pt", 11, 14),
    ("Free response · 13\u201317 pt", 14, 19),
]

TITLE_KW = dict(loc="left", fontsize=10.5, fontweight="bold", color=INK, pad=13)
LETTER_X_LEFT = 0.058
LETTER_X_RIGHT = 0.654
FIG_STEM = "ncee2026_results"

MODELS: list[dict] = []
RUN_META: dict[str, str | int] = {}


def setup_style() -> None:
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "figure.facecolor": PAPER,
        "axes.facecolor": PAPER,
        "savefig.facecolor": PAPER,
        "axes.edgecolor": "#2A2F36",
        "axes.linewidth": 0.8,
        "xtick.color": SLATE,
        "ytick.color": SLATE,
        "text.color": INK,
        "svg.fonttype": "none",
    })


def parse_front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end < 0:
        return {}
    block = text[3:end].strip()
    out: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        out[key.strip()] = val.strip()
    return out


def slug_from_stem(stem: str) -> str:
    parts = stem.split("_", 2)
    return parts[2] if len(parts) >= 3 else stem


def slug_from_report(path: Path) -> str:
    stem = path.stem.removesuffix("_score")
    return slug_from_stem(stem)


def family_for_slug(slug: str) -> str:
    if slug in ("fable-5", "claude-opus-4-8", "haiku-4-5"):
        return "Claude"
    if slug.startswith("gpt-"):
        return "GPT"
    if slug.startswith("gemini-"):
        return "Gemini"
    if slug.startswith("kimi-"):
        return "Kimi"
    if slug.startswith("composer-"):
        return "Composer"
    raise ValueError(f"unknown family for slug: {slug}")


def parse_report_scores(path: Path) -> tuple[int, ...]:
    text = path.read_text(encoding="utf-8")
    scores: list[int] = []
    for line in text.splitlines():
        if not re.match(r"^\|\s*\d{2}\s*\|", line):
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) < 3:
            continue
        scores.append(int(cols[2]))
    if len(scores) != 19:
        raise ValueError(f"{path.name}: expected 19 item scores, got {len(scores)}")
    return tuple(scores)


def load_run(run_id: str) -> Path:
    global MODELS, RUN_META

    run_dir = ROOT / "results" / run_id
    sub_dir = run_dir / "submissions"
    rep_dir = run_dir / "reports"
    manifest = run_dir / "manifest.yaml"

    if not sub_dir.is_dir() or not rep_dir.is_dir():
        raise FileNotFoundError(f"run incomplete: {run_dir}")

    RUN_META = {"run_id": run_id, "agents": 0}
    if manifest.is_file():
        for line in manifest.read_text(encoding="utf-8").splitlines():
            if ":" not in line:
                continue
            key, _, val = line.partition(":")
            key, val = key.strip(), val.strip()
            if key in ("agents", "items", "total_score"):
                RUN_META[key] = int(val)
            else:
                RUN_META[key] = val

    subs: dict[str, tuple[Path, dict[str, str]]] = {}
    for path in sorted(sub_dir.glob("*.md")):
        meta = parse_front_matter(path.read_text(encoding="utf-8"))
        slug = slug_from_stem(path.stem)
        subs[slug] = (path, meta)

    models: list[dict] = []
    for rep_path in sorted(rep_dir.glob("*_score.md")):
        slug = slug_from_report(rep_path)
        if slug not in subs:
            raise FileNotFoundError(f"no submission for report slug: {slug}")
        _, meta = subs[slug]
        name = meta.get("model_display", slug)
        duration_s = int(meta.get("duration_seconds", "0"))
        family = family_for_slug(slug)
        color = SLUG_COLOR.get(slug, FAMILY_BASE[family])
        items = parse_report_scores(rep_path)
        models.append(dict(
            name=name, slug=slug, family=family,
            color=color, duration_s=duration_s, items=items,
            completed_at=meta.get("completed_at", ""),
        ))

    MODELS = models
    RUN_META["agents"] = RUN_META.get("agents") or len(models)
    return run_dir / "summary"


def fmt_mmss(seconds: int) -> str:
    return f"{seconds // 60:d}:{seconds % 60:02d}"


def section_sums(items: Sequence[int]) -> tuple[int, int, int, int]:
    return (sum(items[0:8]), sum(items[8:11]), sum(items[11:14]), sum(items[14:19]))


def sorted_models() -> list[dict]:
    return sorted(
        MODELS,
        key=lambda m: (-sum(m["items"]),
                       FAMILY_ORDER.index(m["family"]),
                       m["completed_at"]),
    )


def panel_letter(fig: plt.Figure, ax: plt.Axes, letter: str, x: float) -> None:
    pos = ax.get_position()
    fig.text(x, pos.y1 + 0.018, letter, fontsize=12.5, fontweight="bold",
             color=INK, ha="left", va="baseline")


def draw_ranking(ax: plt.Axes, models: list[dict]) -> None:
    n = len(models)
    scores = [sum(m["items"]) for m in models]
    mean = sum(scores) / n

    for y, m in enumerate(models):
        s = sum(m["items"])
        if y % 2 == 1:
            ax.axhspan(y - 0.5, y + 0.5, color=ZEBRA, zorder=0)
        ax.barh(y, 150, height=0.60, color=TRACK, zorder=1)
        ax.barh(y, s, height=0.60, color=m["color"], zorder=2)
        ax.scatter([s], [y], s=46, color=m["color"],
                   edgecolor="white", linewidth=1.0, zorder=4)
        ax.text(s + 3.0, y, f"{s}", va="center", ha="left",
                fontsize=10.5, fontweight="bold", color=INK, zorder=5)
        ax.text(-0.015, y - 0.17, m["name"], transform=ax.get_yaxis_transform(),
                ha="right", va="center", fontsize=9.3, fontweight="bold",
                color=FAMILY_BASE[m["family"]])
        ax.text(-0.015, y + 0.28, fmt_mmss(m["duration_s"]),
                transform=ax.get_yaxis_transform(),
                ha="right", va="center", fontsize=6.8, color=MUTE)

    ax.axvline(150, color="#9AA6B2", lw=0.9, dashes=(4, 3), zorder=1.5)
    ax.axvline(mean, color="#8A95A1", lw=0.9, ls=":", zorder=1.5)
    ax.text(mean, -0.78, f"mean = {mean:.1f}", ha="center", va="center",
            fontsize=7.2, color=MUTE, clip_on=False)
    ax.text(-0.015, -0.78, "duration (m:ss)", transform=ax.get_yaxis_transform(),
            ha="right", va="center", fontsize=6.8, color=MUTE, style="italic")

    ax.set_xlim(0, 160)
    ax.set_ylim(n - 0.5, -1.1)
    ax.set_xticks([0, 30, 60, 90, 120, 150])
    ax.set_yticks([])
    ax.tick_params(axis="x", labelsize=8, length=3, width=0.8)
    ax.grid(axis="x", color=FAINT, lw=0.7, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.set_title("Total score (max 150)", **TITLE_KW)


def draw_family(ax: plt.Axes) -> None:
    agg = []
    for fam in FAMILY_ORDER:
        ms = [m for m in MODELS if m["family"] == fam]
        if not ms:
            continue
        ss = [sum(m["items"]) for m in ms]
        agg.append((fam, ms, ss, sum(ss) / len(ss)))
    agg.sort(key=lambda t: -t[3])

    for y, (fam, ms, ss, mean) in enumerate(agg):
        base = FAMILY_BASE[fam]
        if y % 2 == 1:
            ax.axhspan(y - 0.5, y + 0.5, color=ZEBRA, zorder=0)
        if max(ss) > min(ss):
            ax.plot([min(ss), max(ss)], [y, y], color=base, lw=2.2,
                    alpha=0.45, solid_capstyle="round", zorder=2)
        seen: dict[int, int] = {}
        for m, s in zip(ms, ss):
            k = seen.get(s, 0)
            seen[s] = k + 1
            jitter = (-0.13 if k == 1 else 0.13 if k == 2 else 0.0)
            ax.scatter([s], [y + jitter], s=40, color=m["color"],
                       edgecolor="white", linewidth=0.8, zorder=3)
        ax.scatter([mean], [y], marker="D", s=58, color=base,
                   edgecolor=INK, linewidth=0.8, zorder=4)
        ax.text(mean, y - 0.34, f"{mean:.1f}", ha="center", va="center",
                fontsize=8.4, fontweight="bold", color=INK)
        ax.text(-0.02, y - 0.16, fam, transform=ax.get_yaxis_transform(),
                ha="right", va="center", fontsize=9.3, fontweight="bold",
                color=base)
        ax.text(-0.02, y + 0.26, f"{FAMILY_VENDOR[fam]} · n={len(ms)}",
                transform=ax.get_yaxis_transform(),
                ha="right", va="center", fontsize=6.6, color=MUTE)

    ax.scatter([0.045], [0.945], transform=ax.transAxes, marker="D", s=34,
               color=SLATE, edgecolor=INK, linewidth=0.7,
               clip_on=False, zorder=5)
    ax.text(0.085, 0.945, "mean", transform=ax.transAxes,
            ha="left", va="center", fontsize=7.0, color=SLATE)

    ax.axvline(150, color="#9AA6B2", lw=0.9, dashes=(4, 3), zorder=1.5)
    ax.set_xlim(96, 158)
    ax.set_ylim(len(agg) - 0.5, -1.1)
    ax.set_xticks([100, 120, 140, 150])
    ax.set_yticks([])
    ax.tick_params(axis="x", labelsize=8, length=3, width=0.8)
    ax.grid(axis="x", color=FAINT, lw=0.7, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.set_title("Score by family", **TITLE_KW)


def draw_loss_matrix(ax: plt.Axes, models: list[dict]) -> None:
    n = len(models)
    for r, m in enumerate(models):
        for c, (got, mx) in enumerate(zip(m["items"], MAX_PTS)):
            loss = mx - got
            ratio = loss / mx
            face = LOSS_CMAP(ratio) if loss > 0 else "#FAFCFD"
            ax.add_patch(Rectangle((c, r), 1, 1, facecolor=face,
                                   edgecolor="#E2E8EF", lw=0.55, zorder=2))
            if loss > 0:
                ax.text(c + 0.5, r + 0.52, f"\u2212{loss:g}",
                        ha="center", va="center", fontsize=7.2,
                        fontweight="bold", zorder=3,
                        color="white" if ratio > 0.45 else INK)
        total_loss = 150 - sum(m["items"])
        ax.text(-0.012, r + 0.5, m["name"], transform=ax.get_yaxis_transform(),
                ha="right", va="center", fontsize=8.6,
                fontweight="bold", color=FAMILY_BASE[m["family"]])
        ax.text(19.25, r + 0.5, f"\u2212{total_loss}" if total_loss else "",
                ha="left", va="center", fontsize=7.8, color=SLATE,
                clip_on=False)

    for x in (8, 11, 14):
        ax.plot([x, x], [0, n], color="#39424D", lw=1.3, zorder=4)
    for label, s, e in SECTIONS:
        ax.plot([s + 0.10, e - 0.10], [-0.30, -0.30], color="#6A7480",
                lw=1.0, zorder=4, clip_on=False)
        ax.text((s + e) / 2, -0.62, label, ha="center", va="center",
                fontsize=7.2, color="#39424D")
    ax.text(19.32, -0.62, "\u03a3", ha="left", va="center",
            fontsize=7.6, color="#39424D", clip_on=False)

    ax.text(1.0, 1.05, "empty cell = full credit", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=7.2, color=MUTE)

    ax.add_patch(Rectangle((0, 0), 19, n, fill=False,
                           edgecolor="#39424D", lw=1.0, zorder=5))
    ax.set_xlim(-0.02, 19.6)
    ax.set_ylim(n, -1.15)
    ax.set_xticks([c + 0.5 for c in range(19)])
    ax.set_xticklabels([f"Q{c + 1}" for c in range(19)], fontsize=6.8)
    ax.set_yticks([])
    ax.tick_params(length=0)
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.set_title("Per-item point loss", **TITLE_KW)


def draw_time(ax: plt.Axes) -> None:
    for m in MODELS:
        ax.scatter([m["duration_s"] / 60.0], [sum(m["items"])], s=34,
                   color=m["color"], edgecolor="white", linewidth=0.8,
                   alpha=0.95, zorder=3)

    ax.axhline(150, color="#C3CBD4", lw=0.8, dashes=(4, 3), zorder=1)
    ax.set_xlim(-1.2, 36)
    ax.set_ylim(97, 157)
    ax.set_xticks([0, 10, 20, 30])
    ax.set_yticks([100, 120, 140, 150])
    ax.tick_params(labelsize=7.2, length=3, width=0.7, colors=MUTE)
    ax.grid(color=FAINT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.set_xlabel("wall-clock time (min)", fontsize=7.6, color=MUTE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#B9C2CC")
        ax.spines[side].set_linewidth(0.7)
    ax.set_title("Score vs. wall-clock time", **TITLE_KW)


def build_figure(paper_mode: bool = False) -> plt.Figure:
    models = sorted_models()
    n = len(models)
    run_id = str(RUN_META.get("run_id", ""))
    fig = plt.figure(figsize=(13.4, 8.9))

    if not paper_mode:
        fig.text(0.058, 0.972,
                 "Closed-Book AI Agent Evaluation \u2014 "
                 "2026 NCEE Mathematics, Paper I",
                 fontsize=15.5, fontweight="bold", color=INK, va="top")
        fig.text(0.058, 0.934,
                 f"{n} agents \u00b7 19 items \u00b7 150 points \u00b7 {run_id}",
                 fontsize=9.5, color=SLATE, va="top")
        fig.add_artist(Line2D([0.058, 0.975], [0.916, 0.916],
                              transform=fig.transFigure, color=RULE, lw=0.9))

    ax_a = fig.add_axes([0.155, 0.570, 0.460, 0.300])
    ax_b = fig.add_axes([0.715, 0.570, 0.260, 0.300])
    ax_c = fig.add_axes([0.155, 0.095, 0.460, 0.360])
    ax_d = fig.add_axes([0.715, 0.095, 0.260, 0.360])

    draw_ranking(ax_a, models)
    draw_family(ax_b)
    draw_loss_matrix(ax_c, models)
    draw_time(ax_d)

    panel_letter(fig, ax_a, "a", LETTER_X_LEFT)
    panel_letter(fig, ax_b, "b", LETTER_X_RIGHT)
    panel_letter(fig, ax_c, "c", LETTER_X_LEFT)
    panel_letter(fig, ax_d, "d", LETTER_X_RIGHT)

    if not paper_mode:
        fig.add_artist(Line2D([0.058, 0.975], [0.048, 0.048],
                              transform=fig.transFigure, color=RULE, lw=0.9))
        fig.text(0.058, 0.026,
                 "One closed-book submission per agent · provider defaults · "
                 "reasoning effort = medium where selectable · "
                 "errata-verified key · multiple-choice 6/3/0 · "
                 "equivalent forms accepted",
                 fontsize=7.4, color="#75808C", va="center")
        fig.text(0.975, 0.026, "ncee-2026-math-agent-eval",
                 fontsize=7.4, color="#A6AFB9", va="center", ha="right")
    return fig


def write_csv(path: Path) -> None:
    models = sorted_models()
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["rank", "model", "slug", "family", "vendor", "total",
                    "single_choice", "multiple_choice", "fill_in",
                    "free_response", "duration", "duration_seconds"])
        for i, m in enumerate(models, 1):
            sg, mu, fi, fr = section_sums(m["items"])
            w.writerow([i, m["name"], m["slug"], m["family"],
                        FAMILY_VENDOR[m["family"]], sum(m["items"]),
                        sg, mu, fi, fr,
                        fmt_mmss(m["duration_s"]), m["duration_s"]])


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot ncee-2026-math-agent-eval results")
    parser.add_argument("--run", default="2026-06-10", help="run_id under results/")
    parser.add_argument("--paper", action="store_true",
                        help="manuscript variant: strip header/footer, tight bbox")
    args = parser.parse_args()

    setup_style()
    out_dir = load_run(args.run)
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = FIG_STEM + ("_paper" if args.paper else "")
    save_kw = dict(bbox_inches="tight", pad_inches=0.08) if args.paper else {}
    fig = build_figure(paper_mode=args.paper)
    png = out_dir / f"{stem}.png"
    fig.savefig(png, dpi=300, **save_kw)
    try:
        fig.savefig(out_dir / f"{stem}.svg", **save_kw)
    except Exception as exc:
        print(f"[warn] svg export skipped: {exc}")
    plt.close(fig)

    if not args.paper:
        write_csv(out_dir / "scores.csv")
        print(f"[ok] {out_dir / 'scores.csv'}")
    print(f"[ok] {png}")
    print(f"[ok] {out_dir / (stem + '.svg')}")


if __name__ == "__main__":
    main()

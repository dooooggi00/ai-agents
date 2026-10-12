"""读取真实的 results.csv，生成 LaTeX 表格、参数文件与静态图像。

本步骤不重新投针、不编造结果；所有输出都来自同一份 CSV，写入当前工作目录。
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")  # 无显示环境下也能保存图片
import matplotlib.pyplot as plt  # noqa: E402

CSV_NAME = "results.csv"
TABLE_NAME = "results-table.tex"
PARAMS_NAME = "results-params.tex"
FIGURE_NAME = "results.png"

FIELDS: tuple[str, ...] = (
    "seed",
    "n",
    "crossings",
    "pi_estimate",
    "needle_length",
    "line_spacing",
)


def load_rows(path: str | Path = CSV_NAME) -> list[dict]:
    """读取 CSV；找不到或为空时给出明确错误。"""
    src = Path(path)
    if not src.exists():
        raise SystemExit(f"找不到 {src}；请先运行 experiment.py 生成结果。")
    with src.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != list(FIELDS):
            raise SystemExit(
                f"{src} 表头与预期不符：{reader.fieldnames}，应为 {list(FIELDS)}"
            )
        rows = [
            {
                "seed": int(row["seed"]),
                "n": int(row["n"]),
                "crossings": int(row["crossings"]),
                "pi_estimate": float(row["pi_estimate"]),
                "needle_length": float(row["needle_length"]),
                "line_spacing": float(row["line_spacing"]),
            }
            for row in reader
        ]
    if not rows:
        raise SystemExit(f"{src} 没有数据行；请先运行 experiment.py。")
    return rows


def write_table(rows: Sequence[dict], path: str | Path = TABLE_NAME) -> Path:
    """生成可直接 \\input 的 LaTeX 表格（booktabs）。"""
    lines = [
        "% 由 render_results.py 依据 results.csv 自动生成，请勿手工编辑。",
        r"\begin{tabular}{rrr}",
        r"\toprule",
        r"$N$ & $K$ & $\widehat{\pi}$ \\",
        r"\midrule",
    ]
    for row in rows:
        lines.append(
            f"{row['n']:,} & {row['crossings']:,} & {row['pi_estimate']:.5f} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    out = Path(path)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def write_params(rows: Sequence[dict], path: str | Path = PARAMS_NAME) -> Path:
    """生成展示实际 seed、各组 n、针长与线间距的短文字。"""
    seeds = sorted({row["seed"] for row in rows})
    sizes = "、".join(f"{row['n']:,}" for row in rows)
    length = rows[0]["needle_length"]
    spacing = rows[0]["line_spacing"]
    seed_text = "、".join(str(seed) for seed in seeds)
    text = (
        f"本轮实验的实际随机种子为 {seed_text}，投针数 $N$ 分别为 {sizes}，"
        f"针长 $L={length:g}$，平行线间距 $d={spacing:g}$。"
    )
    out = Path(path)
    out.write_text(text + "\n", encoding="utf-8")
    return out


def write_figure(rows: Sequence[dict], path: str | Path = FIGURE_NAME) -> Path:
    """生成展示不同 n 对应估计值的静态图，并画一条真实 pi 参考线。"""
    ns = [row["n"] for row in rows]
    estimates = [row["pi_estimate"] for row in rows]

    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.plot(ns, estimates, marker="o", color="#1f77b4", label="estimate")
    ax.axhline(math.pi, color="#d62728", linestyle="--", label="true pi")
    for x, y in zip(ns, estimates):
        ax.annotate(
            f"{y:.3f}",
            (x, y),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=8,
        )
    ax.set_xscale("log")
    ax.set_xlabel("N (needles)")
    ax.set_ylabel("pi estimate")
    ax.set_title("Buffon's needle: pi estimate vs N")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = Path(path)
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def main(argv: Sequence[str] | None = None) -> int:
    rows = load_rows(CSV_NAME)
    table = write_table(rows)
    params = write_params(rows)
    figure = write_figure(rows)
    print(f"已读取 {Path(CSV_NAME).resolve()}，共 {len(rows)} 行", flush=True)
    for produced in (table, params, figure):
        print(f"已生成 {produced.resolve()}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

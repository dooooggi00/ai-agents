"""蒲丰投针实验：真实模拟、估计圆周率并输出 results.csv。

作为模块被 import 时不启动实验、不写文件；只有直接运行本文件时才会执行三组默认实验。
"""

from __future__ import annotations

import argparse
import csv
import math
import random
from pathlib import Path
from typing import Iterable, Sequence

DEFAULT_SEED = 42
DEFAULT_LENGTH = 0.5
DEFAULT_SPACING = 1.0
DEFAULT_SIZES: tuple[int, ...] = (1000, 10000, 100000)

# CSV 表头，顺序即列顺序。
FIELDS: tuple[str, ...] = (
    "seed",
    "n",
    "crossings",
    "pi_estimate",
    "needle_length",
    "line_spacing",
)


def _is_int(value: object) -> bool:
    """True 只对真正的整数为真（bool 不算）。"""
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_geometry(length: float, spacing: float) -> None:
    """校验几何参数：0 < length <= spacing，且 spacing > 0。"""
    if spacing <= 0:
        raise ValueError(f"线间距 spacing 必须为正，收到 {spacing!r}")
    if not (0 < length <= spacing):
        raise ValueError(
            f"针长 length 必须满足 0 < length <= spacing，"
            f"收到 length={length!r}, spacing={spacing!r}"
        )


def crosses_line(
    distance: float,
    angle: float,
    length: float = DEFAULT_LENGTH,
    spacing: float = DEFAULT_SPACING,
) -> bool:
    """判断一根针是否与平行线相交（针尖恰好触线也算相交）。

    输入范围：0 <= distance <= spacing/2，0 <= angle <= pi/2。
    几何参数或取样值不合法时抛 ValueError，不静默修正。
    """
    _validate_geometry(length, spacing)
    if not (0 <= distance <= spacing / 2):
        raise ValueError(
            f"distance 必须满足 0 <= distance <= spacing/2 = {spacing / 2!r}，"
            f"收到 {distance!r}"
        )
    if not (0 <= angle <= math.pi / 2):
        raise ValueError(f"angle 必须满足 0 <= angle <= pi/2，收到 {angle!r}")
    return distance <= (length / 2) * math.sin(angle)


def estimate_pi(
    n: int,
    crossings: int,
    length: float = DEFAULT_LENGTH,
    spacing: float = DEFAULT_SPACING,
) -> float:
    """由投针数与相交数估计圆周率：2 * length * n / (spacing * crossings)。

    n 为正整数；crossings 为整数且 0 <= crossings <= n。
    crossings=0 时该式无定义，抛 ValueError。
    """
    _validate_geometry(length, spacing)
    if not _is_int(n) or n <= 0:
        raise ValueError(f"n 必须是正整数，收到 {n!r}")
    if not _is_int(crossings) or crossings < 0 or crossings > n:
        raise ValueError(
            f"crossings 必须是整数且满足 0 <= crossings <= n={n}，收到 {crossings!r}"
        )
    if crossings == 0:
        raise ValueError("crossings=0 时无法用该公式估计圆周率")
    return 2 * length * n / (spacing * crossings)


def simulate(
    n: int,
    seed: int = DEFAULT_SEED,
    length: float = DEFAULT_LENGTH,
    spacing: float = DEFAULT_SPACING,
) -> dict:
    """模拟 n 次投针，返回本次实验的实际参数与估计值。

    每次调用在循环外只用 seed 初始化随机数生成器一次；循环内持续取样，
    不在每次投针时重设 seed。
    """
    _validate_geometry(length, spacing)
    if not _is_int(n) or n <= 0:
        raise ValueError(f"n 必须是正整数，收到 {n!r}")
    if not _is_int(seed):
        raise ValueError(f"seed 必须是整数，收到 {seed!r}")

    rng = random.Random(seed)
    half_spacing = spacing / 2
    half_angle = math.pi / 2

    crossings = 0
    for _ in range(n):
        distance = rng.uniform(0.0, half_spacing)
        angle = rng.uniform(0.0, half_angle)
        if crosses_line(distance, angle, length, spacing):
            crossings += 1

    if crossings == 0:
        raise ValueError(
            f"{n} 次投针没有一次相交，无法给出有效估计值（seed={seed}）"
        )

    return {
        "seed": seed,
        "n": n,
        "crossings": crossings,
        "pi_estimate": estimate_pi(n, crossings, length, spacing),
        "needle_length": length,
        "line_spacing": spacing,
    }


def _resolve_sizes(extra: Sequence[int] | None) -> tuple[int, ...]:
    """默认保留三组；通过 --n 追加更大的 n，去重后按从小到大排序。"""
    sizes: list[int] = list(DEFAULT_SIZES)
    if extra:
        sizes.extend(extra)
    return tuple(sorted(dict.fromkeys(sizes)))


def run(
    sizes: Iterable[int],
    seed: int = DEFAULT_SEED,
    length: float = DEFAULT_LENGTH,
    spacing: float = DEFAULT_SPACING,
) -> list[dict]:
    """对每组 n 独立初始化一次 RNG，返回每行结果。"""
    rows: list[dict] = []
    for n in sizes:
        result = simulate(n, seed=seed, length=length, spacing=spacing)
        rows.append(result)
        print(
            f"n={n:>7}  seed={seed}  crossings={result['crossings']:>7}  "
            f"pi_estimate={result['pi_estimate']:.5f}",
            flush=True,
        )
    return rows


def write_csv(rows: Iterable[dict], path: str | Path = "results.csv") -> Path:
    """把结果写入 CSV，表头与字段顺序与 FIELDS 一致。"""
    out = Path(path)
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(FIELDS))
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in FIELDS})
    return out


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="蒲丰投针模拟，输出 results.csv（写入当前工作目录）。"
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="随机种子")
    parser.add_argument(
        "--n",
        type=int,
        action="append",
        dest="sizes",
        metavar="N",
        help="在默认三组之外追加投针数，可重复使用",
    )
    parser.add_argument("--length", type=float, default=DEFAULT_LENGTH, help="针长")
    parser.add_argument("--spacing", type=float, default=DEFAULT_SPACING, help="线间距")
    parser.add_argument("--output", default="results.csv", help="输出 CSV 路径")
    args = parser.parse_args(argv)

    sizes = _resolve_sizes(args.sizes)
    rows = run(sizes, seed=args.seed, length=args.length, spacing=args.spacing)
    path = write_csv(rows, args.output)
    print(f"已写入 {path.resolve()}（共 {len(rows)} 行）", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

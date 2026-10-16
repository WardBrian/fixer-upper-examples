# This is one solution to the refactoring challenge without altering the interface.
#
# However, note that this interface really ought to be changed! The new
# compute_1d_stat function is easier to reason about separately from
# linear_fit, but even still there is the issue of the return type being different between
# the different cases, which will continue to annoy users


from collections import Counter
import statistics

from typing import Literal, Callable, Mapping

T_legacy_1d_modes = Literal[
    "sum", "mean", "median", "mode", "variance", "range", "stdev"
]
T_legacy_modes = Literal[T_legacy_1d_modes, "fit"]

T_1d_stats = Literal[T_legacy_1d_modes, "sample_variance", "sample_stdev"]


STATS: Mapping[T_1d_stats, Callable[[list[float]], float | tuple[float, float]]] = {
    "mode": lambda d: Counter(d).most_common(1)[0],
    "range": lambda d: (min(d), max(d)),
    "mean": statistics.mean,
    "median": statistics.median,
    "variance": statistics.pvariance,
    "sample_variance": statistics.variance,
    "stdev": statistics.pstdev,
    "sample_stdev": statistics.stdev,
    "sum": sum,
}


def compute_1d_stat(data: list[float], stat: T_1d_stats) -> float | tuple[float, float]:
    return STATS[stat](data)


def map_legacy_stat_name(stat: T_1d_stats, is_sample: bool) -> T_1d_stats:
    if is_sample and stat in ("variance", "stdev"):
        return "sample_" + stat
    return stat


def linear_fit(data: list[list[float]]) -> tuple[float, float]:
    x = [point[0] for point in data]
    y = [point[1] for point in data]

    x_mean = statistics.mean(x)
    y_mean = statistics.mean(y)
    x_xi_diff = [(item - x_mean) for item in x]
    x_xi_diff_sq = [item**2 for item in x_xi_diff]
    sum_sq = sum(x_xi_diff_sq)
    y_yi_diff = [(item - y_mean) for item in y]
    slope_numerator = sum(x_val * y_val for (x_val, y_val) in zip(x_xi_diff, y_yi_diff))

    slope = slope_numerator / sum_sq

    sum_x_sq = sum(item**2 for item in x)
    sum_xy = sum(x_val * y_val for (x_val, y_val) in zip(x, y))
    sum_y = sum(y)
    sum_x = sum(x)
    n = len(x)

    intercept = (sum_y * sum_x_sq - sum_x * sum_xy) / (n * sum_x_sq - (sum_x) ** 2)

    return (intercept, slope)


def summarize(
    data: list[float] | list[list[float]],
    mode: T_legacy_modes,
    is_sample: bool = True,
) -> float | tuple[float, float]:
    if mode == "fit":
        return linear_fit(data)

    if data and isinstance(data[0], list):
        raise ValueError("2-d data supplied to 1-d statistic")
    stat = map_legacy_stat_name(mode, is_sample)
    return compute_1d_stat(data, stat)

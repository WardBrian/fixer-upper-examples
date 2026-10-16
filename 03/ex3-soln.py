# Our solution to exercise 2 made some choices that were correct for the goal we
# had, but may not be any longer.
# For example, using standard library routines is generally preferred, but if we
# care about maximizing the shared work in this new routine, using them hides the
# formula in such a way that makes this difficult, and they may not have the required
# helpers

# Here, we end up taking an alternative approach that uses a class to manage
# some mutable state to store partial results

from functools import cached_property
from collections import Counter
from math import sqrt
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


class OneDStats:
    data: list[float]
    n: int

    def __init__(self, data: list[float]):
        self.data = data
        self.n = len(data)

    @cached_property
    def sum(self) -> float:
        return sum(self.data)

    @cached_property
    def mean(self) -> float:
        return self.sum / len(self.data)

    @cached_property
    def median(self) -> float:
        return statistics.median(self.data)

    @cached_property
    def squared_distance_from_mean(self) -> list[float]:
        return [(v - self.mean) ** 2 for v in self.data]

    @cached_property
    def total_variation(self) -> float:
        return sum(self.squared_distance_from_mean)

    @cached_property
    def variance(self) -> float:
        # the second argument of the standard library's variance function
        # lets us pass a previously computed mean, but we also want the squared
        # distances elsewhere, so let's just re-implement it
        return self.total_variation / self.n

    @cached_property
    def sample_variance(self) -> float:
        return self.total_variation / (self.n - 1)

    # the remainder of these aren't currently precursors for anything,
    # so we could leave out the caching if we wanted to

    @cached_property
    def stdev(self) -> float:
        return sqrt(self.variance)

    @cached_property
    def sample_stdev(self) -> float:
        return sqrt(self.sample_variance)

    @cached_property
    def range(self) -> tuple[float, float]:
        return min(self.data), max(self.data)

    @cached_property
    def counts(self) -> Counter:
        return Counter(self.data)

    @cached_property
    def mode(self) -> tuple[float, int]:
        return self.counts.most_common(1)[0]


def map_legacy_stat_name(stat: T_1d_stats, is_sample: bool) -> T_1d_stats:
    if is_sample and stat in ("variance", "stdev"):
        return "sample_" + stat
    return stat


def linear_fit(x: OneDStats, y: OneDStats) -> tuple[float, float]:
    x_mean = x.mean
    y_mean = y.mean

    y_yi_diff = ((item - y_mean) for item in y.data)
    x_xi_diff = ((item - x_mean) for item in x.data)
    slope_numerator = sum(x_val * y_val for (x_val, y_val) in zip(x_xi_diff, y_yi_diff))

    slope = slope_numerator / x.total_variation

    sum_x_sq = sum(item**2 for item in x.data)
    sum_xy = sum(x_val * y_val for (x_val, y_val) in zip(x.data, y.data))
    sum_y = y.sum
    sum_x = x.sum
    n = x.n

    intercept = (sum_y * sum_x_sq - sum_x * sum_xy) / (n * sum_x_sq - (sum_x) ** 2)

    return (intercept, slope)


def summarize(
    data: list[float] | list[list[float]],
    mode: T_legacy_modes,
    is_sample: bool = True,
) -> float | tuple[float, float]:
    if mode == "fit":
        x = OneDStats([point[0] for point in data])
        y = OneDStats([point[1] for point in data])
        return linear_fit(x, y)

    if data and isinstance(data[0], list):
        raise ValueError("2-d data supplied to 1-d statistic")
    stat = map_legacy_stat_name(mode, is_sample)
    return getattr(OneDStats(data), stat)


# new interface

T_stats = Literal[T_1d_stats, "fit"]


def get_stats(
    data: list[float] | list[list[float]], stats: list[T_stats]
) -> dict[T_stats, float | tuple[float, float]]:  # todo TypedDict?
    # decision: if data is 2d, we want all the 1d stats computed on the 'y's
    x, y = _standardize_structure(data)

    result = {}
    for requested in stats:
        if requested == "fit":
            if x is None:
                raise ValueError("requested 'fit' on 1-d data")
            result["fit"] = linear_fit(x, y)
        else:
            result[requested] = getattr(y, requested)

    return result


def _standardize_structure(
    data: list[float] | list[list[float]],
) -> tuple[OneDStats | None, OneDStats]:
    if type(data[0]) == float:
        return (None, OneDStats(data))
    series_1 = []
    series_2 = []
    for d in data:
        if type(d) != list:
            raise ValueError("Data list expected to be two data series.")
        if len(d) != 2:
            raise ValueError("Data series may only contain two elements per point.")
        if type(d[0]) != float or type(d[1]) != float:
            raise ValueError("Data series must comprise two floats per point.")
        series_1.append(d[0])
        series_2.append(d[1])
    return (OneDStats(series_1), OneDStats(series_2))

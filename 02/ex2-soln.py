from typing import Literal, cast
from math import sqrt

# This is one solution to the refactoring challenge of adding outlier removal without
# altering the interface.
#
# However, note that this interface really ought to be changed! We can offer most of
# the desired values directly from a (more robust) Stats class.
#
# Refactoring is always an opportunity for re-designing and re-negotiating the contract
# between the code and its users. In this case, the code would be better if we made the
# decision to push back on the requirement.
#
# As is, we've tried to patch around it by making the assumptions more explicit,
# removing conditions from logic, centralizing most operations in a class which is better
# able to make assumptions about its data, and splitting other operations into their
# own separate functions.


T_supported_modes = Literal['sum', 'mean', 'median', 'mode', 'variance', 'fit', 'range']


class Stats():
    max: float
    min: float
    len: int
    mean: float
    mode: float
    mode_count: int
    total: float
    data: list[float]


    def __init__(self, data: list[float]):
        if (len(data) == 0):
            raise ValueError("Attempt to summarize zero-length list.")
        self.data = data
        self.len = len(data)
        self.max = data[0]
        self.min = data[0]
        self.total = 0
        counts = {}
        for item in data:
            if item not in counts:
                counts[item] = 0
            counts[item] += 1
            if item > self.max:
                self.max = item
            if item < self.min:
                self.min = item
            self.total += item
        self.mean = self.total / self.len

        self.max_count = 0
        self.the_mode = data[0]
        for (k, v) in counts.items():
            if v > self.max_count:
                self.max_count = v
                self.the_mode = k


    def mean_difference(self):
        return [(item - self.mean) for item in self.data]


    def mean_difference_squared(self):
        return [(item - self.mean) ** 2 for item in self.data]


    def variance(self, is_sample: bool = True):
        sq_diff = self.mean_difference_squared()
        sum_sq_diff = sum(sq_diff)
        denom = self.len - 1 if is_sample else self.len
        if denom == 0:
            raise ValueError("Cannot perform sample variance on a sample size of 1.")
        return sum_sq_diff / denom


    def median(self):
        data_sorted = sorted(self.data)
        half = self.len // 2
        if self.len % 2 == 1:
            return data_sorted[half]
        return (data_sorted[half] + data_sorted[half - 1]) / 2


def summarize(
    data: list[float] | list[list[float]],
    mode: T_supported_modes,
    is_sample: bool = True,
) -> float | tuple[float, float]:
    (x, y) = _standardize_structure(data)
    (x_stats, y_stats) = _remove_outliers(x, y)

    if (mode == 'fit'):
        if (y_stats is None):
            raise ValueError("Best-fit summary requires a series of 2d points.")
        return _handle_fit(x_stats, y_stats)

    if (y is not None):
        raise ValueError("Points are only accepted for best-fit summary.")

    if mode == 'sum':
        return x_stats.total
    if mode == 'mean':
        return x_stats.mean
    if mode == 'median':
        return x_stats.median()
    if mode == 'mode':
        return (x_stats.mode, x_stats.max_count)
    if mode == 'variance':
        return x_stats.variance(is_sample)
    if mode == 'range':
        return (x_stats.min, x_stats.max)

    raise NotImplementedError("Unreachable.")


def _remove_outliers(x: list[float], y: list[float] | None = None) -> tuple[Stats, Stats | None]:
    """Exact definition of outliers can vary a lot; I'm using one that depends on variance.

    Args:
        x (list[float]): A data series
        y (list[float] | None, optional): An optional second data series, representing
            the values of some dependent variable whose independent values are in x

    Returns:
        tuple[Stats, Stats | None]: A tuple with one guaranteed Stats object and one that will
            be populated IFF y_stats is not None.
    """
    x_stats = Stats(x)
    (xmax, xmin) = _get_sd_range(x_stats)
    bad_indices = set([i for i, v in enumerate(x) if v > xmax or v < xmin])
    also_bad = []
    if y is not None:
        y_stats = Stats(y)
        (ymax, ymin) = _get_sd_range(y_stats)
        also_bad = [i for i, v in enumerate(y) if v > ymax or v < ymin]
        bad_indices = bad_indices.union(also_bad)
        cleaned_y = [v for i, v in enumerate(y) if i not in bad_indices]
    
    cleaned_x = [v for i, v in enumerate(x) if i not in bad_indices]

    return (Stats(cleaned_x), Stats(cleaned_y) if y is not None else None)


def _get_sd_range(x: Stats) -> tuple[float, float]:
    var = x.variance(False)
    stddev = sqrt(var)
    return (x.mean - 2.5*stddev, x.mean + 2.5*stddev)


def _standardize_structure(data: list[float] | list[list[float]]) -> tuple[list[float], list[float] | None]:
    if type(data[0]) == float:
        return (cast(list[float], data), None)
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
    return (series_1, series_2)


def _handle_fit(x_stats: Stats, y_stats: Stats) -> tuple[float, float]:
    x_xi_diff = x_stats.mean_difference()
    y_yi_diff = y_stats.mean_difference()
    slope_numerator = sum([x_val * y_val for (x_val, y_val) in zip(x_xi_diff, y_yi_diff)])
    slope = slope_numerator / sum(x_stats.mean_difference_squared())

    sum_x_sq = sum([item ** 2 for item in x_stats.data])
    sum_xy = sum([x_val * y_val for (x_val, y_val) in zip(x_stats.data, y_stats.data)])
    intercept = (y_stats.total * sum_x_sq - x_stats.total * sum_xy) / (x_stats.len * sum_x_sq - (x_stats.total) ** 2)

    return (intercept, slope)

# TASK:
# The following routine has grown unruly over time. We'd like to
# both make it more interpretable and add support for an additional
# mode, "stdev", which computes standard deviations

def summarize(
    data: list[float] | list[list[float]],
    mode,
    is_sample: bool = True,
) -> float | tuple[float, float]:
    if mode == 'fit':
        x = [point[0] for point in data]
        y = [point[1] for point in data]
    else:
        x = data

    if mode == 'mode':
        counts = {}
        for item in x:
            if item in counts:
                counts[item] += 1
            else:
                counts[item] = 1

    n = len(data)
    total = sum(x)

    if mode == 'mean' or mode == 'variance':
        mean = total / n

    if mode == 'median':
        x = sorted(x)
        if n % 2 == 1:
            half = n // 2
            median = x[half]
        else:
            half = n // 2
            median = (x[half] + x[half - 1]) / 2

    if mode == 'variance' or mode == 'fit':
        x_xi_diff = [(item - mean) for item in x]
        x_xi_diff_sq = [item ** 2  for item in x_xi_diff]
        sum_sq = sum(x_xi_diff_sq)

    if mode == 'fit':
        y_mean = sum(y) / n
        y_yi_diff = [(item - y_mean) for item in y]
        slope_numerator = 0
        for i in range(len(x_xi_diff)):
            slope_numerator += y_yi_diff[i] * x_xi_diff[i]
        slope = slope_numerator / sum_sq

        sum_x_sq = sum([item ** 2 for item in x])
        sum_y = sum(y)
        sum_xy = 0
        for i in range(len(x)):
            sum_xy += x[i] * y[i]
        intercept = (sum_y * sum_x_sq - total * sum_xy) / (n * sum_x_sq - (total)**2)

    if mode == 'range':
        max = x[0]
        min = x[0]
        for i in range(len(x)):
            if x[i] > max:
                max = x[i]
            if x[i] < min:
                min = x[i]

    if mode == 'sum':
        return total
    if mode == 'mean':
        return mean
    if mode == 'median':
        return median
    if mode == 'mode':
        max_count = 0
        the_mode = None
        for (k, v) in counts.items():
            if v > max_count:
                max_count = v
                the_mode = k
        return (the_mode, max_count)    # type: ignore
    if mode == 'variance':
        if is_sample:
            return sum_sq / (n - 1)
        return sum_sq / n
    if mode == 'fit':
        return (intercept, slope)
    if mode == 'range':
        return (min, max)

    return None

"""Provide some metrics to applied to data"""
import numpy as np
import pandas as pd
from itertools import combinations

from fast_plotting.data import datatypes
from fast_plotting.logger import get_logger
from fast_plotting.io import dump_json

METRICS_LOGGER = get_logger("Metrics")

def integral(data_wrapper):
    repr, dim = data_wrapper.preferred_representation()
    if repr != datatypes.DATA_REPRESENTATION_HISTOGRAM:
        return None
    values, bin_edges = data_wrapper.get_as_histogram()
    if dim == datatypes.DATA_DIMESNION_1D:
        be = bin_edges[0]
        weights = be[1:] - be[:-1]
        # take 0'th entry cause the return value is a 1D numpy according to input shape and return of np.dot
        return np.dot(values.flatten(), weights.flatten())
    be_x = bin_edges[0][1:] - bin_edges[0][:-1]
    be_y = bin_edges[1][1:] - bin_edges[1][:-1]
    weights = np.outer(be_x, be_y).flatten()
    # take 0'th entry cause the return value is a 1D numpy according to input shape and return of np.dot
    return np.dot(values.flatten(), weights)

def _norm(data_wrapper):
    if not data_wrapper:
        return None
    repr, dim = data_wrapper.preferred_representation()
    if repr != datatypes.DATA_REPRESENTATION_HISTOGRAM:
        return None
    values, _ = data_wrapper.get_as_histogram()
    return values / integral(data_wrapper)

def norm(data_wrapper):
    return _norm(data_wrapper)

# def rms(data_wrapper):
#     repr, dim = data_wrapper.preferred_representation()
#     if repr != datatypes.DATA_REPRESENTATION_HISTOGRAM:
#         return None
#     values, bin_edges = data_wrapper.get_as_histogram()
#     x, y, z = data_wrapper.get_as_scatter()
#     if dim == datatypes.DATA_DIMESNION_1D:
#         try:
#             be = bin_edges[0]
#             weights = (be[1:] - be[:-1]) * y
#             average = np.average(x, weights=weights)
#             return np.average((x-average)**2, weights=weights)
#         except ZeroDivisionError:
#             METRICS_LOGGER.warning("Division by 0")
#             return None

    # try:
    #     be_x = bin_edges[0][1:] - bin_edges[0][:-1]
    #     be_y = bin_edges[1][1:] - bin_edges[1][:-1]
    #
    #     values_x = np.dot(values, be_y)
    #     values_y = np.dot(be_x, values)
    #
    #     average_x = np.average(, weights=z)
    #     average_y = np.average(y, weights=z)
    #     return np.average((x-average_x)**2, weights=z), np.average((y-average_y)**2, weights=z)
    # except ZeroDivisionError:
    #     METRICS_LOGGER.warning("Division by 0")
    #     return None, None
    # return None

def _chi2_numpy(norm_1, norm_2):
    try:
        num = (norm_1 - norm_2)**2
        den = norm_1 + norm_2
        ind = np.nonzero(den)
        num = num[ind]
        den = den[ind]
        if not len(num):
            METRICS_LOGGER.warning("Empty data")
            return None
        return np.sum(num / den) / 2
    except ZeroDivisionError:
        METRICS_LOGGER.warning("Division by 0")
        return None

def _chi2(data_wrapper_1, data_wrapper_2):
    norm_1, norm_2 = (_norm(data_wrapper_1), norm(data_wrapper_2))
    return _chi2_numpy(norm_1, norm_2)

def chi2(data_wrapper_1, data_wrapper_2):
    if data_wrapper_1.get_shape() != data_wrapper_2.get_shape():
        METRICS_LOGGER.warning("Different shapes of data")
        return None
    repr, dim = data_wrapper_1.preferred_representation()
    if repr != datatypes.DATA_REPRESENTATION_HISTOGRAM:
        return None
    return _chi2(data_wrapper_1, data_wrapper_2)

def _compare_single_metric(func, data_wrapper_1, data_wrapper_2):
    res1, res2 = (func(data_wrapper_1), func(data_wrapper_2))
    if res1 is None or res2 is None:
        return None
    if res1 == 0.0:
        METRICS_LOGGER.warning("Comparison data integral is 0")
        return np.inf
    return res2 / res1

def _compare_metric(func, data_wrapper_1, data_wrapper_2):
    """forward to correct function

    deciide how func should be called. Either direct comparison
    of same maetric on both data or metric which depends on both at the same time

    """
    n_pos_args = func.__code__.co_argcount
    if n_pos_args == 1:
        return _compare_single_metric(func, data_wrapper_1, data_wrapper_2)
    return func(data_wrapper_1, data_wrapper_2)

def _single_metric(func, data_wrapper):
    """forward to correct function

    deciide how func should be called. Either direct comparison
    of same maetric on both data or metric which depends on both at the same time

    """
    n_pos_args = func.__code__.co_argcount
    if n_pos_args != 1:
        return None
    return func(data_wrapper)

METRICS = {"chi2": chi2,
           "integral": integral}

def compute_metrics(data_wrappers, metrics_names, compare=False, *, add_to_metrics=None):
    if len(data_wrappers) < 2 and compare:
        METRICS_LOGGER.warning("Only one batch of data was passed, nothing to compare")
        return None

    collect_all = {} if add_to_metrics is None else add_to_metrics
    if not compare:
        for dw in data_wrappers:
            collect = {}
            for mn in metrics_names:
                if mn not in METRICS:
                    METRICS_LOGGER.warning("Metric name %s unknown, skip...", mn)
                    continue
                collect[mn] = _single_metric(METRICS[mn], dw)
            collect_all[dw.name] = collect
        return collect_all

    for dw in combinations(data_wrappers, 2):
        collect = {}
        for mn in metrics_names:
            if mn not in METRICS:
                METRICS_LOGGER.warning("Metric name %s unknown, skip...", mn)
                continue
            collect[mn] = _compare_metric(METRICS[mn], dw[0], dw[1])
        collect_all[f"{dw[0].name}__VS__{dw[1].name}"] = collect
    return collect_all

def print_metrics(metrics, *, format="terminal"):

    if not metrics:
        METRICS_LOGGER.warning("Metrics are empty")
        return

    if format == "json":
        dump_json(metrics, "metrics.json")

    metric_name_to_col = {}
    metric_col_to_name = []
    for name, values in metrics.items():
        for m_name, m_value in values.items():
            if m_name in metric_name_to_col:
                continue
            metric_name_to_col[m_name] = len(metric_name_to_col)
            metric_col_to_name.append(m_name)

    if format == "heatmap":
        # col_names = ["data", "metric", "value"]
        # lists = [[] * len(metrics) * len(metric_col_to_name) for _ in range(3)]
        # for name, values in metrics.items():
        #     for m_name, m_value in values.items():
        #         lists[0].append(name)
        #         lists[1].append(m_name)
        #         lists[2].append(m_value)
        # df = pd.DataFrame({cn[i]: lists[i] for i in range(3)})
        METRICS_LOGGER.warning("Heatmap not yet implemented")

    if format == "terminal":
        METRICS_LOGGER.info("Printing metrics")
        #print(metric_col_to_name)
        col_widths = [0] * (len(metric_col_to_name) + 1)
        # first column is the data name, following columnsa are the metrics values
        top_line = [""] + metric_col_to_name
        for i, tl in enumerate(top_line):
            col_widths[i] = max(col_widths[i], len(tl))
        lines = [top_line]
        for name, values in metrics.items():
            line = [name] + [""] * len(metric_col_to_name)
            for m_name, m_value in values.items():
                line[metric_name_to_col[m_name] + 1] = m_value
            for  i, tl in enumerate(line):
                col_widths[i] = max(col_widths[i], len(str(line[i])))
            lines.append(line)

        # now we have it and can construct the output
        for line in lines:
            for i, _ in enumerate(line):
                line[i] = f"{line[i] : <{col_widths[i]}}"

        lines = [" | ".join(line) for line in lines]
        # add 4 for leading "| " and trailing " |"
        length = len(lines[0]) + 4

        line_sep = "-" * length + "\n"

        to_print = "\n"
        for l in lines:
            to_print += line_sep
            to_print += "| " + l + " |\n"
        to_print += line_sep
        print(to_print)

"""Provide some metrics to applied to data"""
import numpy as np

from fast_plotting.data import datatypes
from fast_plotting.logger import get_logger

METRICS_LOGGER = get_logger("Metrics")

def integral(data_wrapper):
    repr, dim = data_wrapper.preferred_representation()
    if repr != datatypes.DATA_REPRESENTATION_HISTOGRAM:
        return None
    values, bin_edges = data_wrapper.get_as_histogram()
    if dim == datatypes.DATA_DIMESNION_1D:
        be = bin_edges[0]
        weights = be[1:] - be[:-1]
        return np.dot(values, weights)
    be_x = bin_edges[0][1:] - bin_edges[0][:-1]
    be_y = bin_edges[1][1:] - bin_edges[1][:-1]
    weights = np.outer(be_x, be_y).flatten()
    return np.dot(values.flatten(), weights)

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


def shape(data_wrapper_1, data_wrapper_2):
    if data_wrapper_1.get_shape() != data_wrapper_2.get_shape():
        METRICS_LOGGER.warning("Different shapes")
        return None
    repr, dim = data_wrapper.preferred_representation()
    if repr != datatypes.DATA_REPRESENTATION_HISTOGRAM:
        return None
    values_1, bin_edges = data_wrapper_1.get_as_histogram()
    values_2, bin_edges = data_wrapper_2.get_as_histogram()

    norm_1 = values_1 / integral(data_wrapper_1)
    norm_2 = values_2 / integral(data_wrapper_2)

    try:
        return np.sum((norm_1 - norm_2)**2 / (norm_1 + norm_2)) / 2
    except ZeroDivisionError:
        METRICS_LOGGER.warning("Empty histograms, division by 0")
        return None

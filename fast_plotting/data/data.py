"""Data structures

Classes:
    DataWrapper
        Holding core data in form of a numpy array and is identified by a name.
        In addition, it holds potential annotations
    DataAnnotations
        Containing additional information such as a description of axes.
        One object is hold by DataWrapper
"""

import numpy as np
import pandas as pd

from fast_plotting.data import datatypes
from fast_plotting.logger import get_logger

DATA_LOGGER = get_logger("Data")

class DataAnnotations:
    """Holding data annotations"""

    def __init__(self, **kwargs):
        """init

        For now only initialise some axis labels
        """
        self.axis_labels = kwargs.pop("axis_labels", [""] * 3)
        self.label = ""
        self.title = ""

class DataWrapper:
    """Holding the actual data identified by name"""

    def __init__(self, name, data, **kwargs):
        """init"""
        # the name should be unique
        self.name = name
        # optional binning
        self.bin_edges = kwargs.pop("bin_edges", None)
        # numpy array of data
        self.data = data
        if len(self.data.shape) > 3:
            DATA_LOGGER.critical("Cannot handle data with more than 3 dimensions, however, got an array with %d dimensions", len(self.data.shape))
        # uncertainties
        self.uncertainties = kwargs.pop("uncertainties", None)
        shape_expected = (*self.data.shape, 2)
        if self.uncertainties is None:
            self.uncertainties = np.full(shape_expected, 0.)
        if shape_expected != self.uncertainties.shape:
            # critical if shapes don't match
            DATA_LOGGER.critical("Got incompatible shapes of data and uncertainties %s (expected) vs. %s (given)", f"{shape_expected}", f"{self.uncertainties.shape}")
        if len(self.data.shape) > 2:
            if self.bin_edges is None:
                DATA_LOGGER.warning("It seems I got 2-dimensional data without any binning. It will not be possible to make a heatmap plot from that")
            else:
                if len(self.bin_edges) != 2:
                    DATA_LOGGER.critical("Bin edges for exactly 2 axes are requried but got %d", len(self.bin_edges))
                if len(self.bin_edges[0]) - 1 != self.data.shape[0] or len(self.bin_edges[1]) -1 != self.data.shape[1]:
                    DATA_LOGGER.critical("From data of shape (%d,%d) would expect bin edges of lengths (%d,%d) but got (%d,%d)", self.data.shape[0], self.data.shape[1], self.data.shape[0] + 1, self.data.shape[1] + 1, len(self.bin_edges[0]), len(self.bin_edges[1]))
            self.data = self.data.reshape(self.data.shape[0] * self.data.shape[1], self.data.shape[2])
            # We checked the compatibility with the data already. So if the data shape is sane, this should be good to go now
            self.uncertainties = self.uncertainties.reshape(self.uncertainties.shape[0] * self.uncertainties.shape[1], self.uncertainties.shape[2], 2)

        # Now make a final check if data length makes sense with bin edges length
        if self.bin_edges is not None:
            expect_length = 1
            bin_edges_length = []
            for be in self.bin_edges:
                bin_edges_length.append(len(be))
                expect_length *= (len(be) - 1)
            if self.data.shape[0] != expect_length:
                DATA_LOGGER.critical("With the given bin edges of length (%d,%d) would expect data length of %d but got data of length %d", *bin_edges_length, expect_length, self.data.shape[0])

        # annotations
        self.data_annotations = kwargs.pop("data_annotations", DataAnnotations(axis_labels=["label"] * data.shape[1]))

    def get_dimension(self):
        shape = self.data.shape[-1]
        if shape not in (2, 3):
            return datatypes.DATA_DIMESNION_UNKNOWN
        dim = datatypes.DATA_DIMESNION_1D if shape == 2 else datatypes.DATA_DIMESNION_2D
        return dim

    def preferred_representation(self):
        """derive preferred representation for this data"""
        repr = datatypes.DATA_REPRESENTATION_HISTOGRAM if self.bin_edges is not None else datatypes.DATA_REPRESENTATION_SCATTER
        return repr, self.get_dimension()

    def get_as_scatter(self):
        """Return ready to be used as scatter plot

        Return a third parameter either way, that can be seen as unity weight in case of 1D data
        """
        if self.get_dimension() == datatypes.DATA_DIMESNION_1D:
            return self.data[:,0], self.data[:,1], np.full((self.data.shape[0],), 1.)
        if self.get_dimension() == datatypes.DATA_DIMESNION_2D:
            return self.data[:,0], self.data[:,1], self.data[:,2]
        return None, None, None

    def get_as_histogram(self):
        if self.get_dimension() == datatypes.DATA_DIMESNION_1D:
            if self.bin_edges is None:
                return None, None
            return self.data[:,1], self.bin_edges
        if self.get_dimension() == datatypes.DATA_DIMESNION_2D:
            if self.bin_edges is None:
                return None, None
            return self.data.reshape(len(self.bin_edges[0]) - 1, len(self.bin_edges[1]) - 1, 3)[:,:,2], self.bin_edges
        return None, None

    def get_as_table(self):
        x, y, z = self.get_as_scatter()
        return pd.DataFrame({"tag": [self.name for _ in x], "x": x, "y": y, "z": z})


def combine_data_wrappers_df(*data_wrappers):
    if not data_wrappers:
        return None
    df = data_wrappers[0].get_as_table()
    if len(data_wrappers) == 1:
        return df
    df = pd.concat([df] + [dw.get_as_table() for dw in data_wrappers[1:]])
    return df



# class DataWrapperComplex(DataWrapper):
#     def __init__(self, name, data, **kwargs):
#         """init"""
#         # the name should be unique
#         self.name = name
#         # at this point - for now - we assume that self.data is a pandas DataFrame
#         self.data = data
#         if kwargs:
#             DATA_LOGGER.warning("Keyword arguments will not be used")
#         if not isinstance(data, pd.DataFrame):
#             # assume it's numpy now
#             super().__init__(name, data)
#             self.data = super().get_as_table()
#
#     def get_dimension(self):
#         return datatypes.DATA_DIMESNION_MULTI

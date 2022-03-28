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

from fast_plotting.logger import get_logger

DATA_LOGGER = get_logger("Data")

class DataAnnotations:
    """Holding data annotations"""

    def __init__(self, **kwargs):
        """init

        For now only initialise some axis labels
        """
        self.axis_labels = kwargs.pop("axis_labels", [""] * 3)

class DataWrapper:
    """Holding the actual data identified by name"""

    def __init__(self, name, data, **kwargs):
        """init"""
        # the name should be unique
        self.name = name
        # numpy array of data
        self.data = data
        # uncertainties
        self.uncertainties = kwargs.pop("uncertainties", None)
        shape_expected = (2 for _ in range(data.shape[1]))
        shape_expected = (data.shape[0], *shape_expected)
        if self.uncertainties is None:
            self.uncertainties = np.full(shape_expected, 0.)
        if shape_expected != self.uncertainties.shape:
            # critical if shapes don't match
            DATA_LOGGER.critical("Got incompatible shapes of data and uncertainties %s (expected) vs. %s (given)", f"{shape_expected}", f"{self.uncertainties.shape}")
        # annotations
        self.data_annotations = kwargs.pop("data_annotations", DataAnnotations(axis_labels=["label"] * data.shape[1]))

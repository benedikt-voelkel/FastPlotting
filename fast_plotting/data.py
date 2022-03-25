"""Data structures

Classes:
    DataWrapper
        Holding core data in form of a numpy array and is identified by a name.
        In addition, it holds potential annotations
    DataAnnotations
        Containing additional information such as a description of axes. One object is hold by DataWrapper
"""

class DataAnnotations:
    """Holding data annotations"""

    def __init__(self, **kwargs):
        """init

        For now only initialise some axis labels
        """
        self.axis_labels = kwargs.pop("axis_labels", None)

class DataWrapper:
    """Holding the actual data identified by name"""

    def __init__(self, name, data, **kwargs):
        """init"""
        # the name should be unique
        self.name = name
        # numpy array of data
        self.data = data
        # annotations
        self.data_annotations = kwargs.pop("data_annotations", DataAnnotations(axis_labels=["label"] * data.shape[1]))

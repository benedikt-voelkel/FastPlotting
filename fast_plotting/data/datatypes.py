"""Data structures

Classes:
    DataWrapper
        Holding core data in form of a numpy array and is identified by a name.
        In addition, it holds potential annotations
    DataAnnotations
        Containing additional information such as a description of axes.
        One object is hold by DataWrapper
"""

# what the data represents
DATA_REPRESENTATION_HISTOGRAM = 0
DATA_REPRESENTATION_SCATTER = 1

# data dimension
# means one depends on the other
DATA_DIMESNION_1D = 0
# means one depends on two others
DATA_DIMESNION_2D = 1
# available dimensions
DATA_DIMESNIONS = (DATA_DIMESNION_1D, DATA_DIMESNION_2D)
# unknown / cannot handle
DATA_DIMESNION_UNKNOWN = -1

"""Handle ROOT as data source"""

import sys
from os.path import split

import numpy as np

from ROOT import TFile, TH1, TH2, TH3, TDirectory, TList

from fast_plotting.data import DataAnnotations
from fast_plotting.logger import get_logger

ROOT_LOGGER = get_logger("ROOTSources")

def convert_to_numpy(histogram):
    """Convert to the numpy format we are using

    Right now only handle TH1<type>
    """
    if isinstance(histogram, TH1) and (isinstance(histogram, TH2) or isinstance(histogram, TH3)):
        ROOT_LOGGER.critical("At the moment can only handle TH1.")

    n_bins = histogram.GetNbinsX()
    data = np.full((n_bins, 2), 0.)

    axis = histogram.GetXaxis()
    for i in range(1, n_bins + 1):
        data[i-1][:] = [axis.GetBinCenter(i), histogram.GetBinContent(i)]

    return data


def get_histogram(root_object, root_path_list):

    next_in_list = root_path_list[0]
    finished = len(root_path_list) == 1
    if isinstance(root_object, TDirectory):
        if finished:
            h = root_object.Get(next_in_list)
            if not h:
                ROOT_LOGGER.critical("Object not found")
        return get_histogram(root_object.Get(next_in_list), root_path_list[1:])
    if isinstance(root_object, TList):
        this_list = None
        for l in root_object:
            if l.GetName() == next_in_list:
                this_list = l
                if finished:
                    return l
                break
        if not this_list:
            ROOT_LOGGER.critical("Object not found")
        return get_histogram(this_list, root_path_list[1:])


def read(filepath, histogram_path):
    """Get a histogram from ROOT source

    Right now only from ROOT file
    """

    f = TFile.Open(filepath, "READ")

    histogram_path_list = histogram_path.split("/")
    histogram = get_histogram(f, histogram_path_list)

    if not histogram:
        ROOT_LOGGER.critical("Failed to load histogram %s from file %s.", histogram_path, filepath)

    # prepare axis labels for annotations
    axis_labels = ["label"] * 2
    for i, a in enumerate((histogram.GetXaxis().GetTitle(), histogram.GetYaxis().GetTitle())):
        if a:
            axis_labels[i] = a

    data_annotations = DataAnnotations(axis_labels=axis_labels)

    # convert to numpy and return together with annotations
    return convert_to_numpy(histogram), data_annotations

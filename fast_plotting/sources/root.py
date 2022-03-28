"""Handle ROOT as data source"""

import numpy as np

from ROOT import TFile, TH1, TH2, TH3, TDirectory, TList

from fast_plotting.data import DataAnnotations
from fast_plotting.logger import get_logger

ROOT_LOGGER = get_logger("ROOTSources")

def convert_to_numpy(histogram):
    """Convert to the numpy format we are using

    Right now only handle TH1<type>
    """
    if isinstance(histogram, TH1) and isinstance(histogram, (TH2, TH3)):
        ROOT_LOGGER.critical("At the moment can only handle TH1.")

    n_bins = histogram.GetNbinsX()
    data = np.full((n_bins, 2), 0.)
    uncertainties = np.full((n_bins, 2, 2), 0.)

    axis = histogram.GetXaxis()
    for i in range(1, n_bins + 1):
        data[i-1][:] = [axis.GetBinCenter(i), histogram.GetBinContent(i)]
        uncertainties[i-1][1][:] = [histogram.GetBinError(i), histogram.GetBinError(i)]
        #uncertainties[i-1][1][:] = [1000, 1000]

    return data, uncertainties

def get_histogram(root_object, root_path_list):
    """Extract histogram from ROOT object

    Args:
        root_object: should either derived from TDirectory or TList
            object holding our object of interest, potentially at some deeper level
        root_path_list: iterable
            going further down in the hierarchy
    """
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
    ROOT_LOGGER.critical("Cannot handle ROOT object")
    return None

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
    axis_labels = [""] * 2
    for i, a in enumerate((histogram.GetXaxis().GetTitle(), histogram.GetYaxis().GetTitle())):
        if a:
            axis_labels[i] = a

    data_annotations = DataAnnotations(axis_labels=axis_labels)

    # convert to numpy and return together with annotations
    return *convert_to_numpy(histogram), data_annotations

def extract_impl(root_object, current_path, collect):
    current_path += f"/{root_object.GetName()}"
    if isinstance(root_object, TH1) and not isinstance(root_object, (TH2, TH3)):
        # Collect only what we can handle at the moment
        collect.append(current_path[1:])
    if isinstance(root_object, TDirectory):
        for k in root_object.GetListOfKeys():
            extract_impl(k.ReadObj(), current_path, collect)
    if isinstance(root_object, TList):
        for l in root_object:
            extract_impl(l, current_path, collect)

def extract_from_source(filepath):
    """get everything out of a potential ROOT file"""
    f = TFile.Open(filepath, "READ")
    if not f:
        return None

    collect = []

    extract_impl(f, "", collect)

    batches = []
    for i, c in enumerate(collect):
        rootpath = c.split("/")
        rootpath = "/".join(rootpath[1:])
        batches.append({"source_name": "root", "identifier": rootpath.replace("/", "_"), "filepath": filepath, "rootpath": rootpath})

    return batches

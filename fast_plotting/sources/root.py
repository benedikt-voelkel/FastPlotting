"""Handle ROOT as data source"""
from os.path import exists
import numpy as np
import gc

from ROOT import TFile, TH1, TH2, TH3, TDirectory, TList, gROOT, gObjectTable

from fast_plotting.data.data import DataAnnotations
from fast_plotting.logger import get_logger

ROOT_LOGGER = get_logger("ROOTSources")

# This is used for buffering loaded TDirectories/TFiles etc to avoid re-loading them again and again.
# Unfortunately we cannot guarantee that the memeory is cleaned everytime we open, load objects from
# and close ROOT files.
FILE_BUFFER = {}

def convert_to_numpy_1d(histogram):
    """Convert to the numpy for TH1"""
    n_bins = histogram.GetNbinsX()
    data = np.full((n_bins, 2), 0.)
    uncertainties = np.full((n_bins, 2, 2), 0.)
    # Need one element more cause N+1 bin edges
    bin_edges = np.full((n_bins + 1, 1), np.nan, dtype=float)

    axis = histogram.GetXaxis()
    for i in range(1, n_bins + 1):
        data[i-1][:] = [axis.GetBinCenter(i), histogram.GetBinContent(i)]
        uncertainties[i-1][1][:] = [histogram.GetBinError(i), histogram.GetBinError(i)]
        bin_edges[i-1] = axis.GetBinLowEdge(i)
        if i == n_bins:
            bin_edges[i] = axis.GetBinUpEdge(i)

    return data, uncertainties, [bin_edges]

def convert_to_numpy_2d(histogram):
    """Convert to the numpy for TH2"""
    n_bins_x = histogram.GetNbinsX()
    n_bins_y = histogram.GetNbinsY()
    n_bins = n_bins_x * n_bins_y

    data = np.full((n_bins_x, n_bins_y, 3), 0.)
    uncertainties = np.full((n_bins_x, n_bins_y, 3, 2), 0.)
    # Need one element more cause N+1 bin edges
    bin_edges = [np.full((n_bins_x + 1), np.nan, dtype=float), np.full((n_bins_y + 1), np.nan, dtype=float)]

    axis_x = histogram.GetXaxis()
    axis_y = histogram.GetYaxis()
    for i in range(1, n_bins_x + 1):
        bin_edges[0][i-1] = axis_x.GetBinLowEdge(i)
        if i == n_bins_x:
            bin_edges[0][i] = axis_x.GetBinUpEdge(i)
        for j in range(1, n_bins_y + 1):
            data[i-1,j-1,:] = [axis_x.GetBinCenter(i), axis_y.GetBinCenter(j), histogram.GetBinContent(i, j)]
            uncertainties[i-1,j-1,2,:] = [histogram.GetBinError(i, j), histogram.GetBinError(i, j)]
    for j in range(1, n_bins_y + 1):
        bin_edges[1][j-1] = axis_y.GetBinLowEdge(j)
        if j == n_bins_y:
            bin_edges[1][j] = axis_y.GetBinUpEdge(j)

    return data, uncertainties, bin_edges

def convert_to_numpy(histogram):
    """Convert to the numpy format we are using

    Right now only handle TH1 and TH2
    """
    if isinstance(histogram, (TH1, TH2)) and isinstance(histogram, TH3):
        ROOT_LOGGER.critical("At the moment can only handle TH1.")

    if isinstance(histogram, TH2):
        return convert_to_numpy_2d(histogram)
    return convert_to_numpy_1d(histogram)

def get_histogram(root_object, root_path_list, *, wait_for_source=False, buffer=None):
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
                if not wait_for_source:
                    ROOT_LOGGER.critical("Object not found")
                return None
            return h
        # Use the buffer here to store and load TDirectory objects if they exist already
        if buffer is not None:
            o = root_object.Get(next_in_list) if next_in_list not in buffer else buffer[next_in_list]
            buffer[next_in_list] = o
        else:
            o = root_object.Get(next_in_list)
        return get_histogram(o, root_path_list[1:], wait_for_source=wait_for_source, buffer=buffer)
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
        return get_histogram(this_list, root_path_list[1:], wait_for_source=wait_for_source, buffer=buffer)
    if not wait_for_source:
        ROOT_LOGGER.critical("Cannot handle ROOT object")
    return None

def read(filepath, histogram_path, *, wait_for_source=False):
    """Get a histogram from ROOT source

    Right now only from ROOT file
    """

    if not exists(filepath):
        if not wait_for_source:
            ROOT_LOGGER.critical("File %s doesn't seem to exist.", filepath)
        return None, None, None, None

    # Use this filebuffer to not open files more than once
    if filepath not in FILE_BUFFER:
        FILE_BUFFER[filepath] = {}
    buffer = FILE_BUFFER[filepath]

    if filepath not in buffer:
        f = TFile.Open(filepath, "READ")
        buffer[filepath] = f
    else:
        f = buffer[filepath]

    histogram_path_list = histogram_path.split("/")
    # Here the buffer is passed as well to collect further TDirectory s
    histogram = get_histogram(f, histogram_path_list, wait_for_source=wait_for_source, buffer=buffer)

    if not histogram:
        if not wait_for_source:
            ROOT_LOGGER.critical("Failed to load histogram %s from file %s.", histogram_path, filepath)
        return None, None, None, None

    # prepare axis labels for annotations
    axis_labels = [""] * 2
    for i, a in enumerate((histogram.GetXaxis().GetTitle(), histogram.GetYaxis().GetTitle())):
        if a:
            axis_labels[i] = a

    data_annotations = DataAnnotations(axis_labels=axis_labels)

    # convert to numpy and return together with annotations
    data, uncertainties, bin_edges = convert_to_numpy(histogram)
    f.Delete(histogram.GetName())
    #f.Close()
    return data, uncertainties, bin_edges, data_annotations

def extract_impl(root_object, current_path, collect, skip_this_name=False):
    if not skip_this_name:
        current_path += f"/{root_object.GetName()}"
    if isinstance(root_object, (TH1, TH2)) and not isinstance(root_object, TH3):
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

    extract_impl(f, "", collect, True)

    batches = []
    for i, c in enumerate(collect):
        batches.append({"source_name": "root", "identifier": c.replace("/", "_"), "filepath": filepath, "rootpath": c})

    return batches

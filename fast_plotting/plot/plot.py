"""Plotting classes and functionality"""

from math import sqrt, ceil
import matplotlib.pyplot as plt
from matplotlib import cm
from time import time

from fast_plotting.registry import get_from_registry
from fast_plotting.logger import get_logger
from fast_plotting.data import datatypes
from fast_plotting.plot import plottypes

PLOT_LOGGER = get_logger("Plot")

def finalise_label(label):
    """Wrapper to adjust label text if necessary"""
    if label:
        label = f"${label}$"
    label = label.replace("#", "")
    return label

def plot_single_1d(x, y, label, ax, plot_type=plottypes.PLOT_TYPE_STEP, xerr=None, yerr=None, bin_edges=None):
    """Put a single object on axes"""
    if plot_type not in plottypes.PLOT_TYPES:
        PLOT_LOGGER.error("Cannot handle plot type %s", plot_type)
        return

    if plot_type == plottypes.PLOT_TYPE_BAR:
        range_x = max(x) - min(x)
        width = range_x / len(x)
        ax.bar(x, y, alpha=0.4, width=width, label=label)
    elif plot_type == plottypes.PLOT_TYPE_SCATTER:
        # derive marker sizes from figure dimensions
        fig = ax.get_figure()
        # get size in pixels
        marker_sizes = fig.get_size_inches() * fig.dpi * 0.1
        p = ax.scatter(x, y, label=label, s=sqrt(marker_sizes[0]**2 + marker_sizes[1]**2))
        c = p.get_facecolor()
        if yerr is not None:
            ax.errorbar(x, y, yerr=yerr, lw=2, fmt="None", elinewidth=3, c=c)
    elif plot_type == plottypes.PLOT_TYPE_LINE:
        ax.plot(x, y, alpha=0.4, label=label)
    elif plot_type == plottypes.PLOT_TYPE_STEP:
        bins = len(x) if bin_edges is None else bin_edges
        h = ax.hist(x, bins=len(x), weights=y, histtype="step", label=label, lw=2, fill=None)
        if yerr is not None:
            ax.errorbar(x, y, yerr=yerr, lw=2, fmt="None", elinewidth=3)

def plot_single_2d(x, y, z, label, ax, plot_type=plottypes.PLOT_TYPE_SCATTER):
    """Put a single object on axes"""
    if plot_type not in plottypes.PLOT_TYPES:
        PLOT_LOGGER.error("Cannot handle plot type %s", plot_type)
        return

    if plot_type == plottypes.PLOT_TYPE_BAR:
        # this would be a heatmap
        return
    elif plot_type == plottypes.PLOT_TYPE_SCATTER:
        # derive marker sizes from figure dimensions
        fig = ax.get_figure()
        # get size in pixels
        marker_sizes = fig.get_size_inches() * fig.dpi * 0.1
        ax.scatter(x, y, label=label, s=sqrt(marker_sizes[0]**2 + marker_sizes[1]**2), c=z, cmap=cm.get_cmap("Greens"), vmin=min(z), vmax=max(z))

def finalise_figure(figure, save_path):
    """Wrapper to save and close figure

    Args:
        figure: Figure
        save_path: str
    """
    figure.tight_layout()
    figure.savefig(save_path)
    plt.close(figure)
    PLOT_LOGGER.debug("Plotted at %s", save_path)

class Plotter:
    def __init__(self, allow_2d_overlaying=False, *, accept_sources_not_found=False):
        self.data_wrappers = []
        # this maps like [[1, 3, 5], [2, 3, 4], [9,3]] where each sub-list conatins the indices of the histogram/function to be plotted. The index of the sub-lists refer to a plot
        self.wrappers_to_plot_mapping = []
        # a figure contains multiple plots and has a grid spec, logic as above
        self.plots_to_figure_mapping = []
        # potential grid specs, each figure has one or None at that index
        #self.grid_specs = []
        # plot name to index
        self.plot_name_to_index = {}
        # figure name to index
        self.figure_name_to_index = {}
        # allow 2d overlaying
        self.allow_2d_overlaying = allow_2d_overlaying
        # some suffices we collect, in particular to make 2D plotting more flexible
        self.plot_name_suffices = {}
        # plot properties
        self.plot_properties = {}
        # whether or not we accept source not found
        self.accept_sources_not_found = accept_sources_not_found

    def define_plot(self, plot_name, **kwargs):
        if plot_name in self.plot_properties:
            PLOT_LOGGER.warning("Not overwriting plot properties for plot %s", plot_name)
            return
        self.plot_properties[plot_name] = kwargs

    def add_to_plot(self, plot_name, identifier, allow_2d_overlaying=None):
        """Add an object to a plot

        Args:
            identifier: str
                name to find in registry
            plot_name: str
                identifies the plot to add to
        """
        allow_2d_overlaying = allow_2d_overlaying if allow_2d_overlaying is not None else self.allow_2d_overlaying
        data_wrapper = get_from_registry(identifier, accept_not_found=self.accept_sources_not_found)
        if data_wrapper is None:
            PLOT_LOGGER.warning("Cannot obtain data of identifier %s", identifier)
            return

        dim = data_wrapper.get_dimension()

        if plot_name not in self.plot_name_to_index:
            self.plot_name_to_index[plot_name] = len(self.wrappers_to_plot_mapping)
            self.wrappers_to_plot_mapping.append([data_wrapper])
        elif dim == datatypes.DATA_DIMESNION_1D or allow_2d_overlaying:
            self.wrappers_to_plot_mapping[self.plot_name_to_index[plot_name]].append(data_wrapper)
        elif dim == datatypes.DATA_DIMESNION_2D:
            # at this point we know that a 2D plot with this name exists. At the same time overlaying of 2D plots is not allowed so we need a new plot
            suffix = int(time())
            plot_name_auto = f"{plot_name}_{suffix}"
            self.plot_name_to_index[plot_name_auto] = len(self.wrappers_to_plot_mapping)
            self.wrappers_to_plot_mapping.append([data_wrapper])
            if plot_name not in self.plot_name_suffices:
                self.plot_name_suffices[plot_name] = []
            self.plot_name_suffices[plot_name].append(suffix)
            if plot_name in self.plot_properties:
                self.plot_properties[plot_name_auto] = self.plot_properties[plot_name]

    def define_figure(self, figure_name, *plot_names):
        if not plot_names:
            PLOT_LOGGER.warning("No plot names specified")
            return
        if figure_name in self.figure_name_to_index:
            PLOT_LOGGER.warning("Figure %s was already defined, not overwriting", figure_name)
            return
        # make a new figure if needed
        self.figure_name_to_index[figure_name] = len(self.plots_to_figure_mapping)
        self.plots_to_figure_mapping.append([])
        plots_on_figure = self.plots_to_figure_mapping[-1]
        for pl in plot_names:
            if pl not in self.plot_name_to_index:
                PLOT_LOGGER.warning("Plot name %s not found, skip", pl)
                continue
            plots_on_figure.append(self.plot_name_to_index[pl])
            # browse through plot names
            if pl in self.plot_name_suffices:
                for pls in self.plot_name_suffices[pl]:
                    plots_on_figure.append(self.plot_name_to_index[f"{pl}_{pls}"])

    def plot_1d(self, data_wrapper, ax):
        # TODO Really only 1d data at the moment
        data = data_wrapper.data
        uncertainties = data_wrapper.uncertainties
        data_annotations = data_wrapper.data_annotations
        x, y, _ = data_wrapper.get_as_scatter()
        #plot_type = plot_object.get("type", plottypes.PLOT_TYPE_STEP)
        plot_single_1d(x, y, data_annotations.label, ax, plottypes.PLOT_TYPE_STEP) #, xerr=xerr, yerr=yerr)

    def plot_2d(self, data_wrapper, ax):
        # TODO Really only 1d data at the moment
        data = data_wrapper.data
        uncertainties = data_wrapper.uncertainties
        data_annotations = data_wrapper.data_annotations
        x, y, z = data_wrapper.get_as_scatter()
        #plot_type = plot_object.get("type", plottypes.PLOT_TYPE_STEP)
        plot_single_2d(x, y, z, data_annotations.label, ax, plottypes.PLOT_TYPE_SCATTER)

    def plot_single(self, data_wrapper, ax):
        """Plot from a config batch

        Args:
            config_batch: dict
                dictionary containing all info for plot
        """
        dim = data_wrapper.get_dimension()
        if dim == datatypes.DATA_DIMESNION_1D:
            self.plot_1d(data_wrapper, ax)
        elif dim == datatypes.DATA_DIMESNION_2D:
            self.plot_2d(data_wrapper, ax)
        else:
            PLOT_LOGGER("Unknown dimension")

    def plot(self, figure_name, save_path):
        plot_index_to_name = [""] * len(self.plot_name_to_index)
        for k, v in self.plot_name_to_index.items():
            plot_index_to_name[v] = k

        if figure_name not in self.figure_name_to_index:
            PLOT_LOGGER.warning("Figure with name %s unknown, not plotting", figure_name)
            return
        plot_index_list = self.plots_to_figure_mapping[self.figure_name_to_index[figure_name]]
        if not plot_index_list:
            PLOT_LOGGER.warning("Nothing to plot")
            return
        n_required_cols_rows = ceil(sqrt(len(plot_index_list)))

        figure, axes = plt.subplots(n_required_cols_rows, n_required_cols_rows, figsize=(40, 40))
        try:
            axes = axes.flatten()
        except AttributeError:
            axes = [axes]

        # collect axes tat contain something so we can switch of the axis on the remaining ones
        n_axes_contain_something = 0
        for plot_index, ax in zip(plot_index_list, axes):
            data_annotations = None
            for data_wrapper in self.wrappers_to_plot_mapping[plot_index]:
                data_annotations = data_wrapper.data_annotations
                self.plot_single(data_wrapper, ax)
            ax.legend(loc="best", fontsize=30)
            # TODO: This doesn't belong here but must go to the calling function
            properties = self.plot_properties.get(plot_index_to_name[plot_index], {})
            ax.set_xlabel(finalise_label(properties.get("x_label", data_annotations.axis_labels[0])), fontsize=30)
            ax.set_ylabel(finalise_label(properties.get("y_label", data_annotations.axis_labels[1])), fontsize=30)
            ax.tick_params("both", labelsize=30)
            ax.set_title(properties.get("title", ""), fontsize=30)
            n_axes_contain_something += 1
        for ax in axes[n_axes_contain_something:]:
            ax.axis("off")
        finalise_figure(figure, save_path)

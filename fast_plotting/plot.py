"""Plotting classes and functionality"""

from math import sqrt
from os.path import join
import matplotlib.pyplot as plt

from fast_plotting.registry import get_from_registry
from fast_plotting.logger import get_logger
from fast_plotting.io import parse_json, make_dir

PLOT_LOGGER = get_logger("Plot")

PLOT_TYPE_BAR = "bar"
PLOT_TYPE_SCATTER = "scatter"
PLOT_TYPE_LINE = "line"
PLOT_TYPES = (PLOT_TYPE_BAR, PLOT_TYPE_SCATTER, PLOT_TYPE_LINE)


def plot_single_1d(x, y, label, ax, plot_type=PLOT_TYPE_BAR, xerr=None, yerr=None):
    """Put a single object on axes"""
    if plot_type not in PLOT_TYPES:
        PLOT_LOGGER.error("Cannot handle plot type %s", plot_type)
        return

    if plot_type == PLOT_TYPE_BAR:
        ax.bar(x, y, alpha=0.4, label=label)
    elif plot_type == PLOT_TYPE_SCATTER:
        # derive marker sizes from figure dimensions
        fig = ax.get_figure()
        # get size in pixels
        marker_sizes = fig.get_size_inches() * fig.dpi * 0.1
        p = ax.scatter(x, y, label=label, s=sqrt(marker_sizes[0]**2 + marker_sizes[1]**2))
        c = p.get_facecolor()
        ax.errorbar(x, y, yerr=yerr, lw=2, fmt="None", elinewidth=3, c=c)
    elif plot_type == PLOT_TYPE_LINE:
        ax.plot(x, y, alpha=0.4, label=label)

def plot_single(config_batch, out_dir="./"):
    """Plot from a config batch

    Args:
        config_batch: dict
            dictionary containing all info for plot
    """
    if not config_batch.get("enable", False):
        return

    figure, ax = plt.subplots(figsize=(30, 30))

    for plot_object in config_batch["objects"]:
        data_wrapper = get_from_registry(plot_object["identifier"])
        data = data_wrapper.data
        uncertainties = data_wrapper.uncertainties
        data_annotations = data_wrapper.data_annotations
        # TODO Really only 1d data at the moment
        x = data[:,0]
        y = data[:,1]
        xerr, yerr = (None, None)
        if uncertainties is not None:
            xerr = uncertainties[:,0,:].T
            yerr = uncertainties[:,1,:].T
        plot_type = plot_object.get("type", PLOT_TYPE_SCATTER)
        plot_single_1d(x, y, plot_object.get("label", "label"), ax, plot_type, xerr=xerr, yerr=yerr)

    ax.legend(loc="best", fontsize=30)
    ax.set_xlabel(config_batch.get("xlabel", data_annotations.axis_labels[0]), fontsize=30)
    ax.set_ylabel(config_batch.get("ylabel", data_annotations.axis_labels[1]), fontsize=30)
    ax.tick_params("both", labelsize=30)

    figure.tight_layout()
    save_path = join(out_dir, config_batch["output"])
    figure.savefig(save_path)
    plt.close(figure)

    PLOT_LOGGER.info("Plotted at %s", save_path)

def plot(config, out_dir="./"):
    """Read from a JSON config

    Args:
        config: str
            apth to config JSON
        out_dir: str
            desired output directory
    """
    make_dir(out_dir)
    for batch in config.get_plots():
        plot_single(batch, out_dir)

def add_plot_for_each_source(config):
    """Add a plot dictionary for each source automatically"""
    for s in config.get_sources():
        config.add_plot(objects=[{"identifier": s["identifier"], "type": PLOT_TYPE_SCATTER, "label": s.get("label", "")}], enable=False, output=f"{s['identifier']}.png")

def add_overlay_plot_for_sources(config):
    """Make overlay plots if possible"""
    objects = {}
    for s in config.get_sources():
        identifier = s["identifier"]
        identifier_key = "_".join(identifier.split("_")[:-1])
        if identifier_key not in objects:
            objects[identifier_key] = []
        objects[identifier_key].append({"identifier": identifier, "type": PLOT_TYPE_SCATTER, "label": s.get("label", "")})
    for k, o in objects.items():
        config.add_plot(objects=o, enable=False, output=f"{k}.png")

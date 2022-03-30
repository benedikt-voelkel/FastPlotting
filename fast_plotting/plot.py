"""Plotting classes and functionality"""

from math import sqrt, ceil
from os.path import join
import matplotlib.pyplot as plt

from fast_plotting.registry import get_from_registry
from fast_plotting.logger import get_logger
from fast_plotting.io import parse_json, make_dir

PLOT_LOGGER = get_logger("Plot")

PLOT_TYPE_BAR = "bar"
PLOT_TYPE_SCATTER = "scatter"
PLOT_TYPE_LINE = "line"
PLOT_TYPE_STEP = "step"
PLOT_TYPES = (PLOT_TYPE_BAR, PLOT_TYPE_SCATTER, PLOT_TYPE_LINE, PLOT_TYPE_STEP)


def finalise_label(label):
    """Wrapper to adjust label text if necessary"""
    if label:
        label = f"${label}$"
    label = label.replace("#", "")
    return label

def plot_single_1d(x, y, label, ax, plot_type=PLOT_TYPE_STEP, xerr=None, yerr=None):
    """Put a single object on axes"""
    if plot_type not in PLOT_TYPES:
        PLOT_LOGGER.error("Cannot handle plot type %s", plot_type)
        return

    if plot_type == PLOT_TYPE_BAR:
        range_x = max(x) - min(x)
        width = range_x / len(x)
        ax.bar(x, y, alpha=0.4, width=width, label=label)
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
    elif plot_type == PLOT_TYPE_STEP:
        ax.step(x, y, where="mid", label=label, lw=2)

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

def plot_single(config_batch, ax=None):
    """Plot from a config batch

    Args:
        config_batch: dict
            dictionary containing all info for plot
    """
    if not ax:
        # make new axes if needed
        _, ax = plt.subplots(figsize=(30, 30))
    figure = ax.get_figure()

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
        plot_type = plot_object.get("type", PLOT_TYPE_STEP)
        plot_single_1d(x, y, plot_object.get("label", "label"), ax, plot_type, xerr=xerr, yerr=yerr)

    ax.legend(loc="best", fontsize=30)

    ax.set_xlabel(finalise_label(config_batch.get("xlabel", f"{data_annotations.axis_labels[0]}")), fontsize=30)
    ax.set_ylabel(finalise_label(config_batch.get("ylabel", f"{data_annotations.axis_labels[1]}")), fontsize=30)
    ax.tick_params("both", labelsize=30)

    return figure, ax

def plot_all_in_one(batches):
    """Plot all given batches into 1 figure"""
    n_axes_cols_rows = ceil(sqrt(len(batches)))
    figure, axes = plt.subplots(n_axes_cols_rows, n_axes_cols_rows, figsize=(40, 40))
    axes = axes.flatten()
    turn_off_axes = 0
    for ax, b in zip(axes, batches):
        plot_single(b, ax)
        turn_off_axes += 1
    if turn_off_axes < len(axes):
        for i in range(turn_off_axes, len(axes)):
            axes[i].axis("off")
    return figure

def plot_impl(batches, all_in_one=False):
    """Actual implementation of plotting

    Call correct plotting function
    """
    if not all_in_one:
        for b in batches:
            yield plot_single(b)[0], b["output"]
    else:
        yield plot_all_in_one(batches), "summary.png"

def plot(config, out_dir="./", all_in_one=False):
    """Read from a JSON config

    Args:
        config: str
            apth to config JSON
        out_dir: str
            desired output directory
        all_in_one: bool
            whether or not to throw everything into one summary figure
    """
    batches = [b for b in config.get_plots() if b["enable"]]
    if not batches:
        # just return if nothing to plot
        return
    make_dir(out_dir)
    for figure, save_path in plot_impl(batches, all_in_one):
        finalise_figure(figure, join(out_dir, save_path))

def add_plot_for_each_source(config):
    """Add a plot dictionary for each source automatically"""
    for s in config.get_sources():
        config.add_plot(identifier=s["identifier"], objects=[{"identifier": s["identifier"], "type": PLOT_TYPE_STEP, "label": s.get("label", "")}], enable=False, output=f"{s['identifier']}.png")

def add_overlay_plot_for_sources(config):
    """Make overlay plots if possible"""
    objects = {}
    for s in config.get_sources():
        identifier = s["identifier"]
        identifier_key = "_".join(identifier.split("_")[:-1])
        if identifier_key not in objects:
            objects[identifier_key] = []
        objects[identifier_key].append({"identifier": identifier, "type": PLOT_TYPE_STEP, "label": s.get("label", "")})
    for k, o in objects.items():
        config.add_plot(identifier=k, objects=o, enable=False, output=f"{k}.png")

from os.path import join

from fast_plotting.plot.plot import Plotter
from fast_plotting.io import make_dir
from fast_plotting.logger import get_logger
from fast_plotting.plot import plottypes

PLOT_LOGGER = get_logger("Plot")

def add_plot_for_each_source(config):
    """Add a plot dictionary for each source automatically"""
    # TODO This is too strict, needs to be more flexible
    config.reset_plots()
    for s in config.get_sources():
        config.add_plot(identifier=s["identifier"], objects=[{"identifier": s["identifier"], "type": plottypes.PLOT_TYPE_STEP, "label": s.get("label", "")}], title=s["identifier"], enable=False, output=f"{s['identifier']}.png")

def add_overlay_plot_for_sources(config):
    """Make overlay plots if possible"""
    # TODO This is too strict, needs to be more flexible
    config.reset_plots()
    objects = {}
    for s in config.get_sources():
        identifier = s["identifier"]
        identifier_key = "_".join(identifier.split("_")[:-1])
        if identifier_key not in objects:
            objects[identifier_key] = []
        objects[identifier_key].append({"identifier": identifier, "type": plottypes.PLOT_TYPE_STEP, "label": s.get("label", "")})
    for k, o in objects.items():
        config.add_plot(identifier=k, objects=o, title=k, enable=False, output=f"{k}.png")

def plot_auto(config, out_dir="./", all_in_one=False, *, accept_sources_not_found=False):
    batches = [b for b in config.get_plots() if b["enable"]]
    if not batches:
        PLOT_LOGGER.warning("Nothing enabled, nothing to plot")
        return
    make_dir(out_dir)
    plotter = Plotter(accept_sources_not_found=accept_sources_not_found)
    collect_fo_all_in_one = []
    for b in batches:
        plot_properties = {"title": b.get("title", b["identifier"])}
        for l in ("x_label", "y_label"):
            axis_label = b.get("x_label", None)
            if axis_label:
                plot_properties[l] = axis_label
        plotter.define_plot(b["identifier"], **plot_properties)
        for plot_object in b["objects"]:
            po_properties = {}
            if "label" in b:
                po_properties["label"] = b["label"]
            plotter.add_to_plot(b["identifier"], plot_object["identifier"], **po_properties)

        if not all_in_one:
            plotter.define_figure(b["identifier"], b["identifier"])
            plotter.plot(b["identifier"], join(out_dir, b["output"]))
        else:
            collect_fo_all_in_one.append(b["identifier"])
    if collect_fo_all_in_one:
        plotter.define_figure("summary", *collect_fo_all_in_one)
        plotter.plot("summary", join(out_dir, "summary.png"))

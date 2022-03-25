"""Plotting classes and functionality"""

import matplotlib.pyplot as plt

from fast_plotting.registry import get_from_registry
from fast_plotting.logger import get_logger
from fast_plotting.io import parse_json

PLOT_LOGGER = get_logger("Plot")

def plot(config_batch):
    """Plot from a config batch

    Args:
        config_batch: dict
            dictionary containing all info for plot
    """
    figure, ax = plt.subplots(figsize=(30, 30))

    for object in config_batch["objects"]:
        data_wrapper = get_from_registry(object["identifier"])
        data = data_wrapper.data
        x = data[:,0]
        y = data[:,1]
        ax.bar(x, y, alpha=0.4, label=object.get("label", "label"))

    ax.legend(loc="best", fontsize=30)
    ax.set_xlabel(config_batch.get("xlabel", "xlabel"), fontsize=30)
    ax.set_ylabel(config_batch.get("ylabel", "ylabel"), fontsize=30)
    ax.tick_params("both", labelsize=30)

    figure.tight_layout()
    figure.savefig(config_batch["output"])
    plt.close(figure)

    PLOT_LOGGER.info("Plotted at %s", config_batch["output"])

def read_from_config(config):
    """Read from a JSON config

    Args:
        config: str
            apth to config JSON
    """
    config = parse_json(config)

    if "plots" not in config:
        PLOT_LOGGER.critical("No plots found")

    for batch in config["plots"]:
        plot(batch)

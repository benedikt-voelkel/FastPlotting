"""Entry point"""

import sys
import argparse

from fast_plotting.config import Config, configure_from_sources
from fast_plotting.registry import read_from_config
from fast_plotting.plot import plot as plot_impl
from fast_plotting.plot import add_plot_for_each_source, add_overlay_plot_for_sources

from fast_plotting.logger import get_logger

MAIN_LOGGER = get_logger()

def plot(args):
    """Plot from cmd args"""
    MAIN_LOGGER.info("Run")

    config = Config()
    config.read(args.config)

    read_from_config(config)
    plot_impl(config, args.output)

    MAIN_LOGGER.info("Done")

    return 0

def configure(args):
    config = configure_from_sources(args.files, args.labels)
    if args.single:
        add_plot_for_each_source(config)
    if args.overlay:
        add_overlay_plot_for_sources(config)
    config.enable_plots(*args.enable_plots)
    config.write(args.output)
    return 0

def main():
    """
    Entry point for general plotting
    """

    common_debug_parser = argparse.ArgumentParser(add_help=False)
    common_debug_parser.add_argument("--debug", action="store_true")

    main_parser = argparse.ArgumentParser("FastPlotting")
    sub_parsers = main_parser.add_subparsers(dest="command")

    plot_parser = sub_parsers.add_parser("plot", parents=[common_debug_parser])
    plot_parser.set_defaults(func=plot)
    plot_parser.add_argument("-c", "--config", help="plot configuration")
    plot_parser.add_argument("-o", "--output", help="Top directory where to save plots", default="./")

    config_parser = sub_parsers.add_parser("configure", parents=[common_debug_parser])
    config_parser.set_defaults(func=configure)
    config_parser.add_argument("-f", "--files", nargs="+", help="An input file from which to build a configuration", required=True)
    config_parser.add_argument("-l", "--labels", nargs="+", help="A label for the data", default="label")
    config_parser.add_argument("-o", "--output", help="Where to write the derived JSON configuration", default="config.json")
    config_parser.add_argument("--overlay", help="If the sources have the same structure, make overlay plots", action="store_true")
    config_parser.add_argument("--single", help="Make single plots for each source found", action="store_true")
    config_parser.add_argument("--enable-plots", dest="enable_plots", nargs="+", help="Enable plots (pass \"all\" to enable all plots)")

    args = main_parser.parse_args()

    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())

"""Entry point"""

import sys
import argparse
from time import sleep

from fast_plotting.config import read_config, configure_from_sources
from fast_plotting.registry import read_from_config, load_source_from_config, get_from_registry
from fast_plotting.plot.utils import plot_auto, add_plot_for_each_source, add_overlay_plot_for_sources
from fast_plotting.metrics.metrics import print_metrics, compute_metrics

from fast_plotting.logger import get_logger, reconfigure_logging

MAIN_LOGGER = get_logger()

def plot(args):
    """Plot from cmd args"""
    MAIN_LOGGER.info("Run")
    config = read_config(args.config)
    read_from_config(config)
    plot_auto(config, args.output, args.all_in_one)
    MAIN_LOGGER.info("Done")
    return 0

def configure(args):
    """create a configuration"""
    if not args.config:
        config = configure_from_sources(args.files, args.labels)
    else:
        # in this case we don't add plots, let's keep things simple for now
        config = read_config(args.config)
        args.output = args.config

    if args.single:
        add_plot_for_each_source(config)
    if args.overlay:
        add_overlay_plot_for_sources(config)

    config.enable_plots(*args.enable_plots)
    config.write(args.output)
    return 0

def monitor(args):
    config = read_config(args.config)
    try:
        while True:
            read_from_config(config, True, wait_for_source=True)
            plot_auto(config, args.output, True, accept_sources_not_found=True)
            sleep(5)
    except KeyboardInterrupt:
        MAIN_LOGGER.info("Stop monitoring, shut down")


def inspect(args):
    """Quick inspection of config"""
    config = read_config(args.config)
    config.print_sources()
    config.print_plots()

def metrics(args):
    config = read_config(args.config)
    for s in args.sources:
        load_source_from_config(config, s)
    print_metrics(compute_metrics([get_from_registry(s) for s in args.sources], args.metrics, args.compare))


def main():
    """
    Entry point for general plotting
    """

    common_debug_parser = argparse.ArgumentParser(add_help=False)
    common_debug_parser.add_argument("--debug", action="store_true")

    common_config_parser = argparse.ArgumentParser(add_help=False)
    common_config_parser.add_argument("--config", "-c", help="Pass already existing config", required=True)

    main_parser = argparse.ArgumentParser("FastPlotting")
    sub_parsers = main_parser.add_subparsers(dest="command")

    metrics_parser = sub_parsers.add_parser("metric", parents=[common_debug_parser, common_config_parser])
    metrics_parser.set_defaults(func=metrics)
    metrics_parser.add_argument("--compare", action="store_true", help="compare all to first")
    metrics_parser.add_argument("-s", "--sources", nargs="+", help="source identifiers to be compared")
    metrics_parser.add_argument("-m", "--metrics", nargs="+", help="metrics to be applied")

    plot_parser = sub_parsers.add_parser("plot", parents=[common_debug_parser])
    plot_parser.set_defaults(func=plot)
    plot_parser.add_argument("-c", "--config", help="plot configuration")
    plot_parser.add_argument("-o", "--output", help="Top directory where to save plots", default="./")
    plot_parser.add_argument("--all-in-one", dest="all_in_one", action="store_true", help="plot everything into one final figure")

    config_parser = sub_parsers.add_parser("configure", parents=[common_debug_parser])
    config_parser.set_defaults(func=configure)
    config_parser.add_argument("-f", "--files", nargs="*", help="An input file from which to build a configuration")
    config_parser.add_argument("-l", "--labels", nargs="*", help="A label for the data")
    config_parser.add_argument("-c", "--config", help="potential input config to configure further")
    config_parser.add_argument("-o", "--output", help="Where to write the derived JSON configuration", default="config.json")
    config_parser.add_argument("--overlay", help="If the sources have the same structure, make overlay plots", action="store_true")
    config_parser.add_argument("--single", help="Make single plots for each source found", action="store_true")
    config_parser.add_argument("--enable-plots", dest="enable_plots", nargs="+", help="Enable plots (pass \"all\" to enable all plots)", default=[])

    monitor_parser = sub_parsers.add_parser("monitor", parents=[common_debug_parser, common_config_parser])
    monitor_parser.set_defaults(func=monitor)
    monitor_parser.add_argument("-o", "--output", help="Top directory where to save plots", default="./")

    inspect_parser = sub_parsers.add_parser("inspect", parents=[common_debug_parser, common_config_parser])
    inspect_parser.set_defaults(func=inspect)

    args = main_parser.parse_args()

    # reconfigure in case user wants to enable debug messages
    reconfigure_logging(args.debug)

    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())

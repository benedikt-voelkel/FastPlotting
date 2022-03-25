import sys
import argparse

from fast_plotting.registry import read_from_config as read_data
from fast_plotting.registry import print_registry
from fast_plotting.plot import read_from_config as read_plots

from fast_plotting.logger import get_logger

MAIN_LOGGER = get_logger()

def plot(args):

    MAIN_LOGGER.info("Run")

    read_data(args.config)
    read_plots(args.config)

    MAIN_LOGGER.info("Done")

    return 0


def main():
    """
    Entry point for general plotting
    """

    parser = argparse.ArgumentParser()

    sub_parsers = parser.add_subparsers(dest="command")

    plot_parser = sub_parsers.add_parser("plot")
    plot_parser.set_defaults(func=plot)
    plot_parser.add_argument("config", help="plot configuration")

    args = parser.parse_args()

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

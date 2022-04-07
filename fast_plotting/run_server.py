"""Entry point"""

import sys
import argparse
from time import sleep

from fast_plotting.application.backend.base import create_app

from fast_plotting.logger import get_logger, reconfigure_logging

APPLICATION_LOGGER = get_logger("Application")


def run(args):
    """Quick inspection of config"""
    app = create_app()

    app.run()

def main():
    """
    Entry point for general plotting
    """

    common_debug_parser = argparse.ArgumentParser(add_help=False)
    common_debug_parser.add_argument("--debug", action="store_true")

    main_parser = argparse.ArgumentParser("FastPlotting")
    sub_parsers = main_parser.add_subparsers(dest="command")

    inspect_parser = sub_parsers.add_parser("run", parents=[common_debug_parser])
    inspect_parser.set_defaults(func=run)

    args = main_parser.parse_args()

    # reconfigure in case user wants to enable debug messages
    reconfigure_logging(args.debug)

    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())

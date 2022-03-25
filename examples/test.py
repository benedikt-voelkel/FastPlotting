"""example 1"""

from os.path import dirname, join

from fast_plotting.registry import read_from_config

config = join(dirname(__file__), "test.json")
read_from_config(config)

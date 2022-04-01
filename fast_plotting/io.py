"""Functionality to manage I/O"""

from os.path import expanduser, isfile, isdir, exists
from os import makedirs
import json

from fast_plotting.logger import get_logger

IO_LOGGER = get_logger("IO")

def parse_json(filepath):
    """wrap JSON reading"""
    filepath = expanduser(filepath)
    if not isfile(filepath):
        #IO_LOGGER.error("ERROR: JSON file %s does not exist.", filepath)
        return None
    with open(filepath, "r") as f:
        try:
            return json.load(f)
        except (UnicodeDecodeError, json.decoder.JSONDecodeError):
            return None

def dump_json(to_json, filepath):
    """wrap JSON writing"""
    filepath = expanduser(filepath)
    with open(filepath, 'w') as f:
        json.dump(to_json, f, indent=2)

def make_dir(name):
    if exists(name):
        if not isdir(name):
            IO_LOGGER.critical("There seems to exist a file which has the same name as your chosen output directory %s. Cannot proceed", name)
        return
    makedirs(name)

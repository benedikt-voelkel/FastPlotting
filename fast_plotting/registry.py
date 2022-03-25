"""Top functionality to handle input data and register"""

import sys

from fast_plotting.data import DataAnnotations, DataWrapper
from fast_plotting.sources.root import read as get_from_root
from fast_plotting.io import parse_json
from fast_plotting.logger import get_logger

DATA_LOGGER = get_logger("Data")
# global dictionary to register all data
DATA_REGISTRY = {}

def print_registry():
    """Print the registry dictionary"""
    print(DATA_REGISTRY)

def add_to_registry(identifier, data_wrapper):
    """Add some data to registry

    Args:
        identifier: str
            unique name
        data_wrapper: fast_plotting.data.DataWrapper
            the data to be registered
    """
    if identifier in DATA_REGISTRY:
        DATA_LOGGER.critical("Data %s is already there, not adding it", identifier)

    DATA_REGISTRY[identifier] = data_wrapper

def get_from_registry(identifier):
    """Get a DataWrapper object by name

    Args:
        identifier: str
            unique name
    """
    if identifier not in DATA_REGISTRY:
        DATA_LOGGER.critical("Data %s not registered", identifier)
    return DATA_REGISTRY[identifier]

def get_data_from_source(batch):
    """Get some data from a source

    Args:
        batch: dict
            Dictionary containing all information to extract data
    """
    source_name = batch["source_name"].lower()
    identifier = batch["identifier"]

    if source_name == "root":
        if "filepath" not in batch or "rootpath" not in batch:
            DATA_LOGGER.critical("Need filepath and path to object inside ROOT file")
        data, data_annotations = get_from_root(batch["filepath"], batch["rootpath"])
        data_wrapper = DataWrapper(identifier, data, data_annotations=data_annotations)
        add_to_registry(identifier, data_wrapper)
    else:
        DATA_LOGGER.critical("Cannot digest from source %s", source_name)

def read_from_config(config):
    """Read from a JSON config

    Args:
        config: str
            apth to config JSON
    """
    config = parse_json(config)

    if "sources" not in config:
        DATA_LOGGER.critical("No sources found")

    for batch in config["sources"]:
        get_data_from_source(batch)

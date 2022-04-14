"""Top functionality to handle input data and register"""

from fast_plotting.data.data import DataWrapper
from fast_plotting.sources.root import read as get_from_root
from fast_plotting.io import parse_json
from fast_plotting.logger import get_logger

DATA_LOGGER = get_logger("Data")
# global dictionary to register all data
DATA_REGISTRY = {}

def print_registry():
    """Print the registry dictionary"""
    print(DATA_REGISTRY)

def add_to_registry(identifier, data_wrapper, overwrite=False):
    """Add some data to registry

    Args:
        identifier: str
            unique name
        data_wrapper: fast_plotting.data.DataWrapper
            the data to be registered
    """
    if identifier in DATA_REGISTRY and not overwrite:
        DATA_LOGGER.critical("Data %s is already there, not adding it", identifier)

    if identifier in DATA_REGISTRY and overwrite:
        DATA_REGISTRY[identifier].data = data_wrapper.data
        DATA_REGISTRY[identifier].uncertainties = data_wrapper.uncertainties
        DATA_REGISTRY[identifier].bin_edges = data_wrapper.bin_edges
        DATA_REGISTRY[identifier].data_annotations = data_wrapper.data_annotations
        return

    if identifier not in DATA_REGISTRY and overwrite:
        DATA_LOGGER.warning("Update of %s requested but not in registry, loading instead for the first time", identifier)

    DATA_REGISTRY[identifier] = data_wrapper

def get_from_registry(identifier, *, accept_not_found=False):
    """Get a DataWrapper object by name

    Args:
        identifier: str
            unique name
    """
    if identifier not in DATA_REGISTRY:
        if not accept_not_found:
            DATA_LOGGER.critical("Data %s not registered", identifier)
        return None
    return DATA_REGISTRY[identifier]

def get_data_from_source(batch, overwrite=False, *, wait_for_source=False):
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
        data, uncertainties, bin_edges, data_annotations = get_from_root(batch["filepath"], batch["rootpath"], wait_for_source=wait_for_source)
        if data is None and wait_for_source:
            DATA_LOGGER.warning("Aparrently waiting for source %s to become available", identifier)
            return

        data_annotations.label = batch.get("label", "")

        data_wrapper = DataWrapper(identifier, data, uncertainties=uncertainties, bin_edges=bin_edges, data_annotations=data_annotations)
        add_to_registry(identifier, data_wrapper, overwrite)
    else:
        DATA_LOGGER.critical("Cannot digest from source %s", source_name)

def load_source_from_config(config, identifier, overwrite=False):
    batch = config.get_source(identifier)
    if not batch:
        DATA_LOGGER.error("Cannot find %s as a source in the configuration", identifier)
        return
    get_data_from_source(batch, overwrite)

def read_from_config(config, update=False, *, wait_for_source=False):
    """Read from a JSON config

    Args:
        config: str
            apth to config JSON
    """
    # Only load objects we actually need
    load_only_identifiers = []
    for batch in config.get_plots():
        if not batch["enable"]:
            continue
        for o in batch["objects"]:
            load_only_identifiers.append(o["identifier"])
    for batch in config.get_sources():
        if batch["identifier"] not in load_only_identifiers:
            continue
        get_data_from_source(batch, update, wait_for_source=wait_for_source)

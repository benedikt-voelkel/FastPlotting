"""Configuration interface"""

from fast_plotting.logger import get_logger
from fast_plotting.io import parse_json, dump_json
from fast_plotting.sources.root import extract_from_source

CONFIG_LOGGER = get_logger("Config")


class ConfigInterface:
    def __init__(self):
        self._config = None

    def __is_sane(self):
        if self._config is None:
            return
        if "sources" not in self._config:
            CONFIG_LOGGER.critical("Cannot find \"sources\" field in configuration")
        if "plots" not in self._config:
            CONFIG_LOGGER.critical("Cannot find \"plots\" field in configuration")

    def __initialise(self):
        if self._config is not None:
            return
        self._config = {"sources": [], "plots": []}

    def read(self, path):
        if self._config is not None:
            CONFIG_LOGGER.warning("Overwriting existing configuration")
        self._config = parse_json(path)
        self.__is_sane()

    def write(self, path):
        if self._config is None:
            CONFIG_LOGGER.warning("No configuration to write")
            return
        dump_json(self._config, path)
        CONFIG_LOGGER.info("Written configuration to %s", path)

    def add_data_source(self, source_name, identifier, **kwargs):
        self.__initialise()
        kwargs["source_name"] = source_name
        kwargs["identifier"] = identifier
        self._config["sources"].append(kwargs)

    def add_plot(self, **kwargs):
        self.__initialise()
        self._config["plots"].append(kwargs)

    def get_sources(self):
        if self._config is None:
            return []
        return self._config["sources"]

    def get_plots(self):
        if self._config is None:
            return []
        return self._config["plots"]

    def enable_plots(self, *identifiers):
        self.__initialise()
        enable_all = "all" in identifiers
        for c in self._config["plots"]:
            if enable_all or c["identifier"] in identifiers:
                c["enable"] = True

def configure_from_sources(sources, labels=None):
    if labels and len(sources) != len(labels):
        CONFIG_LOGGER.critical("Need same number of sources and labels, %d vs. %d", len(source), len(labels))
    extract_funcs = (extract_from_source,)
    config = ConfigInterface()
    for i, (s, l) in enumerate(zip(sources, labels)):
        batches = None
        for ef in extract_funcs:
            batches = ef(s)
            if batches:
                break
        if batches is None:
            CONFIG_LOGGER.error("Cannot extract anything from source")
            continue

        for b in batches:
            b["label"] = l
            b["identifier"] = f"{b['identifier']}_{i}"
            config.add_data_source(**b)

    return config

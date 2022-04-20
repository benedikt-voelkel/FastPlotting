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

    def get_source(self, identifier):
        for batch in self.get_sources():
            if batch["identifier"] == identifier:
                return batch
        return None

    def get_plots(self):
        if self._config is None:
            return []
        return self._config["plots"]

    def reset_plots(self):
        self.__initialise()
        self._config["plots"] = []

    def enable_plots(self, *identifiers):
        """En- or diables plots

        Args:
            identifiers: iterable
                can be strings to JSON or plot's identifier (latter takes precedence, in particular "all" is specified)
        """
        self.__initialise()
        enable_all = "all" in identifiers
        enable_identifiers = []
        if not enable_all:
            for i in identifiers:
                from_json = parse_json(i)
                if not from_json:
                    enable_identifiers.append(i)
                    continue
                for ij in from_json.get("enable", []):
                    enable_identifiers.append(ij)

        n_enabled = 0
        for c in self._config["plots"]:
            if enable_all or c["identifier"] in enable_identifiers:
                c["enable"] = True
                n_enabled += 1
                CONFIG_LOGGER.debug("Enabling plot %s", c["identifier"])
                continue
            c["enable"] = False
        if not n_enabled:
            CONFIG_LOGGER.warning("No plots were enabled")

    def print_sources(self):
        text = "# SOURCES #"
        text = "#" * len(text) + "\n" + text + "\n" + "#" * len(text) + "\n"
        print(text)
        for s in self.get_sources():
            print(f"  {s['identifier']}")
        print("\n")

    def print_plots(self):
        text = "# PLOTS #"
        text = "#" * len(text) + "\n" + text + "\n" + "#" * len(text) + "\n"
        print(text)
        for s in self.get_plots():
            print(f"  {s['identifier']}, enabled: {s['enable']}")
        print("\n")

def configure_from_sources(sources, labels=None, **kwargs):
    if not sources:
        CONFIG_LOGGER.error("There are no sources to configure from")
        return ConfigInterface()
    if not labels:
        labels = [str(i) for i, _ in enumerate(sources)]
    if labels and len(sources) != len(labels):
        CONFIG_LOGGER.critical("Need same number of sources and labels, %d vs. %d", len(source), len(labels))
    extract_funcs = (extract_from_source,)
    config = ConfigInterface()
    input_config_path = kwargs.pop("input_config_path", None)
    if input_config_path:
        config.read(input_config_path)
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
            b["identifier"] = f"{b['identifier']}"
            config.add_data_source(**b)

    return config

def read_config(path):
    config = ConfigInterface()
    config.read(path)
    return config

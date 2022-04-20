import sys
from os.path import join, dirname, realpath
import importlib.util
from glob import glob

from fast_plotting.config import read_config, configure_from_sources
from fast_plotting.plot.utils import plot_auto, add_plot_for_each_source
from fast_plotting.registry import DataRegistry

path = dirname(realpath(__file__))
module_name = "common_test_utils"
spec = importlib.util.spec_from_file_location(module_name, join(path, f"{module_name}.py"))
common_test_utils = importlib.util.module_from_spec(spec)
sys.modules[module_name] = common_test_utils
spec.loader.exec_module(common_test_utils)

from common_test_utils import make_root, change_test_dir

def test_make_plot_from_source(change_test_dir):
    file_name = make_root()
    passed = True
    plot_output_dir = "plots_output_test_make_plot_from_source"
    #try:
    config = configure_from_sources((file_name,), ("label",))
    add_plot_for_each_source(config)
    config.enable_plots("all")
    # registry = DataRegistry()
    # registry.read_from_config(config)
    plot_auto(config, plot_output_dir)
    plot_auto(config, plot_output_dir, True)
    n_plots_config = len(config.get_plots())
    n_plots_saved = len(glob(f"{plot_output_dir}/*.png"))
    passed = n_plots_config + 1 == n_plots_saved
    # except:
    #     passed = False
    assert passed

import sys
from os.path import join, dirname, realpath, exists
import importlib.util
from glob import glob

from fast_plotting.config import configure_from_sources
from fast_plotting.metrics.metrics import compute_metrics, print_metrics
from fast_plotting.registry import DataRegistry

path = dirname(realpath(__file__))
module_name = "common_test_utils"
spec = importlib.util.spec_from_file_location(module_name, join(path, f"{module_name}.py"))
common_test_utils = importlib.util.module_from_spec(spec)
sys.modules[module_name] = common_test_utils
spec.loader.exec_module(common_test_utils)

from common_test_utils import make_root, change_test_dir

METRIC_NAMES = ["integral", "chi2"]

def test_metrics(change_test_dir):
    file_name_1 = make_root(1)
    file_name_2 = make_root(2)

    config_1 = configure_from_sources([file_name_1])
    config_2 = configure_from_sources([file_name_2])
    reg_1 = DataRegistry()
    reg_2 = DataRegistry()
    reg_1.read_from_config(config_1, load_all=True)
    reg_2.read_from_config(config_2, load_all=True)
    identifiers = [b["identifier"] for b in config_1.get_sources()]

    metrics = {}
    for i in identifiers:
        input = [reg_1.get(i), reg_2.get(i)]
        compute_metrics(input, METRIC_NAMES, True, add_to_metrics=metrics)
    print_metrics(metrics, format="json")

    passed = exists("metrics.json")

    assert passed

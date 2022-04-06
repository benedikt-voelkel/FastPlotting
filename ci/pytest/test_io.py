import sys
from os.path import join, dirname, realpath
import importlib.util

from fast_plotting.config import read_config, configure_from_sources

path = dirname(realpath(__file__))
module_name = "common_test_utils"
spec = importlib.util.spec_from_file_location(module_name, join(path, f"{module_name}.py"))
common_test_utils = importlib.util.module_from_spec(spec)
sys.modules[module_name] = common_test_utils
spec.loader.exec_module(common_test_utils)

from common_test_utils import make_root, change_test_dir

JSON_TEST_FILE = join(path, "test.json")

def test_read_sources(change_test_dir):
    passed = True
    try:
        config = read_config(JSON_TEST_FILE)
        config.print_sources()
    except:
        passed = False
    assert passed


def test_make_config_from_source(change_test_dir):
    file_name = make_root()
    passed = True
    try:
        config = configure_from_sources((file_name,), ("label",))
        config.write("config.json")
    except:
        passed = False
    assert passed

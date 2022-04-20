import pytest
from os.path import dirname, realpath, exists, join
from os import makedirs

from ROOT import TFile, TList, TH1F, TH2F

ROOT_TEST_FILE_NAME = "test_io.root"

@pytest.fixture(autouse=True)
def change_test_dir(request, monkeypatch):
    run_tests_dir = "pytest_artifacts"
    this_dir = dirname(realpath(__file__))
    # This is where we want to run, potentially there is more elegant solution for defining the cwd for the tests
    run_tests_dir = join(this_dir, "..", "..", run_tests_dir)
    if not exists(run_tests_dir):
        makedirs(run_tests_dir)
    monkeypatch.chdir(run_tests_dir)

def make_root(suffix=None):
    test_file_name = ROOT_TEST_FILE_NAME
    if suffix:
        test_file_name = test_file_name[:-5]
        test_file_name += f"_{suffix}.root"
    file = TFile(test_file_name, "RECREATE")

    # make a dir1
    dir1 = file.mkdir("dir1")
    dir1.cd()
    # filled with some histograms and to be written to dir1
    l = TList()
    l.SetName("list")

    for i in range(3):
        h = TH1F(f"hist_1_{i}", "", 100, -5, 5)
        h.FillRandom("gaus", 10000)
        l.Add(h)
    dir1.WriteTObject(l)
    l.Clear()

    # add histograms simply to directory
    for i in range(3):
        h = TH1F(f"hist_2_{i}", "", 100, -5, 5)
        h.FillRandom("gaus", 10000)
        h.Write()

    # make more directories
    for i in range(3):
        dirN = file.mkdir(f"dir_{i+2}")
        dirN.cd()
        # add histograms simply to directory
        for j in range(3):
            h = TH1F(f"hist_3_{i}_{j}", "", 100, -5, 5)
            h.FillRandom("gaus", 10000)
            h.Write()

    # make directory insides another directory
    dir_last = file.mkdir("dir_last")
    dir_last.cd()
    dir_last_last = dir_last.mkdir("dir_last_last")
    dir_last_last.cd()
    # add histograms simply to directory
    for i in range(3):
        h = TH2F(f"hist_4_{i}", "", 100, -5, 5, 100, -5, 5)
        h.FillRandom("gaus", 10000)
        h.Write()

    file.Close()

    return test_file_name

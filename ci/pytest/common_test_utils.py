from ROOT import TFile, TList, TH1F

ROOT_TEST_FILE_NAME = "test_io.root"

def make_root(suffix=None):
    test_file_name = ROOT_TEST_FILE_NAME
    if suffix:
        test_file_name += f"_{suffix}"
    file = TFile(test_file_name, "RECREATE")

    # make a dir1
    dir1 = file.mkdir("dir1")
    dir1.cd()
    # filled with some histograms and to be written to dir1
    l = TList()
    l.SetName("list")

    for i in range(10):
        h = TH1F(f"hist_{i}", "", 100, -5, 5)
        h.FillRandom("gaus", 10000)
        l.Add(h)
    dir1.WriteTObject(l)

    # add histograms simply to directory
    for i in range(10):
        h = TH1F(f"hist_{i}", "", 100, -5, 5)
        h.FillRandom("gaus", 10000)
        h.Write()

    # make more directories
    for i in range(10):
        dirN = file.mkdir(f"dir_{i+2}")
        dirN.cd()
        # add histograms simply to directory
        for i in range(10):
            h = TH1F(f"hist_{i}", "", 100, -5, 5)
            h.FillRandom("gaus", 10000)
            h.Write()

    dir_last = file.mkdir("dir_last")
    dir_last.cd()
    dir_last_last = dir_last.mkdir("dir_last_last")
    dir_last_last.cd()
    # add histograms simply to directory
    for i in range(10):
        h = TH1F(f"hist_{i}", "", 100, -5, 5)
        h.FillRandom("gaus", 10000)
        h.Write()

    file.Write()
    file.Close()

    return test_file_name

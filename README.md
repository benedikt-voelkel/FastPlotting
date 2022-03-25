# README

## Requirements

To fully make use of this, `ROOT` Python bindings are required since at the moment, only the `ROOT`
backend is implemented for actual plotting.

## Setup

Set up via
```bash
pip install -e .
```

As usual, it is recommended to do so inside a Python `virtualenv` since this package is not official (yet).

**Note** that during the setup there would be no warning on whether or not `ROOT` is installed on your system.

## Quick start
If you have a ROOT file where there is at least one 1d-histogram inside, do
```bash
python <path/to>/FastPlotting/fast_plotting/run.py configure -f <file.root> -l <someLabel> --single
```
The `--single` makes sure that one plot per histogram is configured. Now, there should be a file called `config.json`. It has 2 top keys which are `sources` and `plots`. Just go to the second one and find a plot you want to enable. Set the field `"enable": true`, save and close the file. Now run
```bash
python <path/to>/FastPlotting/fast_plotting/run.py plot config.json
```
and there should be a plot saved to disk.

Now, if you have a second (or more) ROOT file(s) that has the same internal structure, but somehow different version(s), you can do
```bash
python <path/to>/FastPlotting/fast_plotting/run.py configure -f <file_1.root> <file_2.root> ... <file_N.root> -l <someLabel_1>  <someLabel_2> ... <someLabel_N> --overlay
```
Now enable the ones you want to have plotted again and run
```bash
python <path/to>/FastPlotting/fast_plotting/run.py plot config.json
```

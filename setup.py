from setuptools import setup, find_packages
from codecs import open
from os import path
from glob import glob

setup(
  name='FastPlotting',

  # LAST-TAG is a placeholder. Automatically replaced at deploy time with the right tag
  version='0.0.1',

  description='A plotting framework',

  # Long description from Markdown -- https://dustingram.com/articles/2018/03/16/markdown-descriptions-on-pypi
  # Filter out lines that look like GitHub "badges"
  long_description="\n".join([ line for line in open('README.md').read().split("\n") if not line.startswith("[![") ]),
  long_description_content_type='text/markdown',

  url='https://github.com/benedikt-voelkel/FastPlotting',
  author='Benedikt Volkel',
  author_email='benedikt.volkel@cern.ch',
  #license='GPL',
  classifiers=[

    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 4 - Beta',

    # Indicate who your project is intended for
    'Intended Audience :: Education',
    'Topic :: Scientific/Engineering :: Physics',

    # Pick your license as you wish (should match "license" above)
    #'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 3',
    ],

  # What does your project relate to?
  keywords='plotting',

  # You can just specify the packages manually here if your project is
  # simple. Or you can use find_packages().
  packages=find_packages(),

  # Alternatively, if you want to distribute just a my_module.py, uncomment
  # this:
  #   py_modules=["my_module"],

  # List run-time dependencies here.  These will be installed by pip when
  # your project is installed. For an analysis of "install_requires" vs pip's
  # requirements files see:
  # https://packaging.python.org/en/latest/requirements.html
  install_requires=["numpy", "matplotlib"],

  python_requires='>=3.6',

  # List additional groups of dependencies here (e.g. development
  # dependencies). You can install these using the following syntax,
  # for example:
  # $ pip install -e .[dev,test]
  extras_require={
    "test": ["pylint>=2.6.2", "pytest>=6.2.2"]
  },

  # If there are data files included in your packages that need to be
  # installed, specify them here. Note that you need to specify those files in
  # MANIFEST.in as well, since Python tools behave inconsistently
  # include_package_data=True,
  # package_data={ "hfplot.data_1": [ "data.yml",
  #                                   "data.yml",
  #                                   "data.yml",
  #                                   "data.yml",
  #                                   "data.yml" ],
  #                "hfplot.data_2": [ "data.yml",
  #                                   "data.yml" ] },

  # Although 'package_data' is the preferred approach, in some case you may
  # need to place data files outside of your packages. See:
  # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
  # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
  data_files=[],

  # To provide executable scripts, use entry points in preference to the
  # "scripts" keyword. Entry points provide cross-platform support and allow
  # pip to create the appropriate form of executable for the target platform.
  # See: https://chriswarrick.com/blog/2014/09/15/python-apps-the-right-way-entry_points-and-scripts/


  # entry_points={
  #     "console_scripts": [ "hfplot = hfplot.cli:main" ]
  # }
)

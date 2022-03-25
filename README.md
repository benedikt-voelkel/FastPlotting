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

## Additional setup for testing

In order to test the code and check the style, `pytest` and `pylint` have to be installed. This can be done via
```bash
pip install -e .[test]
```

### Checking the coding style

**NOTE** This is not enforced at the moment and there might still be places where a review is needed.

However, in case you want to implement new code, please make sure that at least the new implementation complies with what `pylint` tells you. To check individual files please run
```bash
pylint path/to/file
```
from somewhere in the repository.

### Test the new implementations

The basic functionality of the code can be checked by running
```bash
ci/run-tests.sh --tests pytest
```
If that fails, most likely your developments broke something. Please make sure that these tests pass before you open a PR.

## Examples

You can immediately jump into the [examples](./examples) and have a look. If you want further technical explanations, just keep reading.

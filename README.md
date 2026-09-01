[![Latest Version](https://img.shields.io/pypi/v/betwixt?label=pypi-version&logo=python&style=plastic)](https://pypi.org/project/betwixt/)
[![Python Versions](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fdusktreader%2Fbetwixt%2Fmain%2Fpyproject.toml&style=plastic&logo=python&label=python-versions)](https://www.python.org/)
[![Build Status](https://github.com/dusktreader/betwixt/actions/workflows/main.yml/badge.svg)](https://github.com/dusktreader/betwixt/actions/workflows/main.yml)
[![Documentation Status](https://github.com/dusktreader/betwixt/actions/workflows/docs.yml/badge.svg)](https://dusktreader.github.io/betwixt/)

# Betwixt

_Betwixt your data models lives a new, delcarative mapping layer._

Betwixt maps peer boundary models without coupling them to one another. The core package supports dataclasses; Pydantic
and SQLAlchemy adapters are opt-in extras.



## Super-quick start

Requires Python 3.12 to 3.14.

Install the base package through pip:

```shell
pip install betwixt
```

Install optional adapter boundaries when needed:

```shell
pip install "betwixt[pydantic]"
pip install "betwixt[sqlalchemy]"
```


## Documentation

Dig into the docs on the [Betwixt homepage](https://dusktreader.github.io/betwixt).

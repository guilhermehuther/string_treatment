[![Downloads](https://static.pepy.tech/badge/string_treatment)](https://pepy.tech/project/string_treatment) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Overview

**string_treatment** is a library for cleaning and adjusting data with inconsistency.

# Installation
Install the latest stable version from PyPI:

```shell
pip install string-treatment
```

# Included Functions

**String treatment:**

* treat_referenced
* treat_unreferenced

# Quick start
**With reference list**
``` python
>>> from string_treatment import treat_referenced
>>> list_of_reference = ['João Pessoa/PB']
>>> data_with_inconsistency = ['João Pessoa PB', 'Joao pessoa--PB', 'joa pssoa(pb)']
>>> treat_referenced(data_with_inconsistency, list_of_reference)
['João Pessoa PB', 'João Pessoa PB', 'João Pessoa PB']
```

**Without reference list**
``` python
>>> from string_treatment import treat_unreferenced
>>> data_with_inconsistency = ['João Pessoa PB', 'Joao pessoa--PB', 'joa pssoa(pb)']
>>> treat_unreferenced(data_with_inconsistency)
['João Pessoa PB', 'João Pessoa PB', 'João Pessoa PB']
```

# Usage
To learn about how to use this library and examples,
[visit the User Guide, which is a Jupyter notebook](https://github.com/guilhermehuther/string_treatment/blob/main/guide.ipynb).

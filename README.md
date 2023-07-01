[![Downloads](https://static.pepy.tech/personalized-badge/requests?period=total&units=international_system&left_color=black&right_color=blue&left_text=Downloads)](https://pepy.tech/project/requests)

# Overview

**string_treatment** is a library for cleaning and adjusting data with inconsistency.

# Installation
Install the latest stable version from PyPI:

```shell
pip install string-treatment
```

# Quick start
#### With reference list
``` python
>>> from string_treatment import string_treatment as st
>>> list_of_reference = ['João Pessoa/PB']
>>> data_with_inconsistency = ['João Pessoa PB', 'Joao pessoa--PB', 'joa pssoa(pb)']
>>> st.treat_referenced(data_with_inconsistency, list_of_reference)
['João Pessoa PB', 'João Pessoa PB', 'João Pessoa PB']
```

#### Without reference list
``` python
>>> from string_treatment import string_treatment as st
>>> data_with_inconsistency = ['João Pessoa PB', 'Joao pessoa--PB', 'joa pssoa(pb)']
>>> st.treat_unreferenced(data_with_inconsistency)
['João Pessoa PB', 'João Pessoa PB', 'João Pessoa PB']
```

# Usage
To learn about how to use this library and examples,
[visit the User Guide, which is a Jupyter notebook](https://github.com/guilhermehuther/string_treatment/blob/main/guide.ipynb).

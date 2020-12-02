# kshingle
Utility functions to split a string into (character-based) k-shingles, shingle sets, sequences of k-shingles.

## Usage

### Convert a string to a sequences of shingles
Using the `k` parameter

```py
import kshingle as ks
shingles = ks.shingling_k("aBc DeF", k=3)
# [['a', 'B', 'c', ' ', 'D', 'e', 'F'],
#  ['aB', 'Bc', 'c ', ' D', 'De', 'eF'],
#  ['aBc', 'Bc ', 'c D', ' De', 'DeF']]
```

Using a range for `k`

```py
import kshingle as ks
shingles = ks.shingling_range("aBc DeF", n_min=2, n_max=3)
# [['aB', 'Bc', 'c ', ' D', 'De', 'eF'],
#  ['aBc', 'Bc ', 'c D', ' De', 'DeF']]
```

Using a specific list of k values

```py
import kshingle as ks
shingles = ks.shingling_list("aBc DeF", klist=[2, 5])
# [['aB', 'Bc', 'c ', ' D', 'De', 'eF'],
#  ['aBc D', 'Bc De', 'c DeF']]
```

## Appendix

### Installation
The `kshingle` [git repo](http://github.com/ulf1/kshingle) is available as [PyPi package](https://pypi.org/project/kshingle)

```
pip install kshingle
pip install git+ssh://git@github.com/ulf1/kshingle.git
```


### Commands
Install a virtual environment

```
python3.6 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
pip install -r requirements-dev.txt --no-cache-dir
```

(If your git repo is stored in a folder with whitespaces, then don't use the subfolder `.venv`. Use an absolute path without whitespaces.)

Python commands

* Check syntax: `flake8 --ignore=F401 --exclude=$(grep -v '^#' .gitignore | xargs | sed -e 's/ /,/g')`
* Run Unit Tests: `pytest`
* Upload to PyPi with twine: `python setup.py sdist && twine upload -r pypi dist/*`

Clean up 

```
find . -type f -name "*.pyc" | xargs rm
find . -type d -name "__pycache__" | xargs rm -r
rm -r .pytest_cache
rm -r .venv
```


### Support
Please [open an issue](https://github.com/ulf1/kshingle/issues/new) for support.


### Contributing
Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). Create a branch, add commits, and [open a pull request](https://github.com/ulf1/kshingle/compare/).

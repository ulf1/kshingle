[![PyPI version](https://badge.fury.io/py/kshingle.svg)](https://badge.fury.io/py/kshingle)
[![DOI](https://zenodo.org/badge/317843267.svg)](https://zenodo.org/badge/latestdoi/317843267)

# kshingle
Utility functions to split a string into (character-based) k-shingles, shingle sets, sequences of k-shingles.

## Install package

```sh
pip install kshingle>=0.4.1
```


## Usage for MinHashing

### Generate Shingle Sets
For algorithms like MinHash (e.g. [datasketch](https://github.com/ekzhu/datasketch) package) a document (i.e. a string) must be split into a set of unique shingles.

```py
import kshingle as ks
shingles = ks.shingleset_k("abc", k=3)
# {'a', 'ab', 'abc', 'b', 'bc', 'c'}
```

```py
import kshingle as ks
shingles = ks.shingleset_range("abc", 2, 3)
# {'ab', 'abc', 'bc', 'c'}
```

```py
import kshingle as ks
shingles = ks.shingleset_list("abc", [1, 3])
# {'a', 'abc', 'b', 'c'}
```


### Wildcard Shingle Sets
Typos can lead to rare shingles, that don't match with the correct spelling. 
The longer the shingled text, the less important the effect of typos. 
However, short text strings will produce less shingles, i.e. the variance of the similarity due to typos is much higher for short text strings than for large text documents.
In order to smooth this effect, we can generate variants of a specfic shingle by replacing characters with a wildcard characters (e.g. special unicode characters such as `U+FFFF`).

Example: 
With `k=5` the document `"aBc DeF"` would result in 25 unique shingles without assumned typos.
For each of these shingles, we enumerate all variants of up to 2 typos.
This leads to a total of 152 unique shingles with no typo, 1 typo, and 2 typos.

```py
import kshingle as ks
shingles = ks.shingleset_k("aBc DeF", k=5)  # -> 25 shingles
shingles = shingles.union(
    ks.wildcard_shinglesets(shingles, n_max_wildcards=2))  # -> 152 shingles
```


### datasketch usage

```py
import datasketch
import kshingle as ks

# Enable wildcard variants and check the results
with_wildcard = False

s1 = ks.shingleset_k("Die Zeitung wird zugestellt.", k=5)
s2 = ks.shingleset_k("Der Bericht wird zugestellt", k=5)

if with_wildcard:
    s1 = s1.union(ks.wildcard_shinglesets(s1, 2))
    s2 = s1.union(ks.wildcard_shinglesets(s2, 2))

m1 = datasketch.MinHash(num_perm=128)
for s in s1:
    m1.update(s.encode('utf8'))

m2 = datasketch.MinHash(num_perm=128)
for s in s2:
    m2.update(s.encode('utf8'))

m1.jaccard(m2)
```


## Usage for Input Sequences

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


### Identify Vocabulary of unique shingles

```py
import kshingle as ks
data = [
    'Cerato­saurus („Horn-Echse“) ist eine Gattung theropoder Dino­saurier aus dem Ober­jura von Nord­ame­rika und Europa.',
    'Charak­teris­tisch für diesen zwei­beini­gen Fleisch­fresser waren drei markante Hörner auf dem Schädel sowie eine Reihe kleiner Osteo­derme (Haut­knochen­platten), die über Hals, Rücken und Schwanz ver­lief.',
    'Er ist der namens­gebende Vertre­ter der Cerato­sauria, einer Gruppe basaler (ursprüng­licher) Thero­poden.'
]
shingled = [ks.shingling_k(s, k=6) for s in data]
VOCAB = ks.identify_vocab(
    shingled, sortmode='log-x-length', n_min_count=2, n_max_vocab=20)
print(VOCAB)
```

### Upsert a word to VOCAB

```py
import kshingle as ks
VOCAB = ['a', 'b']

# insert because "[UNK]" doesn't exist
VOCAB, idx = ks.upsert_word_to_vocab(VOCAB, "[UNK]")
print(idx, VOCAB)
# 2 ['a', 'b', '[UNK]']

# don't insert because "[UNK]" already exists
VOCAB, idx = ks.upsert_word_to_vocab(VOCAB, "[UNK]")
print(idx, VOCAB)
# 2 ['a', 'b', '[UNK]']
```


### Encode sequences of shingles

```py
import kshingle as ks
data = ['abc d abc de abc def', 'abc defg abc def gh abc def ghi']
shingled = [ks.shingling_k(s, k=5) for s in data]
VOCAB = ks.identify_vocab(shingled, n_max_vocab=10)
VOCAB, unkid = ks.upsert_word_to_vocab(VOCAB, "[UNK]")
# Encode all sequences
encoded = ks.encoded_with_vocab(shingled, VOCAB, unkid)
```


### Find k
For bigger `k` values, the generate longer shingles that occur less frequent.
And less frequent shingles might be excluded in `ks.identify_vocab`.
As a result at some upper `k` value the generated sequences only contains `[UNK]` encoded elements.
The function `ks.shrink_k_backwards` identifies `k` values that generate sequences that contain at least one encoded shingle across all examples.

```py
import kshingle as ks
data = ['abc d abc de abc def', 'abc defg abc def gh abc def ghi']

# Step 1: Build a VOCAB
shingled = [ks.shingling_k(s, k=9) for s in data]
VOCAB = ks.identify_vocab(shingled, n_max_vocab=10)
VOCAB, unkid = ks.upsert_word_to_vocab(VOCAB, "[UNK]")
encoded = ks.encoded_with_vocab(shingled, VOCAB, unkid)
# Identify k's that are actually used
klist = ks.shrink_k_backwards(encoded, unkid)

# Step 2: Shingle sequences again
shingled = [ks.shingling_list(s, klist=klist) for s in data]
encoded = encoded_with_vocab(shingled, VOCAB, unkid)
# ...
```

### Padding
Padding should be done with Keras `pad_sequences`

```py
from tensorflow.keras.preprocessing.sequence import pad_sequences
import torch
import kshingle as ks

# Add [PAD] token
VOCAB, padidx = ks.upsert_word_to_vocab(VOCAB, "[PAD]")

# Pad each example with Keras
cfg = {'maxlen': 150, 'dtype': 'int32', 'padding': 'pre', 'truncating': 'pre', 'value': padidx}
padded = [pad_sequences(ex, **cfg).transpose() for ex in encoded]

# Convert to Pytorch
padded = torch.LongTensor(padded)
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

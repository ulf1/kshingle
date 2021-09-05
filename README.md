[![PyPI version](https://badge.fury.io/py/kshingle.svg)](https://badge.fury.io/py/kshingle)
[![DOI](https://zenodo.org/badge/317843267.svg)](https://zenodo.org/badge/latestdoi/317843267)
[![kshingle](https://snyk.io/advisor/python/kshingle/badge.svg)](https://snyk.io/advisor/python/kshingle)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/ulf1/kshingle.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/ulf1/kshingle/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/ulf1/kshingle.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/ulf1/kshingle/context:python)

# kshingle
Utility functions to split a string into character-level k-shingles, shingle sets, sequences of k-shingles.

The package `kshingle` can be deployed for the following use cases:

- [Character-level Shingling for MinHash/LSH](#usage-for-minhashing) : The result is a set of unique shingles for each document.
- [Transform text into Input Sequences for NNs](#usage-for-input-sequences) : The result is input sequence with k features.


## Install package

```sh
pip install "kshingle>=0.8.2"
```


## Usage for MinHashing
Please note that the package `kshingle` only addresses character-level shingles, and **not** combining word tokens (n-grams, w-shingling).

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


### Utility functions
```py
import kshingle as ks
metric = ks.jaccard_strings("Bericht", "berichten", k=5)
# 0.5128205128205128
```

### References
- A. Z. Broder, “On the resemblance and containment of documents,” in Proceedings. Compression and Complexity of SEQUENCES 1997 (Cat. No.97TB100171), Salerno, Italy, 1998, pp. 21–29, doi: [10.1109/SEQUEN.1997.666900](https://doi.org/10.1109/SEQUEN.1997.666900)
- Ch. 3 in: J. Leskovec, A. Rajaraman, and J. D. Ullman, Mining of Massive Datasets, 2nd ed. Cambridge: Cambridge University Press, 2014. URL: [http://infolab.stanford.edu/~ullman/mmds/book.pdf](http://infolab.stanford.edu/~ullman/mmds/book.pdf)
- “MinHash,” Wikipedia. Apr. 17, 2021, Accessed: May 01, 2021. Available: [https://en.wikipedia.org/w/index.php?title=MinHash&oldid=1018264865](https://en.wikipedia.org/w/index.php?title=MinHash&oldid=1018264865).


## Usage for Input Sequences

### Convert a string to a sequences of shingles
Using the `k` parameter

```py
import kshingle as ks
shingles = ks.shingleseqs_k("aBc DeF", k=3)
# [['a', 'B', 'c', ' ', 'D', 'e', 'F'],
#  ['aB', 'Bc', 'c ', ' D', 'De', 'eF'],
#  ['aBc', 'Bc ', 'c D', ' De', 'DeF']]
```

Using a range for `k`

```py
import kshingle as ks
shingles = ks.shingleseqs_range("aBc DeF", n_min=2, n_max=3)
# [['aB', 'Bc', 'c ', ' D', 'De', 'eF'],
#  ['aBc', 'Bc ', 'c D', ' De', 'DeF']]
```

Using a specific list of k values

```py
import kshingle as ks
shingles = ks.shingleseqs_list("aBc DeF", klist=[2, 5])
# [['aB', 'Bc', 'c ', ' D', 'De', 'eF'],
#  ['aBc D', 'Bc De', 'c DeF']]
```


### Padding
The functions `shingleseqs_k`, `shingleseqs_range`, and `shingleseqs_list` can pad the sequence with a `placeholder` element. The `padding` modes are 

- `center` : Pad on both sides (The `evenpad='pre' | 'post` parameter is only available for `padding='center'`, and applied on sequences with even `n`-shingles)
- `pre` : Pad at the beginning of the sequence
- `post` : Pad at the end of sequence


```py
import kshingle as ks
shingles = ks.shingleseqs_list("1234567", k=5, padding='center', evenpad='pre', placeholder='x')
[[f"{s:^5}" for s in seq] for seq in shingles]
```

```
[['  1  ', '  2  ', '  3  ', '  4  ', '  5  ', '  6  ', '  7  '],
 ['  x  ', ' 12  ', ' 23  ', ' 34  ', ' 45  ', ' 56  ', ' 67  '],
 ['  x  ', ' 123 ', ' 234 ', ' 345 ', ' 456 ', ' 567 ', '  x  '],
 ['  x  ', '  x  ', '1234 ', '2345 ', '3456 ', '4567 ', '  x  '],
 ['  x  ', '  x  ', '12345', '23456', '34567', '  x  ', '  x  ']]
```


### Identify Vocabulary of unique shingles

```py
import kshingle as ks
data = [
    'Cerato­saurus („Horn-Echse“) ist eine Gattung theropoder Dino­saurier aus dem Ober­jura von Nord­ame­rika und Europa.',
    'Charak­teris­tisch für diesen zwei­beini­gen Fleisch­fresser waren drei markante Hörner auf dem Schädel sowie eine Reihe kleiner Osteo­derme (Haut­knochen­platten), die über Hals, Rücken und Schwanz ver­lief.',
    'Er ist der namens­gebende Vertre­ter der Cerato­sauria, einer Gruppe basaler (ursprüng­licher) Thero­poden.'
]
shingled = [ks.shingleseqs_k(s, k=6) for s in data]
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
shingled = [ks.shingleseqs_k(s, k=5) for s in data]
VOCAB = ks.identify_vocab(shingled, n_max_vocab=10)
VOCAB, unkid = ks.upsert_word_to_vocab(VOCAB, "[UNK]")
# Encode all sequences
encoded = ks.encode_with_vocab(shingled, VOCAB, unkid)
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
shingled = [ks.shingleseqs_k(s, k=9) for s in data]
VOCAB = ks.identify_vocab(shingled, n_max_vocab=10)
VOCAB, unkid = ks.upsert_word_to_vocab(VOCAB, "[UNK]")
encoded = ks.encode_with_vocab(shingled, VOCAB, unkid)
# Identify k's that are actually used
klist = ks.shrink_k_backwards(encoded, unkid)

# Step 2: Shingle sequences again
shingled = [ks.shingleseqs_list(s, klist=klist) for s in data]
encoded = encode_with_vocab(shingled, VOCAB, unkid)
# ...
```


## Collectively Exhaustive Wildcard Shingling (CEWS)
CEWS is a selection algorithm for k-shingles with wildcards to build a vocabulary list.


### Extract and count shingles
First, build a database `db` with shingles as keys and the occurence within a corpus as values.

```py
from collections import Counter
import kshingle as ks
import itertools

# load the corpora
docs = ["...", "..."]

# loop over all documents
db = Counter()
for doc in docs:
    # extract all shingles of different k-length (no wildcards!)
    shingles = ks.shingleseqs_k(doc, k=5)  # bump it up to 8
    # count all unique shingles, and add the result
    db += Counter(itertools.chain(*shingles))

db = dict(db)
```

### Extra: Augment text by adding typological errors
In order to increase the generalizibility of a trained ML model,
we can use text augmentation to produce possible edge case of errornous text.
High quality corpora try to avoid such errors,
and corpora based laymen's text might not include each possible edge case. 

```py
import augtxt.keyboard_layouts as kbl
from augtxt.augmenters import wordaug
import numpy as np
from collections import Counter

# Augmentation settings: Probability of typological errors
settings = [
    {'p': 0.50, 'fn': 'typo.drop_n_next_twice', 'args': {'loc': ['m', 'e'], 'keep_case': [True, False]} },
    {'p': 0.50, 'fn': 'typo.swap_consecutive', 'args': {'loc': ['m', 'e'], 'keep_case': [True, False]} },
    {'p': 0.25, 'fn': 'typo.pressed_twice', 'args': {'loc': 'u', 'keep_case': [True, False]} },
    {'p': 0.25, 'fn': 'typo.drop_char', 'args': {'loc': ['m', 'e'], 'keep_case': [True, False]} },
    {'p': 0.25, 'fn': 'typo.pressed_shiftalt', 'args': {'loc': ['b', 'm'], 'keymap': kbl.macbook_us, 'trans': kbl.keyboard_transprob}},
]
# Number of augmentation rounds (i.e. the total count will be 10-1000x larger)
n_augm_rounds = 10
# maximum percentage of augmentions
pct_augmented = 0.1 
pct_augmented *= (1.0 + np.prod([cfg['p'] for cfg in settings]))
# Count factor for original shingle
n_factor_original = int((n_augm_rounds / pct_augmented) * (1 - pct_augmented))
# reproducibility
np.random.seed(seed=42)

# loop over shingle frequency database (`db`)
db2 = Counter()
for original in db.keys():
    augmented = [wordaug(original, settings) for _ in range(n_augm_rounds)]
    # count all unique augmented shingles, and add the result
    db2 += Counter(augmented)
    # count the original shingle
    db2[original] += n_factor_original

db2 = dict(db2)
len(db2)
```


### Select the shingles (CEWS), create pattern list, and encode data

```py
# use `db` or `db2` (see above)
import kshingle as ks
memo = ks.cews(db2, threshold=0.9, min_count_split=10, max_wildcards=2)

# ensure that certain shingles are in the memoization cache
#memo = {k: db[k] for k in ["i.e.", "e.g."]}
#memo = ks.cews(db2, memo=memo, threshold=0.9, min_count_split=10, max_wildcards=2)

# Build a pattern list
PATTERNS = ks.shingles_to_patterns(memo, wildcard="?")
unkid = len(PATTERNS)
```

Finally, we can start to encode data

```py
# generate all shingles
shingled = [ks.shingleseqs_k(doc, k=5) for doc in docs]

# Encode data
encoded = ks.encode_with_patterns(shingled, PATTERNS, unkid)
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
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
pip install -r requirements-dev.txt --no-cache-dir
```

(If your git repo is stored in a folder with whitespaces, then don't use the subfolder `.venv`. Use an absolute path without whitespaces.)

Python commands

* Check syntax: `flake8 --ignore=F401 --exclude=$(grep -v '^#' .gitignore | xargs | sed -e 's/ /,/g')`
* Run Unit Tests: `pytest`

Publish

```sh
pandoc README.md --from markdown --to rst -s -o README.rst
python setup.py sdist 
twine upload -r pypi dist/*
```

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

__version__ = '0.7.0'

from .shingleseqs import (shingleseqs_k, shingleseqs_list, shingleseqs_range)
from .shingleset import (shingleset_k, shingleset_range, shingleset_list)
from .vocab import (
    identify_vocab, upsert_word_to_vocab, encode_with_vocab,
    shrink_k_backwards)
from .wildcard import wildcard_shinglesets
from .metrics import jaccard, jaccard_strings
from .cews import (
    expandshingle, cews, shingles_to_patterns, encode_with_patterns)

# deprecated
from .shingleseqs import (shingling_k, shingling_list, shingling_range)
from .vocab import encoded_with_vocab

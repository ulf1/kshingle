__version__ = '0.10.0'

from .shingleseqs import (shingleseqs_k, shingleseqs_list, shingleseqs_range)
from .shingleset import (shingleset_k, shingleset_range, shingleset_list)
from .vocab import (
    identify_vocab, upsert_word_to_vocab, encode_with_vocab,
    shrink_k_backwards)
from .wildcard import wildcard_shinglesets
from .metrics import jaccard, jaccard_strings
from .cews import (
    expandshingle,
    cews,
    shingleseqs_hashes,
    shingles_to_hashes,
    encode_multi_match
)
from .cews_cpu import cews_cpu, encode_with_patterns_cpu

from .pattern_encoding import (
    shingles_to_patterns,
    encode_with_patterns,
    encode_multi_match_corpus
)

# deprecated
from .vocab import encoded_with_vocab

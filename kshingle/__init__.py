from .shingling import (shingling_k, shingling_list, shingling_range)
from .shingleset import (shingleset_k, shingleset_range, shingleset_list)
from .vocab import (
    identify_vocab, upsert_word_to_vocab, encoded_with_vocab,
    shrink_k_backwards)
from .wildcard import wildcard_shinglesets
from .metrics import jaccard, jaccard_strings

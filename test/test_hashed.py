import kshingle as ks
import pytest
from collections import Counter
import itertools


def test21():
    # raw text
    text = "Die Kuh macht muh. Der Hund wufft herum."
    
    multiseq = ks.shingleseqs_hashes(text, k=4)

    # Build pattern list
    db = Counter()
    for doc in [text]:
        shingles = ks.shingleseqs_k(doc, k=4)  # bump it up to 8
        db += Counter(itertools.chain(*shingles))
    db = dict(db)
    memo = ks.cews(
        db, max_wildcards=1, min_samples_leaf=10, threshold=0.9)
    # Build a hashes list
    HASHES = ks.shingles_to_hashes(memo, wildcard='\uFFFF')
    unkid = sum([len(hashes) for hashes in HASHES.values()])

    # Encode sequences
    allseqs = ks.encode_multi_match(
        multiseq, num_matches=3, HASHES=HASHES, unkid=unkid)
    
    assert allseqs.shape[1] == 9

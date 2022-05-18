import re
from typing import Optional, Dict, List
import functools
import numpy as np
import itertools
from .shingleseqs import pad_shingle_sequence
import hashlib
import copy


def select_most_frequent_shingles(matches: List[str],
                                  db: Dict[str, int],
                                  min_samples_split: int,
                                  min_samples_leaf: int,
                                  threshold: float):
    """Select the most frequent shingles that matches the wildcard shingle

    Parameters:
    -----------
    matches : List[str]
        A list of shingles from the database (`db`) that matches the current
          wildcard shingle in the `expandshingle` function.

    db: dict
        Database with shingles as `key` and their frequencies/counts as `value`
          Assumptions:
          - Python's `dict` are automatically in alphabetic order but not key
              length, i.e. we still need to filter keys by length initially.
          - The database `db` is immutable.
          Preprocessing: Make sure that each shingle has a sufficient number of
            counts/frequencies, e.g. remove shingles that occur less than 20x.

    min_samples_split: int (Default: 2)
        If the combined frequency of all shingles covered by one wildcard
          shingle (count sum of the regex query results) is less than the
          specified minimum total frequency, then the recursion aborts.

    min_samples_leaf: int (Default: 1)
        Required number of counts in `db` to be added to the memo cached

    threshold: float (Default: 0.80)
        Replace max. `1.0 - threshold` of the least frequent shingles with
          the wildcard shingle.

    Returns:
    --------
    selected_shingles : List[str]
        The selected most frequent shingles

    residual_count : int
        The residual counts (of the unselected shingles) that will be
          assigned to the wildcard shingle in `expandshingle`

    Example:
    --------
        selected_shingles, residual_count = select_most_frequent_shingles(
            matches, db, min_samples_split, min_samples_leaf, threshold)
    """
    # read only matches
    candidates = [item for item in db.items() if item[0] in matches]

    # proceed if there at least 2 candidates
    if len(candidates) == 0:
        return [], 0
    if len(candidates) == 1:
        return [], candidates[0][1]

    # sort by descending frequency
    candidates = sorted(candidates, key=lambda item: -item[1])

    # compute total counts
    total = sum([val for _, val in candidates])

    if total < min_samples_split:
        return [], total

    # find most frequent (`val`) shingles (`key`) up to 90% of all matches
    # always ignore the least frequent shingle and use the wildcard version
    cumpct = 0.0
    cumcnt = 0
    selected = []
    for key, val in candidates[:-1]:
        if val >= min_samples_leaf:
            # abort if the sum of selected shingles reached threshold
            cumpct += val / total
            if cumpct > threshold:
                break
            # select shingle
            cumcnt += val
            selected.append(key)

    # done
    return selected, total - cumcnt


def expandshingle(s: str,
                  db: Dict[str, int],
                  memo: Optional[dict],
                  wildcard: Optional[str] = '\uFFFF',
                  max_wildcards: Optional[int] = 1,
                  min_samples_split: Optional[int] = 2,
                  min_samples_leaf: Optional[int] = 1,
                  threshold: Optional[float] = 0.8):
    """Recursive algorithm to select given k-shingles

    Parameters:
    -----------
    s: str
        A shingle, i.e. a string of text

    db: dict
        Database with shingles as `key` and their frequencies/counts as `value`
          Assumptions:
          - Python's `dict` are automatically in alphabetic order but not key
              length, i.e. we still need to filter keys by length initially.
          - The database `db` is immutable.
          Preprocessing: Make sure that each shingle has a sufficient number of
            counts/frequencies, e.g. remove shingles that occur less than 20x.

    memo: dict (default: {})
        Database for memoization, i.e. `memo[shingle]=count`. In case of the
          wildcarded shingle, the residual counts that are not covered by the
          selected set of shingles (Basically the `1 - p`).
        The keys in the memoization cache are selected shingles of the CEWS
          algorithm.

    wildcard: str  (Default: '\uFFFF')
        An unicode char that is not actually used by any natural language,
          or the text that you analyzing, e.g. U+FFFE or U+FFFF
          See https://en.wikipedia.org/wiki/Specials_(Unicode_block)

    max_wildcards: int (Default: 1)
        If an input string `s` contains more than the specified maximum
          number of wildcard characters, the recursion aborts.

    min_samples_split: int (Default: 2)
        If the combined frequency of all shingles covered by one wildcard
          shingle (count sum of the regex query results) is less than the
          specified minimum total frequency, then the recursion aborts.

    min_samples_leaf: int (Default: 1)
        Required number of counts in `db` to be added to the memo cached

    threshold: float (Default: 0.80)
        Replace max. `1.0 - threshold` of the least frequent shingles with
          the wildcard shingle.

    Returns:
    --------
    memo: dict
        The updated memoization cache.
    """
    # (0a) stop if the shingle reached the maximum number of wildcards
    if s.count(wildcard) >= max_wildcards:
        return memo
    # (0b) abort
    if min_samples_split < 1:
        raise Exception(
            f"min_samples_split={min_samples_split} but must greater equal 1.")

    # (1a) Prefix/Suffix Wildcards
    # - Expand on the left side (prefix wildcard) and right side (suffix w.)
    # - This will lengthen the shingle by 1 character (k+1)
    tmp = []
    tmp.append(f"{wildcard}{s}")   # "_[shingle]"
    tmp.append(f"{s}{wildcard}")   # "[shingle]_"

    # (1b) Infix Wildcard
    # - Check all wildcard variants of a shingle.
    # - This will NOT expand the length of the shingles directly
    n_len = len(s)
    if n_len >= 3:
        # never replace 1st and last with wildcard ("1")
        # and avoid consequtive wildcards at the left and right end
        off_start = 1 + int(s[0] == wildcard)
        off_end = 1 + int(s[-1] == wildcard)
        # create each infix wildcard combination
        for i in range(off_start, n_len - off_end):
            # Find all matches "[s1]_[s2]"
            tmp.append(f"{s[:i]}{wildcard}{s[(i + 1):]}")

    # (2a) Find all matches
    for snew in tmp:
        # memoization trick
        if snew not in memo:
            # regex search
            # reg = re.escape(snew).replace(wildcard, r"\w{1}")
            reg = r"\w{1}".join([re.escape(s) for s in snew.split(wildcard)])
            pat = re.compile(f"^{reg}$")
            matches = list(filter(pat.match, db.keys()))

            # (2b) Find and select the most frequent shingles
            selected_shingles, residual_count = select_most_frequent_shingles(
                matches, db, min_samples_split, min_samples_leaf, threshold)

            # (2c) Assign the counts of the unselected shingles to the new
            #  wildcard-shingle (`residual_count`), store it the database
            #  (`db`) and memoization cache (`memo`), and traverse to the next
            #  knot
            if residual_count >= min_samples_split:
                memo[snew] = residual_count
                memo = expandshingle(
                    snew, db=db, memo=memo,
                    wildcard=wildcard,
                    max_wildcards=max_wildcards,
                    min_samples_split=min_samples_split,
                    min_samples_leaf=min_samples_leaf,
                    threshold=threshold)

                # (2d) Store the selected shingles to the memoization cache
                #  (`memo`), and trigger the next recursion step (traverse
                #  down the tree)
                for key in selected_shingles:
                    if key not in memo:  # memoization trick
                        memo[key] = db[key]
                        memo = expandshingle(
                            key, db=db, memo=memo,
                            wildcard=wildcard,
                            max_wildcards=max_wildcards,
                            min_samples_split=min_samples_split,
                            min_samples_leaf=min_samples_leaf,
                            threshold=threshold)
    # done
    return memo


def cews(db: Dict[str, int],
         memo: Optional[dict] = {},
         wildcard: Optional[str] = '\uFFFF',
         max_wildcards: Optional[int] = 1,
         min_samples_split: Optional[int] = None,
         min_samples_leaf: Optional[int] = 1,
         threshold: Optional[float] = 0.8,
         priority: Optional[str] = 'common',
         vocab_size: Optional[int] = None):
    """Collectively Exhaustive Wildcard Shingling (CEWS)

    Parameters:
    -----------
    db: dict
        Database with shingles as `key` and their frequencies/counts as `value`
          Assumptions:
          - Python's `dict` are automatically in alphabetic order but not key
              length, i.e. we still need to filter keys by length initially.
          - The database `db` is immutable.
          Preprocessing: Make sure that each shingle has a sufficient number of
            counts/frequencies, e.g. remove shingles that occur less than 20x.

    memo: dict
        Add specific shingles to the memoization cache to make sure that these
          part of subword pattern list lateron. These shingles might certain
          keywords, common stopwords, all chars, emojis, abbreviations.
          Call the function as follows:
            import kshingle as ks
            memo = {k: db[k] for k in ["i.e.", "e.g."]}
            memo = ks.cews(db, memo=memo)

    wildcard : str (Default: U+FFFF)
        An unicode char that is not actually used by any natural language,
          or the text that you analyzing, e.g. U+FFFE or U+FFFF
          See https://en.wikipedia.org/wiki/Specials_(Unicode_block)

    max_wildcards: int (Default: 1)
        If an input string `s` contains more than the specified maximum
          number of wildcard characters, the recursion aborts.

    min_samples_split: int (Default: None)
        If the combined frequency of all shingles covered by one wildcard
          shingle (count sum of the regex query results) is less than the
          specified minimum total frequency, then the recursion aborts.
        If not set, then `min_samples_split = min_samples_leaf / threshold`

    min_samples_leaf: int (Default: 1)
        Required number of counts in `db` to be added to the memo cached.
        `min_samples_leaf` is estimated from `db` if
        - it's a `float` between [0,1]
        - `min_samples_leaf='auto'` and `vocab_size` is set

    threshold: float (Default: 0.80)
        Replace max. `1.0 - threshold` of the least frequent shingles with
          the wildcard shingle.

    priority: str (Default: 'common')
        The order in which to process the shingles.
        - 'common', start with the most frequent shingles. Use this setting
            when specifying high `min_samples_leaf` and/or `vocab_size` to get
            reduce the compute time
        - 'rare', start with less frequent shingles. Use this setting when
            when specifying low `min_samples_leaf=1` and not limiting the
            vocab size.

    vocab_size: int (Default: None)
        Early stopping criteria. The main loop stops if `len(memo) >= vs`.
          The actual memo cache size will be greater equal than `vocab_size`

    Return:
    -------
    memo: dict
        Database for memoization, i.e. `memo[shingle]=count`. In case of the
          wildcarded shingle, the residual counts that are not covered by the
          selected set of shingles (Basically the `1 - p`).
        The keys in the memoization cache are selected shingles of the CEWS
          algorithm.
    """
    # add single-chars to memo automatically
    if len(memo) == 0:
        memo = {k: v for k, v in db.items() if len(k) == 1}

    # sort shingles by frequency
    db_list = list(db.items())
    db_list = sorted(db_list, key=lambda item: -item[1])

    # approximate `min_samples_leaf` with `vocab_size`
    if (min_samples_leaf == 'auto') and (vocab_size is not None):
        idx = min(len(db_list) - 1, vocab_size * 2)
        min_samples_leaf = int(max(1, db_list[idx][1]))

    # if `min_samples_leaf` is float
    if isinstance(min_samples_leaf, float) and (0.0 < min_samples_leaf <= 1.0):
        cnts = np.array([c for _, c in db_list])
        mask = (cnts / np.sum(cnts)) > min_samples_leaf
        if mask.any():
            min_samples_leaf = int(cnts[mask][-1])
        else:
            min_samples_leaf = 1

    # check threshold
    assert threshold is not None
    assert (0.0 < threshold <= 1.0)

    # set `min_samples_split`
    if min_samples_split is None:
        min_samples_split = max(2, int(min_samples_leaf / threshold))

    # only shingles with at least `min_samples_leaf` counts
    if priority == 'rare':
        shingles = [s for s, _ in db_list]
        shingles.reverse()
    elif (priority == 'common') and (vocab_size is not None):
        shingles = [s for s, c in db_list if c >= min_samples_leaf]
    else:  # priority == 'common'
        shingles = [s for s, _ in db_list]

    # loop over all db entries
    for s in shingles:
        memo = expandshingle(
            s, db=db, memo=memo,
            wildcard=wildcard,
            max_wildcards=max_wildcards,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            threshold=threshold)
        # early stopping
        if vocab_size is not None:
            if len(memo) >= vocab_size:
                break

    # done
    return memo


@functools.cmp_to_key
def sort_by_memostats(a, b):
    """ Comparison function list(memo.items())

    Parameters:
    -----------
    a, b : [shingle, num_wild, num_infix, k, count]

    Examples:
    ---------
    wildcard = '\uFFFF'
    MEMOSTATS = [(
        s, len(s.split(wildcard))-1, len(s[1:-1].split(wildcard))-1,
        len(s), c) for s, c in memo.items()]
    MEMOSTATS.sort(key=sort_by_memo)
    shingles = [x[0] for x in MEMOSTATS]
    """
    # (1) Prefer less wilcards
    if a[1] > b[1]:
        return 1
    elif a[1] < b[1]:
        return -1
    else:  # 0: a[1] == b[1]
        # (2) Prefer more infix wildcards
        if a[2] < b[2]:
            return 1
        elif a[2] > b[2]:
            return -1
        else:  # 0: a[2] == b[2]
            # (3) Prefer longer shingle length
            if a[3] < b[3]:
                return 1
            elif a[3] > b[3]:
                return -1
            else:  # 0: same length
                # (4) Prefer more frequent shingles
                if a[4] < b[4]:
                    return 1
                elif a[4] > b[4]:
                    return -1
                else:  # 0: same frequency
                    return 0


def shingleseqs_hashes(s: str,
                       k: int,
                       wildcard: str = '\uFFFF',
                       padding: Optional[str] = "center",
                       placeholder: Optional[str] = "[PAD]",
                       evenpad: Optional[str] = 'pre'
                       ) -> List[List[hashlib.md5]]:
    """ Convert a string to a list of k sequences with MD5 hashed k-shingles

    Parameters:
    -----------
    s: str
        The raw string

    k: int
        The parameter must be k>=1

    wildcard : str (Default: U+FFFF)
        An unicode char that is not actually used by any natural language,
          or the text that you analyzing, e.g. U+FFFE or U+FFFF
          See https://en.wikipedia.org/wiki/Specials_(Unicode_block)

    padding: Optional[str] = None
        Type of padding. 'pre' adds placeholder at the beginning of the
          sequence, 'post' at the end, and 'center' adds placeholder on
          both sides of the sequence.

    placeholder : Optional[str] = "[PAD]"
        The placeholder symbol

    evenpad: Optional[str] = 'pre'
        If padding='center' then sequences with even `n` cannot be perfectly
          centered, i.e. 1 placeholder must be added before (evenpad='pre')
          or after (evenpad='post').

    Returns:
    --------
    List[List[str]]
        A list of k sequences. The 1st sublist contains the chars of the
          string s, e.g. ['a', 'b', 'c'] for s="abc". The k=2 list containd
          2-shingles, e.g. ['ab', 'bc'].

    Example:
    --------
        import kshingle as ks
        multiseq = ks.shingleseqs_hashes("abc", k=2)
        multiseq = ks.shingleseqs_hashes("abc", k=2, padding='center')
    """
    # all combinations of wildcard positions given k
    wildindices = []
    for i in range(1, k):
        wildindices.extend(list(itertools.combinations(range(k), i)))

    # create copies of the text with wildcards
    swild = []
    for indices in wildindices:
        snew = copy.copy(s)
        for n in indices:
            snew = "".join([wildcard if (i % k) == n else c
                            for i, c in enumerate(snew)])
        swild.append(snew)

    # extract all shingles and their wildcard shingles
    placeholder_hash = [hashlib.md5(placeholder.encode('utf-8')).digest()]
    q = len(s)
    multiseq = []
    for n in range(1, k + 1):
        seq = []
        for i in range(q - n + 1):
            shingle = []
            substr = s[i:(i + n)]  # shingle
            hashed = hashlib.md5(substr.encode('utf-8')).digest()
            shingle.append(hashed)  # save hash
            if n >= 2:
                for j in range(len(swild)):
                    substr = swild[j][i:(i + n)]  # wildcard shingle
                    hashed = hashlib.md5(substr.encode('utf-8')).digest()
                    shingle.append(hashed)  # save hash
            seq.append(list(set(shingle)))
        # padding
        seq = pad_shingle_sequence(
            seq=seq, n=n, placeholder=placeholder_hash,
            padding=padding, evenpad=evenpad)
        # prepend missing placeholders if len(seq)<len(s)
        n_missing = q - len(seq)
        if n_missing > 0:
            seq = [placeholder_hash] * n_missing + seq
        # save
        multiseq.append(seq)
    # done
    return multiseq


def shingles_to_hashes(memo: Dict[str, int],
                       wildcard: Optional[str] = '\uFFFF'
                       ) -> Dict[int, List[hashlib.md5]]:
    """Convert shingles with wildcards to MD5 hashes

    Parameters:
    -----------
    memo: dict
        Database for memoization, i.e. `memo[shingle]=count`. In case of the
          wildcarded shingle, the residual counts that are not covered by the
          selected set of shingles (Basically the `1 - p`).
        The keys in the memoization cache are selected shingles of the CEWS
          algorithm.

    wildcard : str (Default: U+FFFF)
        An unicode char that is not actually used by any natural language,
          or the text that you analyzing, e.g. U+FFFE or U+FFFF
          See https://en.wikipedia.org/wiki/Specials_(Unicode_block)

    Returns:
    --------
    HASHES : Dict[int, List[hashlib.md5]]
        The MD5 hashes based on the selected shingles in the
          memoization cache.
    """
    # sort memo cache
    if isinstance(memo, dict):
        MEMOSTATS = [(
            s, len(s.split(wildcard)) - 1, len(s[1:-1].split(wildcard)) - 1,
            len(s), c) for s, c in memo.items()]
    elif isinstance(memo, (list, tuple)):
        MEMOSTATS = [(
            s, len(s.split(wildcard)) - 1, len(s[1:-1].split(wildcard)) - 1,
            len(s), 0) for s in memo]
    MEMOSTATS.sort(key=sort_by_memostats)
    shingles = [x[0] for x in MEMOSTATS]
    # convert shingles to hashes
    HASHES = {}
    for shingle in shingles:
        # create sublist
        n = len(shingle)
        if HASHES.get(n) is None:
            HASHES[n] = []
        # create hashes
        hashed = hashlib.md5(shingle.encode('utf-8')).digest()
        HASHES[n].append(hashed)  # save hash
    return HASHES


def encode_hashed_shingle(tokenhashes: List[hashlib.md5],
                          n: int,
                          HASHES: Dict[int, List[hashlib.md5]],
                          num_matches: int,
                          unkid: int,
                          offset: Optional[int] = 0):
    """ Util fn: Find matches for 1 token """
    matches = []
    for tid, hash in enumerate(HASHES.get(n, [])):
        if hash in tokenhashes:
            matches.append(offset + tid)
        # stop if maximum number of matches were found
        if len(matches) >= num_matches:
            break
    # fill empty list elements
    for _ in range(num_matches - len(matches)):
        matches.append(unkid)
    # done
    return matches


def encode_multi_match(multiseq: List[List[hashlib.md5]],
                       HASHES: Dict[int, List[hashlib.md5]],
                       num_matches: int,
                       unkid: int):
    """ Encode sequence with hashed wildcard shingles

    Parameters:
    -----------
    multiseq : List[List[hashlib.md5]]
        List of k sequences with a list of hashed wildcard shingles
        for each shingle/time-step

    HASHES : Dict[int, List[hashlib.md5]]
        The MD5 hashes based on the selected shingles in the
          memoization cache.

    num_matches : int
        Number of token ID to use for an n-length shingle

    unkid : int
        Token ID for unknown shingles

    Return:
    -------
    allseqs : np.ndarray (shape=[seqlen, numfeats])
        Multi-dimensional sequences with token IDs

    Examples:
    ---------
    allseqs = encode_multi_match(
        multiseq, num_matches=3, HASHES=HASHES, unkid=unkid)
    """
    offset = 0
    allseqs = []
    for i in range(len(multiseq)):
        n = i + 1
        nthseq = []
        for tokenhashes in multiseq[i]:
            matches = encode_hashed_shingle(
                tokenhashes,
                n=n,
                HASHES=HASHES,
                num_matches=min(n, num_matches),
                unkid=unkid,
                offset=offset)
            nthseq.append(matches)
        allseqs.append(nthseq)
        # new offset
        offset += len(HASHES.get(n, []))
    # merge into one big sequence
    allseqs = np.hstack(allseqs)
    # done
    return allseqs

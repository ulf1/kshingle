import re
from typing import Optional, Dict, List, Union
import functools
import numpy as np
import itertools
from .shingleseqs import shingleseqs_k


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

    wildcard : str
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


def shingles_to_patterns(memo: Dict[str, int],
                         wildcard: Optional[str] = '\uFFFF'
                         ):  # -> Dict[int, List[re.Pattern]]:
    """Convert shingles with wildcards to regex patterns

    Parameters:
    -----------
    memo: dict
        Database for memoization, i.e. `memo[shingle]=count`. In case of the
          wildcarded shingle, the residual counts that are not covered by the
          selected set of shingles (Basically the `1 - p`).
        The keys in the memoization cache are selected shingles of the CEWS
          algorithm.

    wildcard : str
        An unicode char that is not actually used by any natural language,
          or the text that you analyzing, e.g. U+FFFE or U+FFFF
          See https://en.wikipedia.org/wiki/Specials_(Unicode_block)

    Returns:
    --------
    PATTERNS : Dict[int, List[re.Pattern]]
        The regex.compile patterns based on the selected shingles in the
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
    # convert shingles to regex patterns
    PATTERNS = {}
    for shingle in shingles:
        # create sublist
        n = len(shingle)
        if PATTERNS.get(n) is None:
            PATTERNS[n] = []
        # create regex
        reg = r"\w{1}".join([re.escape(s) for s in shingle.split(wildcard)])
        pat = re.compile(f"^{reg}$")
        PATTERNS[n].append(pat)
    return PATTERNS


def encode_with_patterns(x: Union[list, str],
                         PATTERNS: dict,  # Dict[int, List[re.Pattern]],
                         unkid: Optional[int] = None):
    """Encode all elements of x with the regex pattern.

    Parameters:
    -----------
    x : Union[list, str]
        Encoding happens if type(x)==str. If type(x)=list then a recursive
          call on each list element is triggered.

    PATTERNS : Dict[int, List[re.Pattern]]
        The regex.compile patterns based on the selected shingles in the
          memoization cache.

    unkid : int
        Index of the UKNOWN token (UNK). It's `unkid=len(PATTERNS)` by default

    Returns:
    --------
    encoded : Union[list, int]
        The IDs refer to the position index in PATTERNS list
    """
    if isinstance(x, str):
        nx = len(x)
        n_pat = len(PATTERNS.get(nx, []))
        for i in range(n_pat):
            if PATTERNS[nx][i].match(x):
                return i
        return unkid if unkid else n_pat
    else:
        return [encode_with_patterns(el, PATTERNS, unkid) for el in x]


def encode_multi_match_str(x: str,
                           PATTERNLIST: list,  # List[re.Pattern],
                           offset: int,
                           num_matches: Optional[int] = 1,
                           unkid: Optional[int] = None):
    """ Encode 1 shingle for `encode_multi_match_corpus` """
    out = []
    for i, pat in enumerate(PATTERNLIST):
        if pat.match(x):
            out.append(i + offset)
            if len(out) >= num_matches:
                break
    # fill empty list elements
    for _ in range(num_matches - len(out)):
        out.append(unkid)
    return out


def encode_multi_match_corpus(corpus: List[str],
                              k: int,
                              PATTERNS: list,  # List[re.Pattern],
                              num_matches: Optional[int] = 1,
                              unkid: Optional[int] = None,
                              stack: bool = True):
    """ Shingle and encode corpus

    Example:
    --------
    corpus = ["lenghty text.", "another long article"]
    encoded, shingled = encode_multi_match_corpus(
        corpus, k=k, PATTERNS=PATTERNS, num_matches=3, stack=True)
    """
    # generate all shingles (docs, k, seqlen)
    shingled = [
        shingleseqs_k(doc, k=k, padding='post', placeholder="[PAD]")
        for doc in corpus]

    # transpose (docs, seqlen, k)
    shingled = [
        np.array(shingled_doc, dtype=object).T.tolist()
        for shingled_doc in shingled]

    # lookup list for offsets, n=i+1
    # e.g., [0, 80, 243, 508, 650]
    offsets = np.cumsum([len(PATTERNS.get(i, [])) for i in range(k)]).tolist()

    # encode (docs, seqlen, k)
    encoded = []
    for doc in shingled:
        encdoc = []
        for seqpos in doc:
            encseqpos = []
            for nkm1, ksegment in enumerate(seqpos):
                encseqpos.append(encode_multi_match_str(
                    ksegment,
                    PATTERNLIST=PATTERNS.get(nkm1 + 1, []),
                    offset=offsets[nkm1],
                    num_matches=min(nkm1 + 1, num_matches),
                    unkid=unkid))
            encdoc.append(encseqpos)
        encoded.append(encdoc)

    # flatten (docs, seqlen, k, num) to (docs, seqlen, k*num)
    encoded = [
        [list(itertools.chain(*seqpos)) for seqpos in doc]
        for doc in encoded]

    # merge to one big sequence
    if stack:
        encoded = np.vstack(encoded)

    # done
    return encoded, shingled


def encode_multi_match_text(text: str,
                            k: int,
                            PATTERNS: list,  # List[re.Pattern],
                            num_matches: Optional[int] = 1,
                            unkid: Optional[int] = None):
    """ Encode by directly looking up patterns across the text

    It's approx 20x faster than `encode_multi_match_corpus`
    """
    # change to full-text pattern
    PATTERNS2 = {}
    for n in sorted(PATTERNS.keys()):
        PATTERNS2[n] = []
        for pat in PATTERNS.get(n, []):
            PATTERNS2[n].append(re.compile(pat.pattern[1:-1]))
    # encode
    encoded = [[] for _ in range(len(text))]
    offset = 0
    end = 0
    for n in range(1, k + 1):
        end += min(n, num_matches)
        for i, pat in enumerate(PATTERNS2.get(n, [])):
            for m in re.finditer(pat, text):
                j = m.start(0)
                if len(encoded[j]) < end:
                    encoded[j].append(i + offset)
        offset += len(PATTERNS2.get(n, []))
        # fill with unkid
        for j in range(len(encoded)):
            num = len(encoded[j])
            for _ in range(end - num):
                encoded[j].append(unkid)
    # done
    return np.array(encoded)


def encode_multi_match_batch(batch: List[str],
                             k: int,
                             PATTERNS,
                             num_matches: int,
                             unkid: int,
                             seqlen: int,
                             padid: int):
    # get positions to split the string lateron
    strend = [0]
    for s in batch:
        strend.append(strend[-1] + len(s) + k)
    # merge all strings into one big string
    combtext = ("-" * k).join(batch)
    # encode string
    encall = encode_multi_match_text(
        combtext,
        k=k,
        PATTERNS=PATTERNS,
        num_matches=num_matches,
        unkid=unkid)
    # split encoded string into subsequences
    encbatch = []
    for i in range(len(strend) - 1):
        # slice subsequence
        enc = encall[strend[i]: strend[i + 1] - k]
        # truncate & pad
        h = np.ones(shape=(seqlen, enc.shape[1]), dtype=np.int64) * padid
        end = min(enc.shape[0], seqlen)
        h[:end, :] = enc[:end, :]
        encbatch.append(h)
    # done
    return encbatch

import re
from typing import Optional, Dict, List, Union
import functools


def select_most_frequent_shingles(matches: List[str],
                                  db: Dict[str, int],
                                  min_count_split: int,
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

    threshold: float (Default: 0.80)
        Replace max. `1.0 - threshold` of the least frequent shingles with
          the wildcard shingle.

    min_count_split: int (Default: 2)
        If the combined frequency of all shingles covered by one wildcard
          shingle (count sum of the regex query results) is less than the
          specified minimum total frequency, then the recursion aborts.

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
            matches, db, min_count_split, threshold)
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

    if total < min_count_split:
        return [], total

    # find most frequent (`val`) shingles (`key`) up to 90% of all matches
    # always ignore the least frequent shingle and use the wildcard version
    cumpct = 0.0
    cumcnt = 0
    selected = []
    for key, val in candidates[:-1]:
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
                  threshold: Optional[float] = 0.8,
                  min_count_split: Optional[int] = 2,
                  max_wildcards: Optional[int] = 3):
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

    threshold: float (Default: 0.80)
        Replace max. `1.0 - threshold` of the least frequent shingles with
          the wildcard shingle.

    min_count_split: int (Default: 2)
        If the combined frequency of all shingles covered by one wildcard
          shingle (count sum of the regex query results) is less than the
          specified minimum total frequency, then the recursion aborts.

    max_wildcards: int (Default: 3)
        If an input string `s` contains more than the specified maximum
          number of wildcard characters, the recursion aborts.

    Returns:
    --------
    memo: dict
        The updated memoization cache.
    """
    # (0a) stop if the shingle reached the maximum number of wildcards
    if s.count(wildcard) >= max_wildcards:
        return memo
    # (0b) abort
    if min_count_split < 1:
        raise Exception(
            f"min_count_split={min_count_split} but must greater equal 1.")

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
                matches, db, min_count_split, threshold)

            # (2c) Assign the counts of the unselected shingles to the new
            #  wildcard-shingle (`residual_count`), store it the database
            #  (`db`) and memoization cache (`memo`), and traverse to the next
            #  knot
            if residual_count >= min_count_split:
                memo[snew] = residual_count
                memo = expandshingle(snew, db=db, memo=memo,
                                     wildcard=wildcard,
                                     threshold=threshold,
                                     min_count_split=min_count_split,
                                     max_wildcards=max_wildcards)

                # (2d) Store the selected shingles to the memoization cache
                #  (`memo`), and trigger the next recursion step (traverse
                #  down the tree)
                for key in selected_shingles:
                    if key not in memo:  # memoization trick
                        memo[key] = db[key]
                        memo = expandshingle(key, db=db, memo=memo,
                                             wildcard=wildcard,
                                             threshold=threshold,
                                             min_count_split=min_count_split,
                                             max_wildcards=max_wildcards)

    # done
    return memo


def cews(db: Dict[str, int],
         memo: Optional[dict] = {},
         wildcard: Optional[str] = '\uFFFF',
         threshold: Optional[float] = 0.8,
         min_count_split: Optional[int] = 2,
         max_wildcards: Optional[int] = 3):
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

    threshold: float (Default: 0.80)
        Replace max. `1.0 - threshold` of the least frequent shingles with
          the wildcard shingle.

    min_count_split: int (Default: 2)
        If the combined frequency of all shingles covered by one wildcard
          shingle (count sum of the regex query results) is less than the
          specified minimum total frequency, then the recursion aborts.

    max_wildcards: int (Default: 3)
        If an input string `s` contains more than the specified maximum
          number of wildcard characters, the recursion aborts.

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
    # loop over all db entries
    shingles = list(db.keys())
    for s in shingles:
        memo = expandshingle(
            s, db=db, memo=memo, wildcard=wildcard, threshold=threshold,
            min_count_split=min_count_split, max_wildcards=max_wildcards)
    # done
    return memo


@functools.cmp_to_key
def sort_by_patterns(a, b):
    """Comparision function for PATTERNS.sort

    Example:
    --------
        PATTERNS.sort(key=sort_by_patterns)
    """
    # (1) Prefer exact matches (no wildcards) or resp. less wilcards
    a_wild = len(a.pattern.split(r"\w{1}")) - 1
    b_wild = len(b.pattern.split(r"\w{1}")) - 1
    if a_wild > b_wild:
        return 1  # a is bad
    elif a_wild < b_wild:
        return -1
    else:  # 0: a_wild == b_wild
        # (2) Prefer infix wildcards over suffix/prefix wildcards
        a_infix = len(
            [None for s in a.pattern[1:-1].split(r"\w{1}") if len(s) > 0]) - 1
        b_infix = len(
            [None for s in b.pattern[1:-1].split(r"\w{1}") if len(s) > 0]) - 1
        if a_infix < b_infix:
            return 1  # a is bad
        elif a_infix > b_infix:
            return -1
        else:  # 0: a_infix == b_infix
            # (3) Prefer short len
            a_len = len(a.pattern)
            b_len = len(b.pattern)
            if a_len > b_len:
                return 1
            elif a_len < b_len:
                return -1
            else:
                # (4) Alphabetic
                if a.pattern > b.pattern:
                    return 1
                elif a.pattern < b.pattern:
                    return -1
                else:
                    return 0


def shingles_to_patterns(memo: Dict[str, int],
                         wildcard: Optional[str] = '\uFFFF'
                         ) -> list:  # List[re.Pattern]
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
    PATTERNS : List[re.Pattern]
        The regex.compile patterns based on the selected shingles in the
          memoization cache.
    """
    PATTERNS = []
    for s in memo.keys():
        reg = s.replace(wildcard, r"\w{1}")
        pat = re.compile(f"^{reg}$")
        PATTERNS.append(pat)
    PATTERNS.sort(key=sort_by_patterns)
    return PATTERNS


def encode_with_patterns(x: Union[list, str],
                         PATTERNS: list,  # List[re.Pattern]
                         unkid: Optional[int] = None):
    """Encode all elements of x with the regex pattern.

    Parameters:
    -----------
    x : Union[list, str]
        Encoding happens if type(x)==str. If type(x)=list then a recursive
          call on each list element is triggered.

    PATTERNS : List[re.Pattern]
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
        n_pat = len(PATTERNS)
        for i in range(n_pat):
            if PATTERNS[i].match(x):
                return i
        return unkid if unkid else n_pat
    else:
        return [encode_with_patterns(el, PATTERNS, unkid) for el in x]

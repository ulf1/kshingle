from typing import List, Optional


def pad_shingle_sequence(seq: List[str],
                         n: int,
                         padding: Optional[str] = 'center',
                         placeholder: Optional[int] = None,
                         evenpad: Optional[str] = 'pre'):
    """Padding of multdimensional shingle sequences

    Parameters:
    -----------
    seq : List[str]
        Sequences with shingles

    n : int
        Length of each shingle

    padding: Optional[str] = 'center'
        Type of padding. 'pre' adds placeholder at the beginning of the
          sequence, 'post' at the end, and 'center' adds placeholder on
          both sides of the sequence.

    placeholder : Optional[int] = None
        The placeholder symbol

    evenpad: Optional[str] = 'pre'
        If padding='center' then sequences with even `n` cannot be perfectly
          centered, i.e. 1 placeholder must be added before (evenpad='pre')
          or after (evenpad='post').
    """
    if padding == 'center':
        # pad left and right
        pads = [placeholder] * ((n - 1) // 2)
        seq = pads + seq + pads
        # pad 1 element if `n` is even
        if (n % 2) == 0:
            if evenpad == 'post':
                seq += [placeholder]
            else:
                seq = [placeholder] + seq
        return seq

    elif padding == 'pre':
        pads = [placeholder] * (n - 1)
        return pads + seq

    elif padding == 'post':
        pads = [placeholder] * (n - 1)
        return seq + pads

    else:
        return seq


def shingleseqs_k(s: str,
                  k: int,
                  padding: Optional[str] = None,
                  placeholder: Optional[int] = None,
                  evenpad: Optional[str] = 'pre'
                  ) -> List[List[str]]:
    """Convert a string to a list of k sequences with k-shingles

    Parameters:
    -----------
    s: str
        The raw string

    k: int
        The parameter must be k>=1

    padding: Optional[str] = None
        Type of padding. 'pre' adds placeholder at the beginning of the
          sequence, 'post' at the end, and 'center' adds placeholder on
          both sides of the sequence.

    placeholder : Optional[int] = None
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
        shingles = ks.shingleseqs_k("abc", k=2)
        shingles = ks.shingleseqs_k("abc", k=2, padding='center')
    """
    shingles = []
    q = len(s)
    for n in range(1, k + 1):
        seq = [s[i:(i + n)] for i in range(q - n + 1)]
        seq = pad_shingle_sequence(
            seq=seq, n=n, placeholder=placeholder,
            padding=padding, evenpad=evenpad)
        shingles.append(seq)
    return shingles


def shingleseqs_range(s: str,
                      n_min: int,
                      n_max: int,
                      padding: Optional[str] = None,
                      placeholder: Optional[int] = None,
                      evenpad: Optional[str] = 'pre'
                      ) -> List[List[str]]:
    """Convert a string to a list of k sequences with k-shingles

    Parameters:
    -----------
    s: str
        The raw string

    n_min: int
        The lower bound k range [n_min, n_max]

    n_max: int
        The upper bound of the k range [n_min, n_max]

    padding: Optional[str] = None
        Type of padding. 'pre' adds placeholder at the beginning of the
          sequence, 'post' at the end, and 'center' adds placeholder on
          both sides of the sequence.

    placeholder : Optional[int] = None
        The placeholder symbol

    evenpad: Optional[str] = 'pre'
        If padding='center' then sequences with even `n` cannot be perfectly
          centered, i.e. 1 placeholder must be added before (evenpad='pre')
          or after (evenpad='post').

    Returns:
    --------
    List[List[str]]
        A list of k sequences. The k=1 sublist contains the chars of the
          string s, e.g. ['a', 'b', 'c', 'd'] for s="abcd". The k=3 list
          contains 3-shingles, e.g. ['abc', 'bcd'].

    Example:
    --------
        import kshingle as ks
        shingles = ks.shingleseqs_range("abcd", [2, 3])
        shingles = ks.shingleseqs_range("abcd", [2, 3], padding='center')
    """
    # correct wrong inputs
    n_max_ = max(0, n_max)
    n_min_ = max(1, n_min)
    # start to loop
    shingles = []
    q = len(s)
    for n in range(n_min_, n_max_ + 1):
        seq = [s[i:(i + n)] for i in range(q - n + 1)]
        seq = pad_shingle_sequence(
            seq=seq, n=n, placeholder=placeholder,
            padding=padding, evenpad=evenpad)
        shingles.append(seq)
    return shingles


def shingleseqs_list(s: str,
                     klist: List[int],
                     padding: Optional[str] = None,
                     placeholder: Optional[int] = None,
                     evenpad: Optional[str] = 'pre'
                     ) -> List[List[str]]:
    """Convert a string to a list of k sequences with k-shingles

    Parameters:
    -----------
    s: str
        The raw string

    klist: List[int]
        A list of specific k values, e.g. klist=[1, 3, 6]

    padding: Optional[str] = None
        Type of padding. 'pre' adds placeholder at the beginning of the
          sequence, 'post' at the end, and 'center' adds placeholder on
          both sides of the sequence.

    placeholder : Optional[int] = None
        The placeholder symbol

    evenpad: Optional[str] = 'pre'
        If padding='center' then sequences with even `n` cannot be perfectly
          centered, i.e. 1 placeholder must be added before (evenpad='pre')
          or after (evenpad='post').

    Returns:
    --------
    List[List[str]]
        A list of k sequences. The k=1 sublist contains the chars of the
          string s, e.g. ['a', 'b', 'c', 'd'] for s="abcd". The k=3 list
          contains 3-shingles, e.g. ['abc', 'bcd'].

    Example:
    --------
        import kshingle as ks
        shingles = ks.shingleseqs_list("abcd", klist=[1, 3])
        shingles = ks.shingleseqs_list("abcd", klist=[1, 3], padding='center')
    """
    shingles = []
    q = len(s)
    for n in klist:
        if n > 0:
            seq = [s[i:(i + n)] for i in range(q - n + 1)]
            seq = pad_shingle_sequence(
                seq=seq, n=n, placeholder=placeholder,
                padding=padding, evenpad=evenpad)
            shingles.append(seq)
    return shingles

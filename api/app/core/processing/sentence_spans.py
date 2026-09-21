"""Assembling a sentence out of its tokens, and noting where each one landed.

A search result is shown as one sentence with the matched word marked inside
it.  Looking that word up in the finished string is guesswork: the same form
may stand in the sentence twice, and a context search marks two words at once,
one of which may well be the same form as the other.  So the position is
written down while the sentence is being put together — each token keeps the
character range it occupies.
"""

# Punctuation is stored as a token of its own, but when the sentence is read
# back it belongs to the word in front of it: "Да молим ." -> "Да молим."
PUNCTUATION_GLUED_TO_PREVIOUS_WORD = {'.', ',', '!', '?', ';', ':'}


def join_tokens_with_spans(tokens, field):
    """The readable sentence, and where in it each token sits.

    ``tokens`` is any iterable of Token objects, ``field`` the name of the
    column to read, usually 'source' or 'diplomatic'.  A token that has
    nothing in that column is not written out and gets no span.

    A span is a pair of character positions, the second one exclusive, the way
    Python slices: ``text[start:end]`` is that token and nothing else.  The
    spans are keyed by ``ud_id``, the number the token carries in its
    sentence, because that is what a search result names.

    Example: tokens 1 "Да", 2 "молим", 3 "." give
             ("Да молим.", {1: (0, 2), 2: (3, 8), 3: (8, 9)})
    """
    text = ''
    spans = {}

    for token in tokens:
        word = (getattr(token, field, '') or '').strip()
        if not word:
            continue

        sticks_to_previous_word = text and word in PUNCTUATION_GLUED_TO_PREVIOUS_WORD
        if text and not sticks_to_previous_word:
            text += ' '

        start = len(text)
        text += word
        spans[token.ud_id] = (start, len(text))

    return text, spans


def displayed_sentence(tokens):
    """The reading of a sentence a search result shows, and where each token sits in it.

    That is the sentence as written in the source; a text that has no source
    falls back to its diplomatic transcription.  The choice is made here, once,
    so that the text and the positions of the marked words cannot disagree.

    Example: ("Да молим.", {1: (0, 2), 2: (3, 8), 3: (8, 9)})
    """
    text, spans = join_tokens_with_spans(tokens, 'source')

    if text:
        return text, spans

    return join_tokens_with_spans(tokens, 'diplomatic')

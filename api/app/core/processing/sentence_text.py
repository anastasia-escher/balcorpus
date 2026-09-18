"""Assembling the readable text of a sentence out of its tokens."""

# Punctuation is stored as a token of its own, but when the sentence is read
# back it belongs to the word in front of it: "Да молим ." -> "Да молим."
PUNCTUATION_GLUED_TO_PREVIOUS_WORD = {'.', ',', '!', '?', ';', ':'}


def join_tokens(tokens, field):
    """Join the given field of each token into one readable string.

    ``tokens`` is any iterable of Token objects, ``field`` the name of the
    column to read, usually 'source' or 'diplomatic'.

    Example: tokens with source "Да", "молим", "." give "Да молим."
    """
    words = []
    for token in tokens:
        word = getattr(token, field, '') or ''
        if not word:
            continue
        if word in PUNCTUATION_GLUED_TO_PREVIOUS_WORD and words:
            words[-1] += word
        else:
            words.append(word)

    return ' '.join(words).strip()


def source_text(sentence):
    """The sentence as it is written in the source, e.g. "Да молим." """
    return join_tokens(sentence.tokens.all(), 'source')


def diplomatic_text(sentence):
    """The sentence in its diplomatic transcription, if the corpus has one."""
    return join_tokens(sentence.tokens.all(), 'diplomatic')

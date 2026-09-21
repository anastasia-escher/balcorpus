"""Assembling the readable text of a sentence out of its tokens."""

from core.processing.sentence_spans import join_tokens_with_spans


def join_tokens(tokens, field):
    """Join the given field of each token into one readable string.

    ``tokens`` is any iterable of Token objects, ``field`` the name of the
    column to read, usually 'source' or 'diplomatic'.  Where each token ended
    up is dropped here; a caller that needs to mark a word inside the sentence
    asks ``sentence_spans`` for it instead.

    Example: tokens with source "Да", "молим", "." give "Да молим."
    """
    text, _spans = join_tokens_with_spans(tokens, field)

    return text


def source_text(sentence):
    """The sentence as it is written in the source, e.g. "Да молим." """
    return join_tokens(sentence.tokens.all(), 'source')

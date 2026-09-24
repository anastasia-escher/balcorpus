"""Assembling the readable text of a sentence out of its tokens."""

from core.processing.sentence_spans import join_tokens_with_spans


def source_text(sentence):
    """The sentence as it is written in the source, e.g. "Да молим."

    Where each token ended up is dropped here; a caller that needs to mark a
    word inside the sentence asks ``sentence_spans`` for it instead.
    """
    text, _spans = join_tokens_with_spans(sentence.tokens.all(), 'source')

    return text

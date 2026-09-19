"""Finding the sentences that stand around a given one.

A concordance line is often not enough to judge a form: the linguist needs to
see what came before and after it. This reads a small window of sentences out
of the same text, in the order they are written in.
"""

from core.models import Sentence

# How many sentences to either side, when the caller does not say.
DEFAULT_WINDOW = 2

# The most the caller may ask for. Without a ceiling this endpoint would be a
# way of downloading a whole text one request at a time.
MAXIMUM_WINDOW = 5


def clamp_window(window):
    """Keep the requested window within what the endpoint is willing to give.

    Example: clamp_window(None) -> 2, clamp_window(99) -> 5, clamp_window(-1) -> 0
    """
    if window is None:
        return DEFAULT_WINDOW

    return max(0, min(window, MAXIMUM_WINDOW))


def sentences_around(text_id, sentence_number, window=DEFAULT_WINDOW):
    """The sentences from ``window`` before to ``window`` after the given one.

    Sentences are numbered per text, so the window is a range of those
    numbers.  A number that no sentence has — at the very start of a text, or
    where a junk row was dropped on import — simply does not come back, which
    is why the caller must not assume how many sentences it gets.

    The tokens are fetched along with the sentences, because the readable text
    of a sentence is assembled from them.
    """
    first = sentence_number - window
    last = sentence_number + window

    return (
        Sentence.objects
        .filter(text_id=text_id, sentence_id__range=(first, last))
        .select_related('speaker', 'text')
        .prefetch_related('tokens')
        .order_by('sentence_id')
    )

"""Reading one text of the corpus, sentence by sentence.

The text page shows a whole work with its annotation set under every word,
which is far more than one request can carry: the longest text in the corpus
holds some fourteen thousand tokens.  So the text is read in the order it is
written and handed out a page at a time.
"""

from core.models import Sentence


def sentences_of_text(text_id):
    """Every sentence of one text, in the order the text is written.

    A text_id that no text has simply gives nothing back, which is what the
    page wants: a text whose annotation has not been imported yet is not an
    error, it is an empty text.

    The tokens are fetched along with the sentences, because the page sets
    each word together with its lemma and its tags.

    Example: sentences_of_text('panov_pechalbari_1936')
    """
    return (
        Sentence.objects
        .filter(text_id=text_id)
        .select_related('speaker', 'text')
        .prefetch_related('tokens')
        .order_by('sentence_id')
    )

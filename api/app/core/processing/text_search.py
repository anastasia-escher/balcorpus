"""Finding a text in the catalogue by its title or by who wrote it.

The catalogue runs to about a hundred texts: too many to read down looking
for one, far too few to need an index. A plain case-insensitive match over
the columns a reader actually remembers is enough.
"""

from django.db.models import Q

from core.models import Text


def build_text_queryset(query=''):
    """The catalogue, narrowed to the texts that match ``query``.

    An empty query gives the whole catalogue back, which is what a page with
    nothing typed into its search box wants.

    Three columns are matched. The title and the author's name are what a
    reader remembers; the text_id is matched as well because it is written in
    Latin letters, so someone typing "pechalbari" still finds "Печалбари".

    Example: build_text_queryset('панов') -> the texts Антон Панов wrote
    """
    texts = Text.objects.all().prefetch_related('authors')

    query = (query or '').strip()
    if not query:
        return texts

    matches = (
        Q(text_name__icontains=query)
        | Q(authors__full_name__icontains=query)
        | Q(text_id__icontains=query)
    )

    # A text has one author today, but the column is many-to-many, so the join
    # could return the same text once per matching author.
    return texts.filter(matches).distinct()

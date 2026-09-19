"""Reading a place of birth into its parts.

The source writes a place as one string in several shapes:

    'Крушево'                            a town
    'с. Брајчино, Општина Ресен'         a village and its municipality
    'с. Мелница, Мариово'                a village and the region around it
    'Титов Велес (Велес)'                a place under two names

Keeping the settlement, its kind and its municipality apart makes the data
answerable: "who was born in the Resen municipality" is a question the one
long string cannot be asked.
"""

import re

from .transliterate import to_latin

# "с." is how the source marks a village.
VILLAGE_MARKER = re.compile(r'^с\.\s*')

MUNICIPALITY_MARKER = 'Општина'

VILLAGE = 'village'
TOWN = 'town'


def split_place(text):
    """Read a place into (settlement, kind, municipality).

    Whatever follows the settlement but is not a municipality stays with the
    settlement in brackets, so no part of the original is lost.

    Examples:
        'с. Брајчино, Општина Ресен' -> ('Brajchino', 'village', 'Resen')
        'с. Мелница, Мариово'        -> ('Melnica (Mariovo)', 'village', None)
        'Крушево'                    -> ('Krushevo', 'town', None)
    """
    if not text:
        return None, None, None

    kind = VILLAGE if VILLAGE_MARKER.match(text) else TOWN
    rest = VILLAGE_MARKER.sub('', text).strip()

    parts = [part.strip() for part in rest.split(',') if part.strip()]
    settlement = parts[0]

    municipality = None
    extra = []
    for part in parts[1:]:
        if part.startswith(MUNICIPALITY_MARKER):
            municipality = part[len(MUNICIPALITY_MARKER):].strip()
        else:
            extra.append(part)

    if extra:
        joined = ', '.join(extra)
        # Splitting on the comma can cut a bracket in half, as in
        # 'Клуж (Клуж-Напокар, Коложвар)'. When the settlement is left with an
        # open bracket, the rest simply goes back inside it.
        if settlement.count('(') > settlement.count(')'):
            settlement = f'{settlement}, {joined}'
        else:
            settlement = f'{settlement} ({joined})'

    return to_latin(settlement), kind, to_latin(municipality) if municipality else None

"""How often one visitor may call the public API.

The rates themselves are in settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'].
Only visitors who are not logged in are counted, which on the public site is
everyone; a logged-in admin is never held back.
"""

from rest_framework.throttling import AnonRateThrottle


class ExportRateThrottle(AnonRateThrottle):
    """Downloads of a whole search, counted separately from other requests."""

    scope = 'export'

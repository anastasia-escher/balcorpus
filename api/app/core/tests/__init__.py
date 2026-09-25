"""Tests for the corpus: what it stores and how it is searched.

The public API allows 60 requests a minute from one address, and the test
suite sends far more than that. So the limits are switched off here, once, for
every test, whichever runner is used; test_public_limits switches them on
again for the tests that are about them.
"""

from rest_framework.throttling import SimpleRateThrottle

SimpleRateThrottle.THROTTLE_RATES = {'anon': None, 'export': None}

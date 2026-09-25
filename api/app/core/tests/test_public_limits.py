"""Tests for the limits that protect the public API from overuse."""

from unittest import mock

from django.core.cache import cache
from django.test import TestCase
from rest_framework.throttling import SimpleRateThrottle

from .corpus_fixtures import make_sentence

SEARCH_URL = '/api/v1/tokens/search/'
XLSX_URL = '/api/v1/tokens/search/xlsx/'


def rates(**rates_by_scope):
    """Switch the request limits on for one test; core/tests/__init__.py turns them off."""
    return mock.patch.dict(SimpleRateThrottle.THROTTLE_RATES, rates_by_scope)


class RequestRateTests(TestCase):
    def setUp(self):
        # The counts live in the cache, which would carry over between tests.
        cache.clear()
        make_sentence('Комедијата е убаво напишана .', lemmas=['комедија', 'сум', 'убав', 'напишан', '.'])

    def test_too_many_requests_are_refused_and_told_when_to_retry(self):
        with rates(anon='2/min', export=None):
            self.client.get(SEARCH_URL, {'lemma': 'убав'})
            self.client.get(SEARCH_URL, {'lemma': 'убав'})
            response = self.client.get(SEARCH_URL, {'lemma': 'убав'})

        self.assertEqual(response.status_code, 429)
        self.assertIn('Retry-After', response)

    def test_downloads_have_a_limit_of_their_own(self):
        with rates(anon='100/min', export='1/min'):
            first = self.client.get(XLSX_URL, {'lemma': 'убав'})
            second = self.client.get(XLSX_URL, {'lemma': 'убав'})
            search = self.client.get(SEARCH_URL, {'lemma': 'убав'})

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 429)
        self.assertEqual(search.status_code, 200)


class ParameterLengthTests(TestCase):
    def test_an_over_long_parameter_is_refused(self):
        response = self.client.get(SEARCH_URL, {'q': 'а' * 101})

        self.assertEqual(response.status_code, 400)
        self.assertIn('q', response.json())

    def test_a_parameter_at_the_limit_is_accepted(self):
        self.assertEqual(self.client.get(SEARCH_URL, {'q': 'а' * 100}).status_code, 200)

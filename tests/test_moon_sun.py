"""Metadata-based test for Moon Sun."""

import pytest

from tests.metadata_test_utils import run_metadata_test_and_verify


def test_moon_sun_from_metadata():
    assert run_metadata_test_and_verify("moon_sun")

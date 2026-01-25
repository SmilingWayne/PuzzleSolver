"""Metadata-based test for Regional Yajilin."""

import pytest

from tests.metadata_test_utils import run_metadata_test_and_verify


def test_regional_yajilin_from_metadata():
    assert run_metadata_test_and_verify("regional_yajilin")

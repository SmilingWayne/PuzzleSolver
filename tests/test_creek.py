"""Metadata-based test for Creek."""

import pytest

from tests.metadata_test_utils import run_metadata_test_and_verify


def test_creek_from_metadata():
    assert run_metadata_test_and_verify("creek")

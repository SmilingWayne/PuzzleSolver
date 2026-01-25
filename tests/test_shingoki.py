"""Metadata-based test for Shingoki."""

import pytest

from tests.metadata_test_utils import run_metadata_test_and_verify


def test_shingoki_from_metadata():
    assert run_metadata_test_and_verify("shingoki")

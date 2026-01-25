"""Metadata-based test for Ken Ken."""

import pytest

from tests.metadata_test_utils import run_metadata_test_and_verify


def test_ken_ken_from_metadata():
    assert run_metadata_test_and_verify("ken_ken")

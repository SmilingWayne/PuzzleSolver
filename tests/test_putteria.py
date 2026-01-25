"""Metadata-based test for Putteria."""

import pytest

from tests.metadata_test_utils import run_metadata_test_and_verify


def test_putteria_from_metadata():
    assert run_metadata_test_and_verify("putteria")

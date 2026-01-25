"""Metadata-based test for Bricks."""

import pytest

from tests.metadata_test_utils import run_metadata_test_and_verify


def test_bricks_from_metadata():
    assert run_metadata_test_and_verify("bricks")

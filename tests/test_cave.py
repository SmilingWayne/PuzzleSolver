"""Metadata-based test for Cave."""

import pytest

from tests.metadata_test_utils import run_metadata_test_and_verify


def test_cave_from_metadata():
    assert run_metadata_test_and_verify("cave")

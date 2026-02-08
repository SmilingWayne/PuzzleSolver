"""Metadata-based test for LITS."""

import pytest

from tests.metadata_test_utils import run_metadata_test_and_verify


def test_lits_from_metadata():
    assert run_metadata_test_and_verify("lits")

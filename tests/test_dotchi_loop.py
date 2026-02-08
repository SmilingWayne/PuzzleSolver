"""Metadata-based test for Dotchi Loop."""

import pytest

from tests.metadata_test_utils import run_metadata_test_and_verify


def test_dotchi_loop_from_metadata():
    assert run_metadata_test_and_verify("dotchi_loop")

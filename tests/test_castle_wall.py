"""Metadata-based test for Castle Wall: input_example -> parser -> solver -> verify via grid_verifier."""

import pytest

from tests.metadata_test_utils import run_metadata_test_and_verify


def test_castle_wall_from_metadata():
    assert run_metadata_test_and_verify("castle_wall")

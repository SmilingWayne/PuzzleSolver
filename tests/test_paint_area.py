"""Metadata-based test for Paint Area."""

import pytest

from tests.metadata_test_utils import run_metadata_test_and_verify


def test_paint_area_from_metadata():
    assert run_metadata_test_and_verify("paint_area")

"""Metadata-based test for Yajikabe."""

import pytest

from tests.metadata_test_utils import run_metadata_test_and_verify


def test_yajikabe_from_metadata():
    assert run_metadata_test_and_verify("yajikabe")

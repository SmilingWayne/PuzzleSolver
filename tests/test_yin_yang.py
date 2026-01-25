"""Metadata-based test for Yin Yang."""

import pytest

from tests.metadata_test_utils import run_metadata_test_and_verify


def test_yin_yang_from_metadata():
    assert run_metadata_test_and_verify("yin_yang")

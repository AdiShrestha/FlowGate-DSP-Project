"""Pytest fixtures never reuse or rotate a real supervisor key."""
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import supervisor


@pytest.fixture(scope='session',autouse=True)
def isolated_default_supervisor_keys(tmp_path_factory):
    original=supervisor._DEFAULT_KEY_DIR
    supervisor._DEFAULT_KEY_DIR=tmp_path_factory.mktemp('supervisor-keys')
    try:yield
    finally:supervisor._DEFAULT_KEY_DIR=original

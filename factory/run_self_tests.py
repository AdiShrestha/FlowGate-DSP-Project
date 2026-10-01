#!/usr/bin/env python3
"""Run the v3 standard-library regression suite, offline."""
import unittest
import tempfile
from pathlib import Path
if __name__=='__main__':
    # Testing never creates or rotates the user's real supervisor key.
    from engine import supervisor
    with tempfile.TemporaryDirectory(prefix='flowgate-factory-tests-') as keys:
        supervisor._DEFAULT_KEY_DIR=Path(keys)
        suite=unittest.defaultTestLoader.discover(str(Path(__file__).parent/'tests'),pattern='test_*.py')
        result=unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)

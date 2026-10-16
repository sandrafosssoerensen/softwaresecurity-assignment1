"""Isolated SQL-query security test for the CWE-89 experiment."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
os.environ.setdefault("SERVICE", "C")

import django

django.setup()

from django.test import override_settings

from app import store


class StoreSqlTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(DATA_DIR=Path(self.temp.name))
        self.settings_override.enable()

    def tearDown(self):
        self.settings_override.disable()
        self.temp.cleanup()

    def test_injected_analysis_id_does_not_return_a_record(self):
        real_id = "known-analysis"
        store.create(real_id, "1", {"marker": "test-record"})

        injected_id = "' OR 1=1 -- "
        result = store.read(injected_id, "1", admin=False)

        # This is the security expectation. It fails with the vulnerable
        # f-string query and passes with the parameterized query.
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main(verbosity=2)

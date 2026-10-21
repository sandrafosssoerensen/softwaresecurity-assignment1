"""Check that the approval gate rejects unlisted, missing, and changed packages."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.check_dependencies import APPROVAL_FILES, compare, load_approved, normalize


class DependencyGateTests(unittest.TestCase):
    def test_exact_inventory_passes(self):
        self.assertEqual(compare({"django": "1.0"}, {"django": "1.0"}), [])

    def test_unapproved_package_fails(self):
        findings = compare({"django": "1.0"}, {"django": "1.0", "unexpected": "2.0"})
        self.assertEqual(findings, ["Unapproved package: unexpected==2.0"])

    def test_changed_version_fails(self):
        self.assertEqual(len(compare({"django": "1.0"}, {"django": "2.0"})), 1)

    def test_missing_package_fails(self):
        self.assertEqual(compare({"django": "1.0"}, {}), ["Missing approved package: django==1.0"])

    def test_package_name_normalization(self):
        self.assertEqual(normalize("Pip_Audit"), normalize("pip-audit"))

    def test_unpinned_requirement_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for filename in APPROVAL_FILES:
                target = root / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("django>=1.0\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exact name==version"):
                load_approved(root)


if __name__ == "__main__":
    unittest.main(verbosity=2)

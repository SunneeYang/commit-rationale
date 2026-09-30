"""Offline packaging checks, not evidence of Marketplace acceptance."""

import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("package_marketplace", ROOT / "scripts/package_marketplace.py")
packager = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(packager)


class MarketplacePackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="rationale-package-")
        self.root = Path(self.temp.name)
        self.repo = self.root / "source"
        self.repo.mkdir()
        shutil.copytree(ROOT / "plugins", self.repo / "plugins")
        shutil.copy2(ROOT / "LICENSE", self.repo / "LICENSE")
        self.output = self.root / "review.zip"

    def tearDown(self):
        self.temp.cleanup()

    def test_exact_allowlist_and_no_hooks_or_secrets(self):
        hidden = self.repo / packager.PLUGIN / "skills/read-commit-history/.env"
        hidden.write_text("SYNTHETIC_SECRET=must-not-ship")
        report = packager.build_package(self.repo, self.output)
        with zipfile.ZipFile(self.output) as archive:
            expected = sorted(["plugin.json", "LICENSE", *packager.SKILL_FILES])
            self.assertEqual(sorted(archive.namelist()), expected)
            self.assertIsNone(archive.testzip())
            for content in (archive.read(name) for name in archive.namelist()):
                self.assertNotIn(b"SYNTHETIC_SECRET", content)
            manifest = json.loads(archive.read("plugin.json"))
        self.assertEqual(manifest["$schema"], packager.SCHEMA)
        self.assertNotIn("author", manifest)
        self.assertNotIn("hooks", manifest["extensions"]["com.openai"])
        self.assertEqual(report["status"], "review-only")
        self.assertFalse(report["submission_ready"])
        self.assertEqual(len(report["sha256"]), 64)
        self.assertEqual(json.loads(self.output.with_suffix(".preflight.json").read_text()), report)

    def test_reproducible_zip_and_explicit_version(self):
        first = packager.build_package(self.repo, self.output, "0.2.0")
        second = packager.build_package(self.repo, self.root / "second.zip", "0.2.0")
        self.assertEqual(first["sha256"], second["sha256"])
        self.assertEqual(first["version"], "0.2.0")

    def test_missing_required_source_fails_before_output(self):
        (self.repo / packager.PLUGIN / packager.SKILL_FILES[-1]).unlink()
        with self.assertRaisesRegex(ValueError, "Missing regular"):
            packager.build_package(self.repo, self.output)
        self.assertFalse(self.output.exists())

    def test_symlinked_source_file_rejected(self):
        path = self.repo / packager.PLUGIN / packager.SKILL_FILES[-1]
        path.unlink()
        path.symlink_to(ROOT / "LICENSE")
        with self.assertRaisesRegex(ValueError, "Symlinked"):
            packager.build_package(self.repo, self.output)
        self.assertFalse(self.output.exists())

    def test_symlinked_parent_directory_rejected(self):
        path = self.repo / packager.PLUGIN / "skills/read-commit-history/scripts"
        shutil.rmtree(path)
        path.symlink_to(ROOT / packager.PLUGIN / "skills/read-commit-history/scripts", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Symlinked"):
            packager.build_package(self.repo, self.output)

    def test_never_overwrites_output(self):
        self.output.write_bytes(b"keep this")
        with self.assertRaisesRegex(ValueError, "already exists"):
            packager.build_package(self.repo, self.output)
        self.assertEqual(self.output.read_bytes(), b"keep this")

    def test_invalid_semver_rejected(self):
        for version in ["latest", "01.2.3", "1.0.0-01", "1.0.0+", "1.0.0/../../x", "1\u0661.0.0"]:
            with self.subTest(version=version), self.assertRaises(ValueError):
                packager.make_manifest(version)
        for version in ["0.2.0", "1.0.0-rc.1+build.2", "0.1.0+codex.20260930054158"]:
            self.assertEqual(packager.make_manifest(version)["version"], version)

    def test_listing_draft_meets_text_limits(self):
        listing = packager.make_manifest("0.2.0")["extensions"]["com.openai"]["interface"]
        self.assertLessEqual(len(listing["displayName"]), 30)
        self.assertLessEqual(len(listing["shortDescription"]), 30)
        self.assertLessEqual(len(listing["longDescription"]), 4000)
        self.assertLessEqual(len(listing["defaultPrompt"]), 3)
        self.assertTrue(all(len(prompt) <= 128 for prompt in listing["defaultPrompt"]))
        self.assertNotIn("developerName", listing)
        self.assertNotIn("logo", listing)

    def test_existing_report_is_preserved(self):
        report = self.output.with_suffix(".preflight.json")
        report.write_text("keep this")
        with self.assertRaisesRegex(ValueError, "already exists"):
            packager.build_package(self.repo, self.output)
        self.assertFalse(self.output.exists())
        self.assertEqual(report.read_text(), "keep this")

    def test_non_zip_output_is_rejected(self):
        with self.assertRaisesRegex(ValueError, ".zip extension"):
            packager.build_package(self.repo, self.root / "wrong.json")

    def test_review_helper_runs_from_extracted_package(self):
        packager.build_package(self.repo, self.output)
        extraction = self.root / "extracted"
        with zipfile.ZipFile(self.output) as archive:
            archive.extractall(extraction)
        import subprocess
        helper = extraction / packager.SKILL_FILES[-1]
        result = subprocess.run(["python3", str(helper), "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--repo", result.stdout)


if __name__ == "__main__":
    unittest.main()

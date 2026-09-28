"""TEST-020：BATCH-001 哈希锁、SBOM 与 notices 基础门禁。"""
import json
import os
import re
import unittest
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = {"Flask": "2.3.2", "Werkzeug": "2.3.6", "Jinja2": "3.1.2",
           "MarkupSafe": "2.1.3", "itsdangerous": "2.1.2", "click": "8.3.1",
           "blinker": "1.6.2", "gevent": "24.2.1", "greenlet": "3.0.3",
           "zope.event": "5.0", "zope.interface": "6.4.post2",
           "cffi": "2.0.0", "pycparser": "2.21", "colorama": "0.4.6",
           "setuptools": "65.5.0"}
TEST_ONLY = {"Pillow": "9.5.0"}

class FoundationDeliveryTests(unittest.TestCase):
    def test_hash_lock_matches_fixed_runtime_and_test_dependencies(self):
        lock = (ROOT / "requirements.lock").read_text(encoding="utf-8")
        test_lock = (ROOT / "requirements-test.lock").read_text(encoding="utf-8")
        for name, version in RUNTIME.items():
            with self.subTest(name=name):
                self.assertRegex(lock, re.compile(
                    r"(?im)^" + re.escape(name) + r"==" + re.escape(version) + r"\b.*--hash=sha256:[0-9a-f]{64}"))
                self.assertEqual(metadata.version(name), version)
        self.assertNotRegex(lock, r"(?im)^Pillow==")
        self.assertRegex(test_lock, r"(?im)^Pillow==9\.5\.0\b.*--hash=sha256:[0-9a-f]{64}")

    def test_sbom_and_notices_cover_runtime_and_test_packages(self):
        sbom = json.loads((ROOT / "sbom.json").read_text(encoding="utf-8"))
        packages = {(item["name"], item["version"]) for item in sbom["packages"]}
        self.assertEqual(packages, set(RUNTIME.items()) | set(TEST_ONLY.items()))
        notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        for name in (*RUNTIME, *TEST_ONLY, "Bootstrap", "jQuery"):
            with self.subTest(name=name):
                self.assertIn(name, notices)

    def test_config_example_has_placeholders_only(self):
        sample = (ROOT / "config.example.ps1").read_text(encoding="utf-8")
        self.assertIn("BOOKSHOP_SECRET_KEY", sample)
        self.assertIn("BOOKSHOP_DATABASE_PATH", sample)
        self.assertIn("BOOKSHOP_UPLOAD_DIR", sample)
        self.assertNotRegex(sample, r"(?i)[0-9a-f]{64}")

    def test_sbom_hashes_match_both_lock_files(self):
        locks = (ROOT / "requirements.lock").read_text(encoding="utf-8")
        locks += (ROOT / "requirements-test.lock").read_text(encoding="utf-8")
        entries = re.findall(r"(?im)^(\S+)==(\S+) --hash=sha256:([0-9a-f]{64})$", locks)
        normalize = lambda name: re.sub(r"[-_.]+", "-", name).lower()
        expected = {(normalize(name), version, digest) for name, version, digest in entries}
        sbom = json.loads((ROOT / "sbom.json").read_text(encoding="utf-8"))
        actual = {(normalize(p["name"]), p["version"], p["sha256"]) for p in sbom["packages"]}
        self.assertEqual(actual, expected)

    def test_original_licenses_accompany_installed_distributions(self):
        for name in (*RUNTIME, *TEST_ONLY):
            with self.subTest(name=name):
                files = metadata.distribution(name).files or []
                licenses = [f for f in files if ".dist-info/" in str(f)
                            and ("LICENSE" in str(f).upper() or "COPYING" in str(f).upper())]
                self.assertTrue(licenses)
                self.assertTrue(all(f.locate().is_file() for f in licenses))

    @unittest.skipUnless(os.environ.get("BOOKSHOP_VERIFY_ENV") == "1",
                         "实际安装集合精确核对只在干净虚拟环境执行")
    def test_clean_environment_installed_set_is_exact(self):
        normalize = lambda name: re.sub(r"[-_.]+", "-", name).lower()
        actual = {(normalize(d.metadata["Name"]), d.version) for d in metadata.distributions()
                  if normalize(d.metadata["Name"]) != "pip"}
        expected = {(normalize(name), version) for name, version in
                    {**RUNTIME, **TEST_ONLY}.items()}
        self.assertEqual(actual, expected)

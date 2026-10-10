"""TEST-042：CI workflow 静态检查（REQ-PLATFORM-012、MIG-RULE-013、MIG-RULE-014、MIG-RULE-022、DEC-015）。"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WF = ROOT / ".github" / "workflows" / "bookshop-ci.yml"


def text():
    return WF.read_text(encoding="utf-8")


def test_only_new_workflow():
    names = sorted(p.name for p in (ROOT / ".github" / "workflows").glob("*.yml"))
    assert names == ["bookshop-ci.yml"]


def test_triggers_master_only():
    t = text()
    assert re.search(r"on:\s*\n\s+push:\s*\n\s+branches:\s*\[\s*master\s*\]", t)
    assert re.search(r"\n\s+pull_request:\s*\n\s+branches:\s*\[\s*master\s*\]", t)


def test_runner_python_and_encoding():
    t = text()
    assert "runs-on: windows-latest" in t and "ubuntu" not in t
    assert re.search(r'python-version:\s*"3\.12\.10"', t)
    assert re.search(r'PYTHONUTF8:\s*"1"', t)


def test_install_and_run():
    t = text()
    assert "py -3.12 -m venv .venv" in t or "python -m venv .venv" in t
    assert "--require-hashes -r requirements-test.txt" in t
    assert re.search(r"\.venv\\Scripts\\python\.exe -m pytest .*--junitxml=reports/junit\.xml", t)
    assert "-m \"not server\"" not in t and "-m 'not server'" not in t
    assert "migration_gate.mjs coverage --root migration-plans/bookshop --change openspec/changes/migrate-bookshop-to-flask" in t
    assert "migration_gate.mjs lint --root openspec/changes/migrate-bookshop-to-flask" in t
    assert "actions/upload-artifact" in t and "reports/junit.xml" in t

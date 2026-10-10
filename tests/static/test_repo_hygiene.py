"""TEST-043：仓库卫生（REQ-PLATFORM-012、REQ-PLATFORM-010、MIG-RULE-010、MIG-RULE-011、DEC-011、DEC-022）。"""
import hashlib
import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {".git", ".venv", ".venv-check", "BookShop", "node_modules", "__pycache__", "reports"}
TEXT_EXT = {".py", ".md", ".html", ".css", ".js", ".ps1", ".yml", ".yaml", ".ini", ".in", ".txt", ".toml", ".sql", ".json"}
LOCAL_PATH = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]|[\\/]Users[\\/]|AppData")


def files():
    for p in ROOT.rglob("*"):
        rel = p.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts) or not p.is_file():
            continue
        yield rel, p


def test_no_local_paths():
    bad = []
    for rel, p in files():
        if p.suffix not in TEXT_EXT or rel.as_posix() == "tests/static/test_repo_hygiene.py":
            continue
        if rel.parts[0] == "bookshop_web" and rel.parts[1:2] == ("static",):
            continue  # 第三方压缩文件，单独核对哈希
        for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if LOCAL_PATH.search(re.sub(r"https?://\S+", "", line)):
                bad.append(f"{rel.as_posix()}:{n}")
    assert not bad, bad


def test_no_hardcoded_secrets():
    from bookshop_web.config import EXAMPLE_SECRET

    pattern = re.compile(r"BOOKSHOP_SECRET_KEY\s*=\s*['\"]([^'\"]+)['\"]")
    for rel, p in files():
        if p.suffix not in {".py", ".ps1", ".md", ".yml"} or rel.parts[0] == "tests":
            continue
        for value in pattern.findall(p.read_text(encoding="utf-8", errors="replace")):
            assert value == EXAMPLE_SECRET, f"{rel.as_posix()} 里写死了密钥"
    assert not [rel for rel, p in files() if p.suffix in {".pem", ".key", ".pfx"}]


def test_templates_have_no_external_urls():
    for p in (ROOT / "bookshop_web" / "templates").glob("*.html"):
        for attr in re.findall(r"(?:src|href|action)\s*=\s*\"([^\"]*)\"", p.read_text(encoding="utf-8")):
            assert not re.match(r"^(https?:)?//", attr), (p.name, attr)


def test_vendor_hashes_match():
    vendor = (ROOT / "bookshop_web" / "static" / "VENDOR.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\| `([^`]+)` \| `sha512-([^`]+)` \|", vendor, re.M)
    assert len(rows) >= 5
    for rel, digest in rows:
        data = (ROOT / "bookshop_web" / "static" / rel).read_bytes()
        assert base64.b64encode(hashlib.sha512(data).digest()).decode() == digest, rel


def test_licenses_present():
    static = ROOT / "bookshop_web" / "static"
    assert (static / "bootstrap" / "LICENSE").is_file()
    assert (static / "bootstrap-icons" / "LICENSE").is_file()
    assert (ROOT / "THIRD_PARTY_NOTICES.md").is_file()


def test_gitignore():
    lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    for entry in (".venv/", "*.db", "*.db-wal", "*.db-shm"):
        assert entry in lines, entry


def test_config_example_only_placeholder():
    from bookshop_web.config import EXAMPLE_SECRET

    text = (ROOT / "config.example.ps1").read_text(encoding="utf-8")
    assert EXAMPLE_SECRET in text

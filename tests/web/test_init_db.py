"""TEST-017：初始化命令与演示数据（REQ-DATA-003、MIG-RULE-015、LEGACY-066、GAP-002、DEC-010）。

只断言结构和转写是否正确，不把演示数据当作原书店的事实。
"""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests.conftest import ADMIN_PASSWORD, db

ROOT = Path(__file__).resolve().parents[2]


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


@pytest.mark.batch(2)
def test_seeded_content(seeded):
    c = db(seeded)
    try:
        assert [tuple(r) for r in c.execute("SELECT tid, tname FROM tag ORDER BY tid")] == [(1, "小说"), (2, "散文"), (3, "诗歌")]
        assert [r[0] for r in c.execute("SELECT bid FROM book ORDER BY bid")] == [1, 2, 3, 4, 5, 6, 7, 8, 9, 11]
        assert c.execute("SELECT COUNT(*) FROM book WHERE on_sale = 1").fetchone()[0] == 10
        users = c.execute("SELECT uname, upwd, role, active, session_version FROM user").fetchall()
        assert len(users) == 1
        uname, upwd, role, active, sv = tuple(users[0])
        assert (uname, role, active, sv) == ("admin", 2, 1, 0)
        assert upwd.startswith("scrypt:32768:8:1$") and ADMIN_PASSWORD not in upwd
        assert c.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0
        assert c.execute("SELECT COUNT(*) FROM addbook_draft").fetchone()[0] == 0
    finally:
        c.close()


@pytest.mark.batch(2)
def test_covers_copied(seeded):
    src = ROOT / "bookshop_web" / "seed" / "covers"
    names = sorted(p.name for p in src.iterdir())
    assert names == sorted(f"b{i}.jpg" for i in (1, 2, 3, 4, 5, 6, 7, 8, 9, 11))
    for n in names:
        assert digest(seeded / "covers" / n) == digest(src / n)


@pytest.mark.batch(2)
@pytest.mark.parametrize("pw", ["", "123456", "x" * 65])
def test_rejects_bad_admin_password(data_dir, pw):
    from bookshop_web.initdb import InitError, init_db

    with pytest.raises(InitError):
        init_db(data_dir, pw)
    assert not (data_dir / "bookshop.db").exists()


@pytest.mark.batch(2)
def test_refuses_existing_db(seeded):
    from bookshop_web.initdb import InitError, init_db

    before = digest(seeded / "bookshop.db")
    with pytest.raises(InitError, match="已存在"):
        init_db(seeded, ADMIN_PASSWORD)
    assert digest(seeded / "bookshop.db") == before


def run_cli(args, env_extra, data_dir):
    env = {k: v for k, v in os.environ.items() if not k.startswith("BOOKSHOP_")}
    env.update(PYTHONUTF8="1", BOOKSHOP_DATA_DIR=str(data_dir), **env_extra)
    return subprocess.run([sys.executable, "-m", "bookshop_web", *args], env=env, capture_output=True, text=True,
                          encoding="utf-8", timeout=120, cwd=ROOT, stdin=subprocess.DEVNULL)


@pytest.mark.batch(2)
def test_cli_success(data_dir):
    p = run_cli(["init-db"], {"BOOKSHOP_ADMIN_PASSWORD": ADMIN_PASSWORD}, data_dir)
    assert p.returncode == 0, p.stderr
    assert (data_dir / "bookshop.db").exists()
    assert ADMIN_PASSWORD not in p.stdout + p.stderr


@pytest.mark.batch(2)
def test_cli_rejects_123456(data_dir):
    p = run_cli(["init-db"], {"BOOKSHOP_ADMIN_PASSWORD": "123456"}, data_dir)
    assert p.returncode != 0 and not (data_dir / "bookshop.db").exists()
    assert "不能是 123456" in p.stderr, p.stderr


# 命令行解析在 BATCH-001 已实现，这一项从那时起就应当通过。
def test_cli_no_password_argument(data_dir):
    p = run_cli(["init-db", "--password", "x"], {"BOOKSHOP_ADMIN_PASSWORD": ADMIN_PASSWORD}, data_dir)
    assert p.returncode != 0 and "未知参数" in p.stderr
    assert not (data_dir / "bookshop.db").exists()


@pytest.mark.batch(2)
def test_cli_without_password_and_tty(data_dir):
    p = run_cli(["init-db"], {}, data_dir)
    assert p.returncode != 0 and "BOOKSHOP_ADMIN_PASSWORD" in p.stderr
    assert not (data_dir / "bookshop.db").exists()

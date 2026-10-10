"""TEST-044：启停脚本、运行中实例的冒烟检查、数据目录的备份与恢复（REQ-PLATFORM-012、REQ-DATA-003、DEC-009、DEC-013）。

用 Windows PowerShell 5.1 实际执行 scripts/start.ps1 和 scripts/stop.ps1。保护回滚。
"""
import hashlib
import http.client
import os
import secrets
import shutil
import socket
import sqlite3
import subprocess
import time
from pathlib import Path

import pytest

from tests.conftest import copy_seed

pytestmark = pytest.mark.server
ROOT = Path(__file__).resolve().parents[2]


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Result:
    def __init__(self, returncode, output):
        self.returncode, self.stdout, self.stderr = returncode, output, ""


def ps(script, env):
    """输出写到文件而不是管道：即使有进程意外继承了句柄，也不会让测试一直等管道关闭。"""
    log = Path(env["BOOKSHOP_DATA_DIR"]).parent / f"{script}.{time.time_ns()}.log"
    with log.open("wb") as f:
        p = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ROOT / "scripts" / script)],
                           env=env, stdin=subprocess.DEVNULL, stdout=f, stderr=subprocess.STDOUT, timeout=90, cwd=ROOT)
    return Result(p.returncode, log.read_text(encoding="utf-8", errors="replace"))


def get(port, path):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    conn.request("GET", path)
    r = conn.getresponse()
    r.read()
    conn.close()
    return r


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def test_start_smoke_stop_and_restore(tmp_path, seeded_template):
    data = tmp_path / "data"
    data.mkdir()
    copy_seed(seeded_template, data)
    port = free_port()
    env = {k: v for k, v in os.environ.items() if not k.startswith("BOOKSHOP_")}
    env.update(BOOKSHOP_DATA_DIR=str(data), BOOKSHOP_SECRET_KEY=secrets.token_hex(32), BOOKSHOP_PORT=str(port))

    started = ps("start.ps1", env)
    try:
        assert started.returncode == 0, started.stdout + started.stderr
        pid_file = data / "run" / "bookshop.pid"
        assert pid_file.is_file()
        # 运行中实例的冒烟检查（test-plan：Post-Deployment Smoke Tests）
        assert get(port, "/BookShop/").status == 200
        assert get(port, "/BookShop/login.jsp").status == 200
        r = get(port, "/BookShop/jsp/my.jsp")
        assert r.status == 302 and r.getheader("Location").endswith("/BookShop/login.jsp")
        assert get(port, "/BookShop/img/b1.jpg").status == 200
    finally:
        stopped = ps("stop.ps1", env)
    assert stopped.returncode == 0, stopped.stdout + stopped.stderr
    assert not (data / "run" / "bookshop.pid").exists()
    with pytest.raises(OSError):
        socket.create_connection(("127.0.0.1", port), timeout=2).close()
    assert (data / "logs" / "bookshop.log").is_file()

    # 回滚演练：停服状态下备份 → 修改数据 → 恢复 → 与备份一致
    backup = tmp_path / "backup"
    shutil.copytree(data, backup)
    before = digest(backup / "bookshop.db")
    conn = sqlite3.connect(data / "bookshop.db")
    conn.execute("UPDATE book SET stock = 1 WHERE bid = 9")
    conn.commit()
    conn.close()
    assert digest(data / "bookshop.db") != before
    for p in data.glob("bookshop.db*"):
        p.unlink()
    shutil.copyfile(backup / "bookshop.db", data / "bookshop.db")
    assert digest(data / "bookshop.db") == before
    conn = sqlite3.connect(data / "bookshop.db")
    assert conn.execute("SELECT stock FROM book WHERE bid = 9").fetchone()[0] == 100
    conn.close()


def test_start_refuses_bad_config(tmp_path):
    env = {k: v for k, v in os.environ.items() if not k.startswith("BOOKSHOP_")}
    env.update(BOOKSHOP_DATA_DIR=str(tmp_path), BOOKSHOP_SECRET_KEY="replace-with-64-hex-chars-from-python-secrets-token-hex-32",
               BOOKSHOP_PORT=str(free_port()))
    r = ps("start.ps1", env)
    assert r.returncode != 0
    assert not (tmp_path / "run" / "bookshop.pid").exists()

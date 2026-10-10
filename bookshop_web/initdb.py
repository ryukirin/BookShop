"""初始化命令：建库并导入演示数据（REQ-DATA-003、GAP-002、MIG-RULE-015、DEC-010）。

    python -m bookshop_web init-db

管理员口令只从环境变量 BOOKSHOP_ADMIN_PASSWORD 读取，或在终端里交互输入（不回显）；
不接受命令行参数。数据库已存在时拒绝覆盖。
"""
from __future__ import annotations

import getpass
import os
import shutil
import sys
from pathlib import Path

from werkzeug.security import generate_password_hash

from .config import check_interpreter, load_config
from .db import connect, db_path, write_tx
from .seed.seed_data import BOOKS, TAGS

PACKAGE_DIR = Path(__file__).resolve().parent
SCHEMA = PACKAGE_DIR / "schema.sql"
SEED_COVERS = PACKAGE_DIR / "seed" / "covers"
SCHEMA_VERSION = 1


class InitError(Exception):
    pass


def check_admin_password(pw: str | None) -> str:
    if not pw:
        raise InitError("管理员口令不能为空。")
    if pw == "123456":
        raise InitError("管理员口令不能是 123456（旧系统的占位口令）。")
    if len(pw) > 64:
        raise InitError("管理员口令不能超过 64 个字符。")
    return pw


def create_schema(conn) -> None:
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA user_version = 1")


def init_db(data_dir: Path, admin_password: str) -> None:
    check_admin_password(admin_password)
    data_dir = Path(data_dir)
    path = db_path(data_dir)
    if path.exists():
        raise InitError(f"数据库已存在，拒绝覆盖：{path}")
    covers = data_dir / "covers"
    try:
        conn = connect(path)
        try:
            create_schema(conn)
            with write_tx(conn):
                conn.executemany("INSERT INTO tag (tid, tname) VALUES (?, ?)", TAGS)
                conn.executemany(
                    "INSERT INTO book (bid, bname, publishers, stock, price_cents, tid, url, cont) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", BOOKS)
                conn.execute("INSERT INTO user (uname, upwd, role) VALUES (?, ?, 2)",
                             ("admin", generate_password_hash(admin_password)))
        finally:
            conn.close()
        covers.mkdir(exist_ok=True)
        for src in SEED_COVERS.iterdir():
            shutil.copyfile(src, covers / src.name)
    except BaseException:
        for suffix in ("", "-wal", "-shm"):
            p = path.with_name(path.name + suffix)
            if p.exists():
                p.unlink()
        raise


def _interactive() -> bool:
    """stdin 是不是真正的终端。Windows 上 NUL 设备的 isatty() 也是 True，要再查控制台模式。"""
    if sys.stdin is None or not sys.stdin.isatty():
        return False
    if os.name != "nt":
        return True
    import ctypes
    import msvcrt

    try:
        handle = msvcrt.get_osfhandle(sys.stdin.fileno())
    except OSError:
        return False
    mode = ctypes.c_uint32()
    return bool(ctypes.windll.kernel32.GetConsoleMode(ctypes.c_void_p(handle), ctypes.byref(mode)))


def _read_password() -> str:
    pw = os.environ.get("BOOKSHOP_ADMIN_PASSWORD")
    if pw is not None:
        return pw
    if not _interactive():
        raise InitError("请设置环境变量 BOOKSHOP_ADMIN_PASSWORD，或在交互终端中运行以便输入管理员口令。")
    first = getpass.getpass("管理员 admin 的口令：")
    if first != getpass.getpass("再输入一次："):
        raise InitError("两次输入的口令不一致。")
    return first


def main() -> int:
    check_interpreter()
    config = load_config(require_secret=False)
    try:
        init_db(config.data_dir, _read_password())
    except InitError as e:
        sys.stderr.write(f"初始化失败：{e}\n")
        return 1
    print(f"初始化完成：{len(TAGS)} 个分类、{len(BOOKS)} 本演示书、管理员 admin。演示数据中的价格、库存、简介是占位值。")
    return 0

"""SQLite 连接（REQ-DATA-002、MIG-RULE-012、DEC-006）。"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from flask import current_app, g

DB_NAME = "bookshop.db"


def db_path(data_dir: Path) -> Path:
    return Path(data_dir) / DB_NAME


def connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path, isolation_level=None, timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = connect(db_path(current_app.config["BOOKSHOP"].data_dir))
    return g.db


def close_db(exc=None) -> None:
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


@contextmanager
def write_tx(conn: sqlite3.Connection | None = None):
    """写事务：BEGIN IMMEDIATE 先拿写锁，正常退出 COMMIT，异常 ROLLBACK 后继续抛出。

    依赖数据库状态的校验（存在、在架、库存、重名、草稿）要放在同一个事务里（MIG-RULE-012）。
    """
    conn = conn if conn is not None else get_db()
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    conn.execute("COMMIT")

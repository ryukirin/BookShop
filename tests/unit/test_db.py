"""TEST-016（单元部分）：连接与事务（REQ-DATA-002、MIG-RULE-012、LEGACY-058、COMP-006、EXP-013）。"""
import os
import sqlite3
import threading

import pytest

pytestmark = pytest.mark.batch(2)


@pytest.fixture
def path(seeded):
    from bookshop_web.db import db_path

    return db_path(seeded)


def test_connect_pragmas(path):
    from bookshop_web.db import connect

    c = connect(path)
    try:
        assert c.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert c.execute("PRAGMA busy_timeout").fetchone()[0] == 5000
        assert c.isolation_level is None
    finally:
        c.close()


def test_write_tx_commits_and_rolls_back(path):
    from bookshop_web.db import connect, write_tx

    c = connect(path)
    try:
        with write_tx(c):
            c.execute("UPDATE book SET stock = 7 WHERE bid = 1")
        assert c.execute("SELECT stock FROM book WHERE bid = 1").fetchone()[0] == 7
        with pytest.raises(RuntimeError):
            with write_tx(c):
                c.execute("UPDATE book SET stock = 3 WHERE bid = 1")
                raise RuntimeError("boom")
        assert c.execute("SELECT stock FROM book WHERE bid = 1").fetchone()[0] == 7
        assert not c.in_transaction
    finally:
        c.close()


def test_concurrent_immediate_writers(path):
    """20 个线程各自连接，在 BEGIN IMMEDIATE 里先查后写，抢购库存 5 的书。"""
    from bookshop_web.db import connect, write_tx

    c = connect(path)
    c.execute("UPDATE book SET stock = 5 WHERE bid = 9")
    c.close()
    out, barrier = [], threading.Barrier(20)

    def buyer():
        conn = connect(path)
        try:
            barrier.wait()
            with write_tx(conn):
                if conn.execute("SELECT stock FROM book WHERE bid = 9").fetchone()[0] <= 0:
                    out.append("soldout")
                    return
                conn.execute("UPDATE book SET stock = stock - 1 WHERE bid = 9")
                conn.execute("INSERT INTO orders (bid, uid, unit_price_cents) VALUES (9, 1, 3980)")
                out.append("ok")
        except sqlite3.Error as e:
            out.append(f"error:{e}")
        finally:
            conn.close()

    threads = [threading.Thread(target=buyer) for _ in range(20)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    c = connect(path)
    try:
        assert sorted(out) == ["ok"] * 5 + ["soldout"] * 15, out
        assert c.execute("SELECT stock FROM book WHERE bid = 9").fetchone()[0] == 0
        assert c.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 5
    finally:
        c.close()


def test_files_deletable_after_close(path):
    from bookshop_web.db import connect

    c = connect(path)
    c.execute("SELECT COUNT(*) FROM book").fetchone()
    c.close()
    for suffix in ("", "-wal", "-shm"):
        p = str(path) + suffix
        if os.path.exists(p):
            os.remove(p)
    assert not os.path.exists(path)

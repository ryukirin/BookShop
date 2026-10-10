"""TEST-015：表结构与约束（REQ-DATA-001、LEGACY-064、LEGACY-065、GAP-001、EXP-003、EXP-013）。"""
import sqlite3

import pytest

from tests.conftest import ADMIN_PASSWORD, db

pytestmark = pytest.mark.batch(2)


@pytest.fixture
def conn(seeded):
    c = db(seeded)
    yield c
    c.close()


def test_tables_and_no_customer(conn):
    names = {r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert names - {"sqlite_sequence"} == {"user", "tag", "book", "orders", "addbook_draft"}


def test_all_tables_strict(conn):
    rows = conn.execute("PRAGMA table_list").fetchall()
    strict = {r["name"]: r["strict"] for r in rows if r["schema"] == "main" and not r["name"].startswith("sqlite_")}
    assert strict and all(strict.values()), strict


def test_wal_and_user_version(conn):
    assert conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    assert conn.execute("PRAGMA user_version").fetchone()[0] == 1


@pytest.mark.parametrize("sql", [
    "INSERT INTO book (bname, publishers, stock, price_cents, tid, url, cont) VALUES ('x', 'x', 1, 1, 99, 'x.jpg', 'x')",
    "INSERT INTO orders (bid, uid, unit_price_cents) VALUES (999, 1, 100)",
    "INSERT INTO orders (bid, uid, unit_price_cents) VALUES (1, 999, 100)",
])
def test_foreign_keys(conn, sql):
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
        conn.execute(sql)


def test_uname_nocase_unique(conn):
    with pytest.raises(sqlite3.IntegrityError, match="UNIQUE"):
        conn.execute("INSERT INTO user (uname, upwd, role) VALUES ('Admin', 'h', 1)")


def test_tname_nocase_unique(conn):
    conn.execute("INSERT INTO tag (tid, tname) VALUES (10, 'Poetry')")
    with pytest.raises(sqlite3.IntegrityError, match="UNIQUE"):
        conn.execute("INSERT INTO tag (tid, tname) VALUES (11, 'poetry')")


@pytest.mark.parametrize("sql", [
    "INSERT INTO user (uname, upwd, role) VALUES ('x', 'h', 3)",
    "INSERT INTO user (uname, upwd, role) VALUES ('', 'h', 1)",
    "INSERT INTO user (uname, upwd, role) VALUES ('" + "a" * 21 + "', 'h', 1)",
    "INSERT INTO user (uname, upwd, role, active) VALUES ('x', 'h', 1, 2)",
    "INSERT INTO book (bname, publishers, stock, price_cents, tid, url, cont) VALUES ('" + "a" * 101 + "', 'x', 1, 1, 1, 'x.jpg', 'x')",
    "INSERT INTO book (bname, publishers, stock, price_cents, tid, url, cont) VALUES ('x', 'x', 1, 1, 1, 'x.jpg', '" + "a" * 4001 + "')",
    "INSERT INTO book (bname, publishers, stock, price_cents, tid, url, cont) VALUES ('x', 'x', -1, 1, 1, 'x.jpg', 'x')",
    "INSERT INTO book (bname, publishers, stock, price_cents, tid, url, cont) VALUES ('x', 'x', 1000000, 1, 1, 'x.jpg', 'x')",
    "INSERT INTO book (bname, publishers, stock, price_cents, tid, url, cont) VALUES ('x', 'x', 1, 10000000, 1, 'x.jpg', 'x')",
    "INSERT INTO book (bname, publishers, stock, price_cents, tid, url, cont, on_sale) VALUES ('x', 'x', 1, 1, 1, 'x.jpg', 'x', 2)",
    "UPDATE book SET stock = stock - 101 WHERE bid = 1",
])
def test_checks(conn, sql):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(sql)


def test_strict_rejects_text_in_integer(conn):
    with pytest.raises(sqlite3.Error):
        conn.execute("INSERT INTO book (bname, publishers, stock, price_cents, tid, url, cont) VALUES ('x', 'x', 'abc', 1, 1, 'x.jpg', 'x')")


def test_strict_coerces_lossless_text(conn):
    """记录 COMP-003：'5.00' 会被无损转成 5，所以校验必须在应用层做。"""
    cur = conn.execute("INSERT INTO book (bname, publishers, stock, price_cents, tid, url, cont) VALUES ('x', 'x', '5.00', 1, 1, 'x.jpg', 'x')")
    assert tuple(conn.execute("SELECT stock, typeof(stock) FROM book WHERE bid = ?", (cur.lastrowid,)).fetchone()) == (5, "integer")


def test_autoincrement_continues_after_seed(conn):
    cur = conn.execute("INSERT INTO book (bname, publishers, stock, price_cents, tid, url, cont) VALUES ('x', 'x', 1, 1, 1, 'x.jpg', 'x')")
    assert cur.lastrowid == 12

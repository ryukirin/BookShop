"""EXP-013：SQLite 写事务（BEGIN IMMEDIATE、WAL、busy_timeout）、NOCASE，以及 Windows 上的文件清理。"""
import os
import sqlite3
import sys
import tempfile
import threading
from pathlib import Path

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))


def connect(db):
    conn = sqlite3.connect(db, isolation_level=None, timeout=5.0, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def run(db):
    c = connect(db)
    mode = c.execute("PRAGMA journal_mode = WAL").fetchone()[0]
    check("journal_mode 设为 WAL", mode == "wal", mode)
    c.executescript("""
    CREATE TABLE user (uid INTEGER PRIMARY KEY, uname TEXT NOT NULL COLLATE NOCASE UNIQUE) STRICT;
    CREATE TABLE book (bid INTEGER PRIMARY KEY, stock INTEGER NOT NULL CHECK (stock >= 0)) STRICT;
    CREATE TABLE orders (oid INTEGER PRIMARY KEY, bid INTEGER NOT NULL REFERENCES book(bid), uid INTEGER NOT NULL) STRICT;
    INSERT INTO book VALUES (1, 5);
    """)

    # 20 个线程、各用自己的连接，同时抢购库存 5 的书：先查后写，放在同一个 BEGIN IMMEDIATE 事务里
    out, barrier = [], threading.Barrier(20)

    def buyer():
        conn = connect(db)
        try:
            barrier.wait()
            conn.execute("BEGIN IMMEDIATE")
            stock = conn.execute("SELECT stock FROM book WHERE bid = 1").fetchone()[0]
            if stock <= 0:
                conn.execute("ROLLBACK")
                out.append("soldout")
                return
            conn.execute("UPDATE book SET stock = stock - 1 WHERE bid = 1")
            conn.execute("INSERT INTO orders (bid, uid) VALUES (1, 1)")
            conn.execute("COMMIT")
            out.append("ok")
        except sqlite3.Error as e:
            out.append("error:" + str(e))
        finally:
            conn.close()

    threads = [threading.Thread(target=buyer) for _ in range(20)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    stock = c.execute("SELECT stock FROM book WHERE bid = 1").fetchone()[0]
    orders = c.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    check("20 个并发购买：恰好 5 单成功、15 个售罄、没有锁错误，库存为 0",
          out.count("ok") == 5 and out.count("soldout") == 15 and stock == 0 and orders == 5,
          f"ok={out.count('ok')} soldout={out.count('soldout')} errors={[o for o in out if o.startswith('error')]}")

    # 10 个线程同时用同一个用户名注册：查重和插入在同一个事务里
    out2, barrier2 = [], threading.Barrier(10)

    def register(name):
        conn = connect(db)
        try:
            barrier2.wait()
            conn.execute("BEGIN IMMEDIATE")
            if conn.execute("SELECT 1 FROM user WHERE uname = ?", (name,)).fetchone():
                conn.execute("ROLLBACK")
                out2.append("taken")
                return
            conn.execute("INSERT INTO user (uname) VALUES (?)", (name,))
            conn.execute("COMMIT")
            out2.append("ok")
        except sqlite3.Error as e:
            out2.append("error:" + str(e))
        finally:
            conn.close()

    names = ["zhangsan", "ZhangSan", "ZHANGSAN", "zhangsan", "Zhangsan", "zhangSan", "zhangsan", "ZHANGsan", "zhangsan", "zhangsan"]
    threads = [threading.Thread(target=register, args=(n,)) for n in names]
    [t.start() for t in threads]
    [t.join() for t in threads]
    check("10 个并发注册（大小写各异的同一用户名）：恰好 1 个成功，其余提示已占用",
          out2.count("ok") == 1 and out2.count("taken") == 9, str(out2))

    try:
        c.execute("INSERT INTO user (uname) VALUES ('ZhangSan')")
        check("NOCASE 唯一约束拒绝只差大小写的用户名", False)
    except sqlite3.IntegrityError as e:
        check("NOCASE 唯一约束拒绝只差大小写的用户名", True, str(e))
    hit = c.execute("SELECT uname FROM user WHERE uname = ?", ("ZHANGSAN",)).fetchone()
    check("按用户名等值查询时不区分 ASCII 大小写（登录、会员搜索）", hit is not None, str(hit))
    c.execute("INSERT INTO user (uname) VALUES ('Äb')")
    try:
        c.execute("INSERT INTO user (uname) VALUES ('äb')")
        check("NOCASE 只折叠 ASCII：Äb 和 äb 被当作不同的用户名", True)
    except sqlite3.IntegrityError:
        check("NOCASE 只折叠 ASCII：Äb 和 äb 被当作不同的用户名", False)
    c.close()


with tempfile.TemporaryDirectory() as d:
    db = str(Path(d) / "t.db")
    run(db)
    leftovers = sorted(os.listdir(d))
    for name in leftovers:
        os.remove(Path(d) / name)
    check("所有连接关闭后，数据库文件和 -wal/-shm 文件都能删除（Windows 不锁文件）", not os.listdir(d), str(leftovers))

print(f"python {sys.version.split()[0]} sqlite {sqlite3.sqlite_version}")
failed = 0
for name, ok, detail in RESULTS:
    failed += not ok
    print(("PASS " if ok else "FAIL ") + "EXP-013 " + name + (f"  [{detail}]" if detail else ""))
sys.exit(1 if failed else 0)

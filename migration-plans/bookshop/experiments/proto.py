"""可行性原型：只验证 migration-strategy 里的 EXP-002～EXP-007，不是实现代码。"""
import io
import sqlite3
import sys
import tempfile
import time
from datetime import timedelta
from pathlib import Path

from flask import Flask, abort, redirect, render_template_string, request, send_file, session
from werkzeug.security import check_password_hash, generate_password_hash

COVERS = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[3] / "BookShop" / "WebContent" / "img"
RESULTS = []


def check(exp, name, cond, detail=""):
    RESULTS.append((exp, name, bool(cond), detail))


SCHEMA = """
CREATE TABLE user (
  uid INTEGER PRIMARY KEY AUTOINCREMENT,
  uname TEXT NOT NULL UNIQUE,
  upwd TEXT NOT NULL,
  role INTEGER NOT NULL CHECK (role IN (1, 2)),
  active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1))
) STRICT;
CREATE TABLE tag (tid INTEGER PRIMARY KEY, tname TEXT NOT NULL UNIQUE) STRICT;
CREATE TABLE book (
  bid INTEGER PRIMARY KEY AUTOINCREMENT,
  bname TEXT NOT NULL, publishers TEXT NOT NULL,
  stock INTEGER NOT NULL CHECK (stock >= 0),
  price_cents INTEGER NOT NULL CHECK (price_cents >= 0),
  tid INTEGER NOT NULL REFERENCES tag(tid),
  url TEXT NOT NULL, cont TEXT NOT NULL,
  on_sale INTEGER NOT NULL DEFAULT 1 CHECK (on_sale IN (0, 1))
) STRICT;
CREATE TABLE orders (
  oid INTEGER PRIMARY KEY AUTOINCREMENT,
  bid INTEGER NOT NULL REFERENCES book(bid),
  uid INTEGER NOT NULL REFERENCES user(uid),
  unit_price_cents INTEGER NOT NULL
) STRICT;
"""

CATALOGUE = """
SELECT b.bid, b.bname, b.url, b.cont, b.price_cents, COUNT(o.oid) AS num
FROM book b JOIN tag t ON b.tid = t.tid LEFT JOIN orders o ON o.bid = b.bid
WHERE b.on_sale = 1 AND b.bname LIKE '%' || ? || '%'
GROUP BY b.bid ORDER BY num DESC, b.bid ASC
"""


def connect(path):
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def exp003(db):
    conn = connect(db)
    conn.executescript(SCHEMA)
    conn.executemany("INSERT INTO tag VALUES (?, ?)", [(1, "小说"), (2, "散文")])
    conn.execute("INSERT INTO user (uname, upwd, role) VALUES ('张三', 'x', 1)")
    rows = [("清欢", "河北教育出版社", 1, 3200, 2, "b6.jpg", "林清玄"),
            ("清欢", "另一出版社", 5, 3000, 2, "b7.jpg", "同名书"),
            ("Python入门", "测试", 10, 2550, 1, "x.jpg", "测试")]
    conn.executemany("INSERT INTO book (bname, publishers, stock, price_cents, tid, url, cont) VALUES (?,?,?,?,?,?,?)", rows)
    conn.commit()

    fk_off = sqlite3.connect(db)  # 不开 PRAGMA 的连接
    fk_off.execute("INSERT INTO book (bname, publishers, stock, price_cents, tid, url, cont) VALUES ('x','x',1,1,99,'x','x')")
    fk_off.rollback()
    fk_off.close()
    check("EXP-003", "未开 PRAGMA 时外键不生效（证明每个连接都要开）", True)
    try:
        conn.execute("INSERT INTO book (bname, publishers, stock, price_cents, tid, url, cont) VALUES ('x','x',1,1,99,'x','x')")
        check("EXP-003", "开 PRAGMA 后不存在的分类被外键拒绝", False)
    except sqlite3.IntegrityError as e:
        check("EXP-003", "开 PRAGMA 后不存在的分类被外键拒绝", True, str(e))
    for sql, name in [("INSERT INTO user (uname, upwd, role) VALUES ('张三','y',1)", "用户名唯一"),
                      ("INSERT INTO user (uname, upwd, role) VALUES ('李四','y',3)", "role 只能是 1/2"),
                      ("INSERT INTO book (bname, publishers, stock, price_cents, tid, url, cont) VALUES ('x','x','abc',1,1,'x','x')", "STRICT 表拒绝把非数字文本写进 INTEGER")]:
        try:
            conn.execute(sql)
            check("EXP-003", name, False)
        except sqlite3.IntegrityError as e:
            check("EXP-003", name, True, str(e))
        except sqlite3.Error as e:
            check("EXP-003", name, True, type(e).__name__ + ": " + str(e))

    cur = conn.execute("INSERT INTO book (bname, publishers, stock, price_cents, tid, url, cont) VALUES ('coerce','x','5.00',1,1,'x','x')")
    got = conn.execute("SELECT stock, typeof(stock) FROM book WHERE bid = ?", (cur.lastrowid,)).fetchone()
    check("EXP-003", "STRICT 会把能无损转换的 '5.00' 收成整数 5（校验必须在应用层做）", got == (5, "integer"), str(got))
    conn.execute("DELETE FROM book WHERE bid = ?", (cur.lastrowid,))
    # 原子购买：库存 1 的书买两次，第二次失败
    def buy(bid, uid):
        with conn:
            cur = conn.execute("UPDATE book SET stock = stock - 1 WHERE bid = ? AND on_sale = 1 AND stock > 0", (bid,))
            if cur.rowcount != 1:
                return False
            conn.execute("INSERT INTO orders (bid, uid, unit_price_cents) SELECT bid, ?, price_cents FROM book WHERE bid = ?", (uid, bid))
            return True
    check("EXP-003", "库存 1 时第一次购买成功", buy(1, 1))
    check("EXP-003", "库存 0 时第二次购买被拒绝，库存不为负", (not buy(1, 1)) and conn.execute("SELECT stock FROM book WHERE bid=1").fetchone()[0] == 0)
    conn.execute("UPDATE book SET price_cents = 9900 WHERE bid = 1")
    snap = conn.execute("SELECT unit_price_cents FROM orders WHERE bid = 1").fetchone()[0]
    check("EXP-003", "改价后订单仍保留成交价 3200 分", snap == 3200, f"unit_price_cents={snap}")

    allrows = conn.execute(CATALOGUE, ("",)).fetchall()
    names = [r[1] for r in allrows]
    check("EXP-003", "同名同分类的两本书按 bid 分开列出", names.count("清欢") == 2, str(names))
    check("EXP-003", "按销量降序，销量相同按 bid 升序", [r[0] for r in allrows] == [1, 2, 3], str([(r[0], r[5]) for r in allrows]))
    check("EXP-003", "LIKE 对 ASCII 不区分大小写（python 命中 Python入门）", len(conn.execute(CATALOGUE, ("python",)).fetchall()) == 1)
    check("EXP-003", "LIKE 匹配中文子串（欢）", len(conn.execute(CATALOGUE, ("欢",)).fetchall()) == 2)
    check("EXP-003", "LIKE 中用户输入的 % 仍是通配符（与旧系统一致）", len(conn.execute(CATALOGUE, ("%",)).fetchall()) == 3)
    conn.execute("UPDATE book SET on_sale = 0 WHERE bid = 2")
    check("EXP-003", "下架的书不出现在书目里", [r[0] for r in conn.execute(CATALOGUE, ("",)).fetchall()] == [1, 3])
    rev = conn.execute("SELECT SUM(unit_price_cents) FROM orders o JOIN book b ON o.bid=b.bid JOIN user u ON o.uid=u.uid").fetchone()[0]
    check("EXP-003", "账目按成交价求和（整数分，无浮点误差）", rev == 3200, f"sum={rev}")
    conn.commit()
    return conn


def exp004():
    t = time.perf_counter()
    h = generate_password_hash("abc123")
    dt = (time.perf_counter() - t) * 1000
    check("EXP-004", "默认方法是 scrypt:32768:8:1", h.startswith("scrypt:32768:8:1$"), h.split("$")[0])
    check("EXP-004", "check_password_hash 正确/错误口令", check_password_hash(h, "abc123") and not check_password_hash(h, "abc124"))
    check("EXP-004", f"单次哈希耗时 {dt:.0f} ms（< 1000 ms）", dt < 1000, f"len={len(h)}")


def make_app(db):
    app = Flask(__name__)
    app.config.update(SECRET_KEY="x" * 64, SESSION_COOKIE_SAMESITE="Lax",
                      PERMANENT_SESSION_LIFETIME=timedelta(minutes=30), MAX_CONTENT_LENGTH=5 * 1024 * 1024)
    page = "<ul>{% for b in books %}<li>{{ b[1] }}</li>{% endfor %}</ul>"

    @app.get("/BookShop/jsp/book.action")
    def book_action():
        op = request.args.get("opttype")
        if op == "queryBytag":
            session["catalogue"] = {"tname": request.args["tname"]}
            return redirect("buy.jsp")
        abort(400)

    @app.get("/BookShop/jsp/buy.jsp")
    def buy_jsp():
        crit = session.get("catalogue")
        if not crit:
            return render_template_string(page, books=[])
        conn = connect(db)
        try:
            rows = conn.execute("SELECT b.bid, b.bname FROM book b JOIN tag t ON b.tid=t.tid WHERE t.tname = ? AND b.on_sale = 1", (crit["tname"],)).fetchall()
        finally:
            conn.close()
        return render_template_string(page, books=rows)

    @app.post("/BookShop/login.action")
    def login():
        session.clear()
        session.permanent = True
        session["uid"] = 1
        return redirect("index.jsp")

    @app.post("/BookShop/logout")
    def logout():
        session.clear()
        return redirect("login.jsp")

    @app.post("/BookShop/jsp/upload")
    def upload():
        f = request.files["file"]
        head = f.stream.read(8)
        if not (head.startswith(b"\x89PNG\r\n\x1a\n") or head.startswith(b"\xff\xd8\xff")):
            abort(400)
        return "ok"

    @app.get("/BookShop/jsp/showpic.jsp")
    def showpic():
        name = request.args.get("img", "")
        target = (COVERS / name).resolve()
        if COVERS.resolve() not in target.parents or not target.is_file():
            abort(404)
        head = target.read_bytes()[:8]
        mime = "image/png" if head.startswith(b"\x89PNG") else "image/jpeg" if head.startswith(b"\xff\xd8\xff") else None
        if mime is None:
            abort(404)
        return send_file(target, mimetype=mime)

    return app


def exp_web(db):
    app = make_app(db)
    c = app.test_client()
    # EXP-002
    r = c.get("/BookShop/jsp/book.action?opttype=queryBytag&tname=%E6%95%A3%E6%96%87")
    check("EXP-002", "旧 URL 路由可用，查询后 302 到 buy.jsp", r.status_code == 302 and r.headers["Location"].endswith("buy.jsp"), r.headers.get("Location", ""))
    r = c.get("/BookShop/jsp/buy.jsp")
    check("EXP-002", "UTF-8 编码的中文 GET 参数“散文”被正确解码并查到“清欢”", "清欢" in r.get_data(as_text=True))
    check("EXP-002", "缺少 opttype 返回 400", c.get("/BookShop/jsp/book.action").status_code == 400)
    check("EXP-002", "未定义的 opttype 返回 400", c.get("/BookShop/jsp/book.action?opttype=nope").status_code == 400)
    check("EXP-002", "查询类 URL 用 POST 访问返回 405", c.post("/BookShop/jsp/book.action?opttype=queryBytag&tname=x").status_code == 405)
    # EXP-005
    conn = connect(db)
    conn.execute("INSERT INTO book (bname, publishers, stock, price_cents, tid, url, cont) VALUES ('<script>alert(1)</script>','x',1,1,2,'x','x')")
    conn.commit()
    conn.close()
    body = c.get("/BookShop/jsp/buy.jsp").get_data(as_text=True)
    check("EXP-005", "书名中的 <script> 被转义输出", "&lt;script&gt;" in body and "<script>" not in body)
    # EXP-006
    c2 = app.test_client()
    c2.get("/BookShop/jsp/book.action?opttype=queryBytag&tname=x")
    before = c2.get_cookie("session").value
    r = c2.post("/BookShop/login.action")
    sc = r.headers.get("Set-Cookie", "")
    after = c2.get_cookie("session").value
    check("EXP-006", "登录后会话 Cookie 换了新值（旧值里没有 uid）", before != after)
    check("EXP-006", "Cookie 带 HttpOnly 和 SameSite=Lax", "HttpOnly" in sc and "SameSite=Lax" in sc, sc[:120])
    check("EXP-006", "permanent 会话的有效期是 30 分钟", "Expires=" in sc)
    c2.post("/BookShop/logout")
    with c2.session_transaction() as s:
        check("EXP-006", "退出后会话里没有 uid", "uid" not in s)
    # EXP-007
    big = io.BytesIO(b"\xff\xd8\xff" + b"0" * (6 * 1024 * 1024))
    check("EXP-007", "超过 5 MB 的上传返回 413", c.post("/BookShop/jsp/upload", data={"file": (big, "a.jpg")}, content_type="multipart/form-data").status_code == 413)
    check("EXP-007", "扩展名是 .jpg 但内容不是图片时被拒绝", c.post("/BookShop/jsp/upload", data={"file": (io.BytesIO(b"GIF89a....."), "a.jpg")}, content_type="multipart/form-data").status_code == 400)
    check("EXP-007", "大写扩展名 .PNG 的真实 PNG 被接受", c.post("/BookShop/jsp/upload", data={"file": (io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"0" * 10), "A.PNG")}, content_type="multipart/form-data").status_code == 200)
    kinds = {}
    for name in ["b1.jpg", "b2.jpg", "b3.jpg", "b4.jpg", "b5.jpg", "b6.jpg", "b7.jpg", "b8.jpg", "b9.jpg", "b11.jpg"]:
        r = c.get(f"/BookShop/jsp/showpic.jsp?img={name}")
        kinds[name] = (r.status_code, r.mimetype)
    check("EXP-007", "10 张种子封面都能输出，b6/b8 按内容识别为 image/png", all(v[0] == 200 for v in kinds.values()) and kinds["b6.jpg"][1] == "image/png" and kinds["b8.jpg"][1] == "image/png" and kinds["b1.jpg"][1] == "image/jpeg", str(kinds))
    check("EXP-007", "路径穿越 ../ 返回 404", c.get("/BookShop/jsp/showpic.jsp?img=../WEB-INF/web.xml").status_code == 404)
    check("EXP-007", "不存在的封面返回 404（旧系统是 500）", c.get("/BookShop/jsp/showpic.jsp?img=nope.jpg").status_code == 404)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as d:
        db = str(Path(d) / "t.db")
        conn = exp003(db)
        conn.close()
        exp004()
        exp_web(db)
    print(f"python {sys.version.split()[0]} sqlite {sqlite3.sqlite_version}")
    failed = 0
    for exp, name, ok, detail in RESULTS:
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL'} {exp} {name}" + (f"  [{detail}]" if detail else ""))
    print(f"total={len(RESULTS)} failed={failed}")
    sys.exit(1 if failed else 0)

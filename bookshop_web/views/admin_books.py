"""管理端书籍管理：列表、搜索、两步新增、修改、下架（REQ-BOOK-001～REQ-BOOK-006）。

检查顺序按 MIG-RULE-019：参数不合规 400 → 资源不存在或已下架 404 → 字段不合规 alert。
"""
from __future__ import annotations

import shutil
import uuid

from flask import abort, g, redirect, render_template, request, session

from .. import covers
from ..db import get_db, write_tx
from ..dispatch import action, page
from ..money import parse_price
from ..responses import alert, bad_request
from ..validation import positive_id, stock, text

ADMIN = "/BookShop/jsp/admin.action"
BOOKS_SELECT = ("SELECT b.bid, b.bname, b.cont, b.publishers, t.tname, b.stock, b.price_cents, COUNT(o.oid) AS num "
                "FROM book b JOIN tag t ON t.tid = b.tid LEFT JOIN orders o ON o.bid = b.bid WHERE b.on_sale = 1")
BOOKS_ORDER = " GROUP BY b.bid ORDER BY b.bid ASC"
BOOKS_ALL = BOOKS_SELECT + BOOKS_ORDER
BOOKS_BY_NAME = BOOKS_SELECT + " AND b.bname LIKE '%' || ? || '%'" + BOOKS_ORDER
ON_SALE = "SELECT bid, publishers, stock, price_cents FROM book WHERE bid = ? AND on_sale = 1"
TAGS = "SELECT tid, tname FROM tag ORDER BY tid"
SAVE_DRAFT = ("INSERT OR REPLACE INTO addbook_draft (uid, bname, publishers, stock, price_cents, tid, cont) "
              "VALUES (?, ?, ?, ?, ?, ?, ?)")
INSERT_BOOK = ("INSERT INTO book (bname, publishers, stock, price_cents, tid, url, cont) "
               "VALUES (?, ?, ?, ?, ?, ?, ?)")


class _NoDraft(Exception):
    pass


# ---------- 列表与搜索 ----------

@action(ADMIN, "queryAllbooks")
def query_all_books():
    session["q_admin_books"] = {"op": "all"}
    return redirect("bookadmin.jsp")


@action(ADMIN, "queryBooks")
def query_books():
    q = text("q_book", request.args.get("bname", ""))
    if q is None:
        bad_request("param")
    session["q_admin_books"] = {"op": "name", "q": q}
    return redirect("bookadmin.jsp")


def _books(criteria) -> list:
    db = get_db()
    if criteria == {"op": "all"}:
        return db.execute(BOOKS_ALL).fetchall()
    if isinstance(criteria, dict) and criteria.get("op") == "name" and isinstance(criteria.get("q"), str):
        return db.execute(BOOKS_BY_NAME, (criteria["q"],)).fetchall()
    return []


@page("/BookShop/jsp/bookadmin.jsp")
def bookadmin_page():
    return render_template("bookadmin.html", side="books", books=_books(session.get("q_admin_books")))


# ---------- 两步新增 ----------

@page("/BookShop/jsp/add.jsp")
def add_page():
    return render_template("add.html", side="books", tags=get_db().execute(TAGS).fetchall())


@action(ADMIN, "addBooks")
def add_books():
    f = request.form
    fields = (text("bname", f.get("bname")), text("publishers", f.get("publishers")), text("cont", f.get("cont")),
              stock(f.get("stock")), parse_price(f.get("price")), positive_id(f.get("tid")))
    if any(v is None for v in fields):
        return alert("check_book_info", "add.jsp")
    bname, publishers, cont, stock_n, price_cents, tid = fields
    db = get_db()
    with write_tx(db):
        if db.execute("SELECT 1 FROM tag WHERE tid = ?", (tid,)).fetchone() is None:
            return alert("check_book_info", "add.jsp")
        db.execute(SAVE_DRAFT, (g.user["uid"], bname, publishers, stock_n, price_cents, tid, cont))
    return redirect("addnext.jsp")


@page("/BookShop/jsp/addnext.jsp")
def addnext_page():
    return render_template("addnext.html", side="books")


@action(ADMIN, "addBooksimg")
def add_books_img():
    uid = g.user["uid"]
    db = get_db()
    if db.execute("SELECT 1 FROM addbook_draft WHERE uid = ?", (uid,)).fetchone() is None:
        return alert("fill_book_first", "add.jsp")
    upload = request.files.get("file")
    mime = covers.sniff(upload.stream.read(8)) if upload is not None and upload.filename else None
    if mime is None:
        return alert("upload_image", "addnext.jsp")
    # 文件名由服务器生成，不用客户端提供的名字（LEGACY-054、LEGACY-072）。
    name = uuid.uuid4().hex + (".png" if mime == "image/png" else ".jpg")
    folder = covers.covers_dir()
    folder.mkdir(exist_ok=True)
    path = folder / name
    upload.stream.seek(0)
    with path.open("xb") as out:
        shutil.copyfileobj(upload.stream, out)
    # 先写文件再开事务；事务失败就删掉刚写的文件（COMP-024）。
    try:
        with write_tx(db):
            draft = db.execute("SELECT * FROM addbook_draft WHERE uid = ?", (uid,)).fetchone()
            if draft is None:
                raise _NoDraft
            db.execute(INSERT_BOOK, (draft["bname"], draft["publishers"], draft["stock"], draft["price_cents"],
                                     draft["tid"], name, draft["cont"]))
            db.execute("DELETE FROM addbook_draft WHERE uid = ?", (uid,))
    except _NoDraft:
        path.unlink(missing_ok=True)
        return alert("fill_book_first", "add.jsp")
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    return redirect("admin.action?opttype=queryAllbooks")


# ---------- 修改 ----------

@action(ADMIN, "showBooks")
def show_books():
    bid = positive_id(request.args.get("bid"))
    if bid is None:
        bad_request("param")
    if get_db().execute(ON_SALE, (bid,)).fetchone() is None:
        abort(404)
    session["edit_bid"] = bid
    return redirect("editbook.jsp")


@page("/BookShop/jsp/editbook.jsp")
def editbook_page():
    bid = session.get("edit_bid")
    book = None
    if isinstance(bid, int):
        book = get_db().execute(ON_SALE, (bid,)).fetchone()
        if book is None:
            abort(404)
    return render_template("editbook.html", side="books", book=book)


@action(ADMIN, "editBooks")
def edit_books():
    f = request.form
    bid = positive_id(f.get("bid"))
    if bid is None:
        bad_request("param")
    publishers, stock_n, price_cents = text("publishers", f.get("publishers")), stock(f.get("stock")), parse_price(f.get("price"))
    db = get_db()
    with write_tx(db):
        if db.execute(ON_SALE, (bid,)).fetchone() is None:
            abort(404)
        if publishers is None or stock_n is None or price_cents is None:
            return alert("check_book_info", f"admin.action?opttype=showBooks&bid={bid}")
        db.execute("UPDATE book SET publishers = ?, stock = ?, price_cents = ? WHERE bid = ?",
                   (publishers, stock_n, price_cents, bid))
    return redirect("admin.action?opttype=queryAllbooks")


# ---------- 下架 ----------

@action(ADMIN, "deleteBooks")
def delete_books():
    """“删除”改为下架：从书目中消失，订单、账目和封面文件保留（MIG-DEC-007）。"""
    bid = positive_id(request.form.get("bid"))
    if bid is None:
        bad_request("param")
    db = get_db()
    with write_tx(db):
        if db.execute(ON_SALE, (bid,)).fetchone() is None:
            abort(404)
        db.execute("UPDATE book SET on_sale = 0 WHERE bid = ?", (bid,))
    return redirect("admin.action?opttype=queryAllbooks")

"""会员端书目：列表、筛选、搜索、详情、封面（REQ-CATALOG-001～REQ-CATALOG-008）。"""
from __future__ import annotations

from flask import abort, render_template, request, send_file, session

from .. import covers
from ..db import get_db
from ..dispatch import action, page
from ..responses import bad_request
from ..validation import positive_id, text

BOOK = "/BookShop/jsp/book.action"

# 书目：按 bid 分组，销量 = 订单数，销量降序、同销量按 bid 升序，只列在架的书（LEGACY-013、LEGACY-046）。
LIST_SELECT = ("SELECT b.bid, b.bname, b.url, b.cont, COUNT(o.oid) AS num "
               "FROM book b JOIN tag t ON t.tid = b.tid LEFT JOIN orders o ON o.bid = b.bid "
               "WHERE b.on_sale = 1")
LIST_ORDER = " GROUP BY b.bid ORDER BY num DESC, b.bid ASC"
LIST_ALL = LIST_SELECT + LIST_ORDER
# LIKE 对 ASCII 不区分大小写；输入里的 % 和 _ 仍是通配符，和旧系统一致（LEGACY-016、COMP-005）。
LIST_BY_NAME = LIST_SELECT + " AND b.bname LIKE '%' || ? || '%'" + LIST_ORDER
# tname 列是 COLLATE NOCASE，等值比较不区分 ASCII 大小写（LEGACY-015、MIG-DEC-013）。
LIST_BY_TAG = LIST_SELECT + " AND t.tname = ?" + LIST_ORDER
TAGS = "SELECT tid, tname FROM tag ORDER BY tid"
DETAIL = ("SELECT b.bid, b.bname, b.publishers, b.cont, b.stock, b.price_cents, b.url, t.tname, "
          "(SELECT COUNT(*) FROM orders o WHERE o.bid = b.bid) AS num "
          "FROM book b JOIN tag t ON t.tid = b.tid WHERE b.bid = ? AND b.on_sale = 1")


def _list(criteria) -> list:
    db = get_db()
    if not isinstance(criteria, dict):
        return []
    op, q = criteria.get("op"), criteria.get("q")
    if op == "all":
        return db.execute(LIST_ALL).fetchall()
    if op == "name" and isinstance(q, str):
        return db.execute(LIST_BY_NAME, (q,)).fetchall()
    if op == "tag" and isinstance(q, str):
        return db.execute(LIST_BY_TAG, (q,)).fetchall()
    return []


@action(BOOK, "queryAllbook")
def query_all():
    session["q_catalogue"] = {"op": "all"}
    return redirect_buy()


@action(BOOK, "queryByname")
def query_by_name():
    q = text("q_book", request.args.get("bname", ""))
    if q is None:
        bad_request("param")
    session["q_catalogue"] = {"op": "name", "q": q}
    return redirect_buy()


@action(BOOK, "queryBytag")
def query_by_tag():
    q = text("tname", request.args.get("tname", ""))
    if q is None:
        bad_request("param")
    session["q_catalogue"] = {"op": "tag", "q": q}
    return redirect_buy()


def redirect_buy():
    from flask import redirect

    return redirect("buy.jsp")


@page("/BookShop/jsp/buy.jsp")
def buy_page():
    books = _list(session.get("q_catalogue")) if "q_catalogue" in session else []
    return render_template("buy.html", active="buy", books=books, tags=get_db().execute(TAGS).fetchall())


def on_sale_book(bid: int):
    return get_db().execute(DETAIL, (bid,)).fetchone()


@action(BOOK, "bookDetail")
def book_detail():
    from flask import redirect

    bid = positive_id(request.args.get("bid"))
    if bid is None:
        bad_request("param")
    if on_sale_book(bid) is None:
        abort(404)
    session["detail_bid"] = bid
    return redirect("bookdetails.jsp")


@page("/BookShop/jsp/bookdetails.jsp")
def details_page():
    bid = session.get("detail_bid")
    book = None
    if isinstance(bid, int):
        book = on_sale_book(bid)
        if book is None:
            abort(404)
    return render_template("bookdetails.html", active="buy", book=book)


@page("/BookShop/jsp/showpic.jsp")
def showpic():
    found = covers.find_cover(request.args.get("img", ""))
    if found is None:
        abort(404)
    path, mime = found
    return send_file(path, mimetype=mime)

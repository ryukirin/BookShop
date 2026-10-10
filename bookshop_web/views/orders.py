"""购买与我的订单（REQ-ORDER-001～REQ-ORDER-003）。"""
from __future__ import annotations

from flask import abort, g, redirect, render_template, request

from ..db import get_db, write_tx
from ..dispatch import action, page
from ..responses import alert, bad_request
from ..validation import positive_id

BOOK = "/BookShop/jsp/book.action"
MY = "/BookShop/jsp/my.action"
MY_ORDERS = ("SELECT u.uname, b.bname, o.unit_price_cents FROM orders o "
             "JOIN book b ON b.bid = o.bid JOIN user u ON u.uid = o.uid "
             "WHERE o.uid = ? ORDER BY o.oid")


@action(BOOK, "buybook")
def buybook():
    bid = positive_id(request.form.get("bid"))
    if bid is None:
        bad_request("param")
    db = get_db()
    # 在架检查、库存检查、扣库存、记成交价、插订单都在同一个写事务里（LEGACY-040、LEGACY-042）。
    with write_tx(db):
        book = db.execute("SELECT stock, price_cents FROM book WHERE bid = ? AND on_sale = 1", (bid,)).fetchone()
        if book is None:
            abort(404)
        sold = book["stock"] > 0
        if sold:
            db.execute("UPDATE book SET stock = stock - 1 WHERE bid = ?", (bid,))
            db.execute("INSERT INTO orders (bid, uid, unit_price_cents) VALUES (?, ?, ?)",
                       (bid, g.user["uid"], book["price_cents"]))
    if not sold:
        return alert("out_of_stock", f"book.action?opttype=bookDetail&bid={bid}")
    return redirect("my.action?opttype=queryMyorder")


@action(MY, "queryMyorder")
def query_my_orders():
    return redirect("myorder.jsp")


@page("/BookShop/jsp/myorder.jsp")
def myorder_page():
    rows = get_db().execute(MY_ORDERS, (g.user["uid"],)).fetchall()
    return render_template("myorder.html", side="orders", orders=rows)

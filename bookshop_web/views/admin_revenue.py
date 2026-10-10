"""管理端账目统计（REQ-REVENUE-001）。金额取成交价，合计用整数分精确求和。"""
from __future__ import annotations

from flask import redirect, render_template

from ..db import get_db
from ..dispatch import action, page

ADMIN = "/BookShop/jsp/admin.action"
ALL_ORDERS = ("SELECT o.oid, u.uname, b.bname, o.unit_price_cents FROM orders o "
              "JOIN user u ON u.uid = o.uid JOIN book b ON b.bid = o.bid ORDER BY o.oid")


@action(ADMIN, "showAllmoney")
def show_all_money():
    return redirect("oderadmin.jsp")


@page("/BookShop/jsp/oderadmin.jsp")
def orderadmin_page():
    rows = get_db().execute(ALL_ORDERS).fetchall()
    total = sum(r["unit_price_cents"] for r in rows)
    return render_template("oderadmin.html", side="money", orders=rows, total=total)

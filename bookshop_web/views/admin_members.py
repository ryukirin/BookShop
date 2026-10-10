"""管理端会员管理：列表、搜索、停用（REQ-MEMBER-001～REQ-MEMBER-003）。"""
from __future__ import annotations

from flask import abort, redirect, render_template, request, session

from ..db import get_db, write_tx
from ..dispatch import action, page
from ..responses import bad_request
from ..validation import positive_id, text

ADMIN = "/BookShop/jsp/admin.action"
MEMBERS_ALL = "SELECT uid, uname FROM user WHERE role = 1 AND active = 1 ORDER BY uid"
# uname 列是 COLLATE NOCASE，等值查找不区分 ASCII 大小写（MIG-DEC-013）。
MEMBERS_BY_NAME = "SELECT uid, uname FROM user WHERE role = 1 AND active = 1 AND uname = ? ORDER BY uid"


@action(ADMIN, "queryAllcustomers")
def query_all_customers():
    session["q_admin_customers"] = {"op": "all"}
    return redirect("admin.jsp")


@action(ADMIN, "queryCustomers")
def query_customers():
    q = text("q_member", request.args.get("uname", ""))
    if q is None:
        bad_request("param")
    session["q_admin_customers"] = {"op": "name", "q": q}
    return redirect("admin.jsp")


def _members(criteria) -> list:
    db = get_db()
    if criteria == {"op": "all"}:
        return db.execute(MEMBERS_ALL).fetchall()
    if isinstance(criteria, dict) and criteria.get("op") == "name" and isinstance(criteria.get("q"), str):
        return db.execute(MEMBERS_BY_NAME, (criteria["q"],)).fetchall()
    return []


@page("/BookShop/jsp/admin.jsp")
def admin_page():
    return render_template("admin.html", side="members", members=_members(session.get("q_admin_customers")))


@action(ADMIN, "deleteCustomers")
def delete_customers():
    """“删除”改为停用：只能停用未停用的会员（role 1），订单保留，会话立即失效（MIG-DEC-007）。"""
    uid = positive_id(request.form.get("uid"))
    if uid is None:
        bad_request("param")
    db = get_db()
    with write_tx(db):
        if db.execute("SELECT 1 FROM user WHERE uid = ? AND role = 1 AND active = 1", (uid,)).fetchone() is None:
            abort(404)
        db.execute("UPDATE user SET active = 0, session_version = session_version + 1 WHERE uid = ?", (uid,))
    return redirect("admin.action?opttype=queryAllcustomers")

"""账号与会话：注册、登录、退出、个人页、修改密码（REQ-ACCOUNT-001～REQ-ACCOUNT-007）。"""
from __future__ import annotations

import sqlite3

from flask import g, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from ..db import get_db, write_tx
from ..dispatch import LOGIN_PAGE, action, page
from ..responses import alert
from ..security import start_session
from ..validation import text

LOGIN = "/BookShop/login.action"
MY = "/BookShop/jsp/my.action"
ROLE_LABEL = {1: "会员", 2: "管理员"}
# 用户名不存在时也做一次哈希校验，让失败响应的耗时一致。
_DUMMY_HASH = generate_password_hash("bookshop-dummy-password")


@action(LOGIN, "addusers")
def addusers():
    uname = request.form.get("inputUname")
    pwd = request.form.get("inputPassword")
    again = request.form.get("checkPassword")
    if text("uname", uname) is None or text("upwd", pwd) is None:
        return alert("check_user_or_password", "register.jsp")
    pwd_hash = generate_password_hash(pwd) if pwd == again else None
    db = get_db()
    try:
        with write_tx(db):
            if db.execute("SELECT 1 FROM user WHERE uname = ?", (uname,)).fetchone():
                return alert("change_uname", "register.jsp")
            if pwd_hash is None:
                return alert("check_password", "register.jsp")
            db.execute("INSERT INTO user (uname, upwd, role) VALUES (?, ?, 1)", (uname, pwd_hash))
    except sqlite3.IntegrityError:
        return alert("fail_try_again", "register.jsp")
    return redirect("login.jsp")


@action(LOGIN, "checkUsers")
def check_users():
    uname = request.form.get("inputName", "")
    pwd = request.form.get("inputPassword", "")
    row = None
    if text("uname", uname) is not None:
        row = get_db().execute(
            "SELECT uid, upwd, role, active, session_version FROM user WHERE uname = ?", (uname,)
        ).fetchone()
    ok = check_password_hash(row["upwd"] if row else _DUMMY_HASH, pwd)
    if row is None or row["active"] != 1 or not ok:
        return alert("username_error", "login.jsp")
    start_session(row)
    return redirect("index.jsp" if row["role"] == 1 else "jsp/admin.action?opttype=queryAllcustomers")


def logout():
    """POST /BookShop/logout.action；方法和 CSRF 已由 dispatch 检查。递增版本号，所有设备上的会话一起失效。"""
    if g.user is not None:
        db = get_db()
        with write_tx(db):
            db.execute("UPDATE user SET session_version = session_version + 1 WHERE uid = ?", (g.user["uid"],))
    session.clear()
    return redirect(LOGIN_PAGE)


@action(MY, "initMypage")
def init_mypage():
    return redirect("my.jsp")


@page("/BookShop/jsp/my.jsp")
def my_page():
    return render_template("my.html", side="info", uname=g.user["uname"], role_label=ROLE_LABEL[g.user["role"]])


@page("/BookShop/jsp/changepwd.jsp")
def changepwd_page():
    return render_template("changepwd.html", side="pwd")


@action(MY, "updatePwd")
def update_pwd():
    old = request.form.get("oldpwd", "")
    new = request.form.get("newpwd", "")
    again = request.form.get("anewpwd", "")
    new_ok = new == again and text("upwd", new) is not None
    new_hash = generate_password_hash(new) if new_ok else None
    uid = g.user["uid"]
    db = get_db()
    with write_tx(db):
        row = db.execute("SELECT upwd, session_version FROM user WHERE uid = ?", (uid,)).fetchone()
        old_ok = check_password_hash(row["upwd"], old)
        if new_ok and old_ok:
            db.execute("UPDATE user SET upwd = ?, session_version = session_version + 1 WHERE uid = ?", (new_hash, uid))
            outcome = "success"
        elif not old_ok:
            outcome = "password_error"
        else:
            outcome = "check_new_password"
    if outcome == "success":
        session["sv"] = row["session_version"] + 1  # 当前会话换上新版本号，继续保持登录
    return alert(outcome, "changepwd.jsp")

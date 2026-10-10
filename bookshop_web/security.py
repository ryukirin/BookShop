"""会话加载与吊销、CSRF、管理员判断（REQ-ACCOUNT-003、REQ-ACCOUNT-004、REQ-PLATFORM-007、DEC-004、DEC-005）。

会话里只放：uid、sv（会话版本号）、login_at、csrf，以及页面查询条件
（q_catalogue、q_admin_books、q_admin_customers、detail_bid、edit_bid）。
"""
from __future__ import annotations

import hmac
import secrets
import time

from flask import g, request, session

from .responses import bad_request

ABSOLUTE_LIFETIME = 8 * 60 * 60
clock = time.time  # 测试可替换


def ensure_csrf() -> str:
    token = session.get("csrf")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf"] = token
        session.permanent = True
    return token


def check_csrf() -> None:
    sent = request.form.get("csrf_token", "")  # 读取表单时可能先触发 413
    expected = session.get("csrf")
    if not expected or not sent or not hmac.compare_digest(sent, expected):
        bad_request("csrf")


def load_user() -> None:
    """每个请求从数据库读取当前用户；会话无效时清空会话，按未登录处理。"""
    g.user = None
    uid = session.get("uid")
    if uid is None:
        return
    from .db import get_db

    row = get_db().execute(
        "SELECT uid, uname, role, active, session_version FROM user WHERE uid = ?", (uid,)
    ).fetchone()
    login_at = session.get("login_at")
    now = clock()
    if (
        row is None
        or row["active"] != 1
        or row["session_version"] != session.get("sv")
        or not isinstance(login_at, (int, float))
        or now - login_at > ABSOLUTE_LIFETIME
        or login_at > now + 60
    ):
        session.clear()
        return
    g.user = row


def start_session(user_row) -> None:
    """登录成功：清空旧会话，重新签发（防会话固定）。"""
    session.clear()
    session["uid"] = user_row["uid"]
    session["sv"] = user_row["session_version"]
    session["login_at"] = int(clock())
    session["csrf"] = secrets.token_urlsafe(32)
    session.permanent = True


def is_admin() -> bool:
    return g.user is not None and g.user["role"] == 2

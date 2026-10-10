"""opttype 分派表与统一的检查顺序（REQ-PLATFORM-003、REQ-PLATFORM-004、MIG-RULE-019、DEC-003）。

检查顺序（先命中的为准）：
  1 路径没注册 404（Flask 路由）  2 请求体超过 6 MiB 413（waitress）
  3 /jsp/* 没有有效会话 302 登录页  4 管理端而非管理员 403
  5 opttype 缺失或未知 400        6 方法不对 405
  7 读表单时超过 5 MiB 413        8 CSRF 无效 400
  9 起由业务处理函数负责：参数 400、资源 404、业务 alert。
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from typing import Callable

from flask import Flask, abort, g, redirect, request

from .responses import bad_request
from .security import check_csrf, is_admin

LOGIN_PAGE = "/BookShop/login.jsp"


@dataclass(frozen=True)
class Op:
    method: str


@dataclass(frozen=True)
class Action:
    login: bool
    admin: bool
    ops: dict


@dataclass(frozen=True)
class Page:
    login: bool
    admin: bool


G, P = Op("GET"), Op("POST")
ACTIONS = {
    "/BookShop/login.action": Action(False, False, {"addusers": P, "checkUsers": P}),
    "/BookShop/jsp/book.action": Action(True, False, {"queryAllbook": G, "queryByname": G, "queryBytag": G,
                                                      "bookDetail": G, "buybook": P}),
    "/BookShop/jsp/my.action": Action(True, False, {"initMypage": G, "queryMyorder": G, "updatePwd": P}),
    "/BookShop/jsp/admin.action": Action(True, True, {"queryAllcustomers": G, "queryCustomers": G,
                                                      "queryAllbooks": G, "queryBooks": G, "showBooks": G,
                                                      "showAllmoney": G, "deleteCustomers": P, "addBooks": P,
                                                      "addBooksimg": P, "editBooks": P, "deleteBooks": P}),
}
LOGOUT = "/BookShop/logout.action"

_PUBLIC, _MEMBER, _ADMIN = Page(False, False), Page(True, False), Page(True, True)
PAGES = {
    "/BookShop/": _PUBLIC, "/BookShop/index.jsp": _PUBLIC,
    "/BookShop/login.jsp": _PUBLIC, "/BookShop/register.jsp": _PUBLIC,
    **{f"/BookShop/jsp/{p}": _MEMBER for p in ("buy.jsp", "bookdetails.jsp", "my.jsp", "myorder.jsp", "changepwd.jsp",
                                               "showpic.jsp")},
    **{f"/BookShop/jsp/{p}": _ADMIN for p in ("admin.jsp", "bookadmin.jsp", "add.jsp", "addnext.jsp",
                                              "editbook.jsp", "oderadmin.jsp")},
}

HANDLERS: dict[tuple[str, str], Callable] = {}
PAGE_HANDLERS: dict[str, Callable] = {}


def action(path: str, op: str):
    assert op in ACTIONS[path].ops, (path, op)

    def deco(fn):
        HANDLERS[(path, op)] = fn
        return fn
    return deco


def page(*paths: str):
    def deco(fn):
        for p in paths:
            assert p in PAGES, p
            PAGE_HANDLERS[p] = fn
        return fn
    return deco


def not_implemented():
    abort(501)


def _method() -> str:
    return "GET" if request.method == "HEAD" else request.method


def _gate(login: bool, admin: bool):
    if login and g.user is None:
        return redirect(LOGIN_PAGE)
    if admin and not is_admin():
        abort(403)
    return None


def _dispatch_action(path: str):
    act = ACTIONS[path]
    stop = _gate(act.login, act.admin)
    if stop is not None:
        return stop
    name = request.args.get("opttype", "")
    op = act.ops.get(name)
    if op is None:
        bad_request("opttype")
    if _method() != op.method:
        abort(405)
    if op.method == "POST":
        check_csrf()
    return HANDLERS.get((path, name), not_implemented)()


def _dispatch_page(path: str):
    pg = PAGES[path]
    stop = _gate(pg.login, pg.admin)
    if stop is not None:
        return stop
    if _method() != "GET":
        abort(405)
    return PAGE_HANDLERS.get(path, not_implemented)()


def _dispatch_logout():
    if _method() != "POST":
        abort(405)
    check_csrf()
    from .views.account import logout

    return logout()


def register(app: Flask) -> None:
    for path in ACTIONS:
        app.add_url_rule(path, endpoint=f"action {path}", view_func=partial(_dispatch_action, path),
                         methods=["GET", "POST"])
    for path in PAGES:
        app.add_url_rule(path, endpoint=f"page {path}", view_func=partial(_dispatch_page, path),
                         methods=["GET", "POST"])
    app.add_url_rule(LOGOUT, endpoint="logout", view_func=_dispatch_logout, methods=["GET", "POST"])

"""alert 跳转与错误页（REQ-PLATFORM-005、REQ-PLATFORM-006、MIG-RULE-020、DEC-017）。"""
from __future__ import annotations

import re

from flask import Flask, Response, render_template
from werkzeug.exceptions import BadRequest, HTTPException

# 文案是常量表，响应里不拼接任何用户输入。前 7 条是旧系统原文（含原有拼写）。
ALERTS = {
    "change_uname": "please change uer name!",
    "check_password": "please check password!",
    "fail_try_again": "fail,try again!",
    "username_error": "username or password error!",
    "success": "success!",
    "password_error": "password error!",
    "check_new_password": "check new password!",
    "check_user_or_password": "please check user name or password!",
    "out_of_stock": "out of stock!",
    "check_book_info": "please check book info!",
    "fill_book_first": "please fill in book info first!",
    "upload_image": "please upload a png or jpg image!",
}
_LOCATION = re.compile(r"[A-Za-z0-9_./?=&-]+")


def alert(key: str, location: str) -> Response:
    """旧系统风格的提示：200，响应体是一段 alert 脚本加跳转。"""
    text = ALERTS[key]
    if not _LOCATION.fullmatch(location):
        raise ValueError(f"非法的跳转目标：{location!r}")
    body = f"<script>alert('{text}'); window.location='{location}' </script>"
    return Response(body, status=200, mimetype="text/html")


# 400 的几种原因，错误页上的说明各不相同（测试也据此区分）。
BAD_REQUEST = {
    "opttype": "无效的操作",
    "csrf": "表单令牌无效，请刷新页面后重试",
    "param": "请求参数无效",
}
ERRORS = {
    400: ("请求无效", BAD_REQUEST["param"]),
    403: ("没有权限", "没有权限访问该页面"),
    404: ("页面不存在", "页面不存在"),
    405: ("请求方法不允许", "不支持该请求方法"),
    413: ("请求内容过大", "请求内容过大，文件不能超过 5 MiB"),
    500: ("服务器内部错误", "服务器内部错误，请稍后重试"),
    501: ("功能尚未迁移", "功能尚未迁移"),
}


def bad_request(kind: str) -> None:
    raise BadRequest(description=BAD_REQUEST[kind])


def _render(code: int, message: str | None = None):
    title, default = ERRORS[code]
    html = render_template("error.html", code=code, title=title, message=message or default)
    return html, code


def register_error_handlers(app: Flask) -> None:
    def handle_http(e: HTTPException):
        code = e.code if e.code in ERRORS else 500
        message = e.description if code == 400 and e.description in BAD_REQUEST.values() else None
        return _render(code, message)

    for code in ERRORS:
        if code != 500:
            app.register_error_handler(code, handle_http)

    @app.errorhandler(500)
    def handle_500(e):
        return _render(500)

"""业务视图。导入各模块时，它们通过 dispatch.action / dispatch.page 注册处理函数。"""
from __future__ import annotations

from pathlib import Path

from flask import Flask, abort, send_from_directory

from . import account, admin_books, admin_members, admin_revenue, catalogue, orders, pages  # noqa: F401

STATIC = Path(__file__).resolve().parents[1] / "static"


def register_static(app: Flask) -> None:
    def make(subdir: str):
        def serve(filename: str):
            return send_from_directory(STATIC / subdir, filename)
        return serve

    for url, subdir in (("/BookShop/css", "css"), ("/BookShop/bootstrap", "bootstrap"),
                        ("/BookShop/bootstrap-icons", "bootstrap-icons")):
        app.add_url_rule(f"{url}/<path:filename>", endpoint=f"static {subdir}", view_func=make(subdir))
    app.add_url_rule("/BookShop/img/<name>", endpoint="img", view_func=pages.public_image)

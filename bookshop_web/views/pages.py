"""公开页面：首页、登录、注册，以及公开图片（REQ-PLATFORM-001、REQ-PLATFORM-011）。"""
from __future__ import annotations

from flask import abort, render_template, send_file

from .. import covers
from ..dispatch import page


@page("/BookShop/", "/BookShop/index.jsp")
def index():
    return render_template("index.html")


@page("/BookShop/login.jsp")
def login_page():
    return render_template("login.html")


@page("/BookShop/register.jsp")
def register_page():
    return render_template("register.html")


def public_image(name: str):
    found = covers.find_public(name)
    if found is None:
        abort(404)
    path, mime = found
    return send_file(path, mimetype=mime)

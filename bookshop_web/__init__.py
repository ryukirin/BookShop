"""BookShop：旧 Java Servlet/JSP 网上书店的 Flask 迁移版（openspec change migrate-bookshop-to-flask）。"""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path

from flask import Flask, request

from . import dispatch, money, responses, security
from .config import Config
from .logging_setup import log_request, log_unhandled

PACKAGE_DIR = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_DIR / "static"
APP_MAX_CONTENT = 5 * 1024 * 1024
SESSION_IDLE = timedelta(minutes=30)


class BookshopFlask(Flask):
    def log_exception(self, exc_info):
        # 不用 Flask 默认的带回溯日志：回溯里有 SQL 文本（MIG-RULE-017）。
        log_unhandled(exc_info[0], request.method, request.path)


def create_app(config: Config) -> Flask:
    app = BookshopFlask(__name__, static_folder=None)
    app.config.update(
        SECRET_KEY=config.secret_key,
        SESSION_COOKIE_NAME="session",
        SESSION_COOKIE_PATH="/BookShop",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=SESSION_IDLE,
        SESSION_REFRESH_EACH_REQUEST=True,
        MAX_CONTENT_LENGTH=APP_MAX_CONTENT,
        BOOKSHOP=config,
    )
    app.jinja_env.globals["csrf_token"] = security.ensure_csrf
    app.jinja_env.globals["fmt"] = money.fmt
    app.before_request(security.load_user)
    app.after_request(log_request)

    from . import db, views  # noqa: F401  导入时注册各业务处理函数

    app.teardown_appcontext(db.close_db)
    dispatch.register(app)
    views.register_static(app)
    responses.register_error_handlers(app)
    return app

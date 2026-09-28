"""BookShop 迁移目标的 Flask 应用工厂。"""
import json
import logging
import os
import secrets
import tempfile
import traceback
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask, g, request

from bookshop_app.routes import register_foundation_routes


class SafeFlask(Flask):
    """防止 Flask 默认异常日志写入敏感请求或异常正文。"""

    def log_exception(self, exc_info):
        self.logger.error("内部异常", extra={
            "error_category": type(exc_info[1]).__name__,
            "request_id": getattr(g, "request_id", None),
            "error_frames": [
                {"file": Path(frame.filename).name, "line": frame.lineno, "function": frame.name}
                for frame in traceback.extract_tb(exc_info[2])
            ],
        })


class JsonFormatter(logging.Formatter):
    def format(self, record):
        data = {
            "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "level": record.levelname,
            "event": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
            "error_category": getattr(record, "error_category", None),
            "method": getattr(record, "request_method", None),
            "path": getattr(record, "request_path", None),
            "status": getattr(record, "response_status", None),
            "error_frames": getattr(record, "error_frames", None),
        }
        return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def _absolute_path(value, label, *, directory=False):
    if not value or not isinstance(value, (str, os.PathLike)):
        raise ValueError(label + " 必须配置为绝对路径")
    path = Path(value)
    if not path.is_absolute():
        raise ValueError(label + " 必须配置为绝对路径")
    try:
        if directory:
            path.mkdir(parents=True, exist_ok=True)
            if not path.is_dir():
                raise ValueError(label + " 不是可用目录")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists() and not path.is_file():
                raise ValueError(label + " 不是可用文件路径")
    except OSError as exc:
        raise ValueError(label + " 不可用") from exc
    return path


def _secret_bytes(value):
    if isinstance(value, bytes):
        secret = value
    elif isinstance(value, str):
        try:
            secret = bytes.fromhex(value)
        except ValueError as exc:
            raise ValueError("签名密钥须为安全随机源生成的十六进制字节") from exc
    else:
        raise ValueError("缺少签名密钥")
    if len(secret) < 32 or len(set(secret)) < 8:
        raise ValueError("签名密钥无效或强度不足")
    return secret


def create_app(overrides=None):
    """仅从环境或显式测试注入读取配置；没有默认数据库与秘密。"""
    values = {
        "DATABASE_PATH": os.environ.get("BOOKSHOP_DATABASE_PATH"),
        "UPLOAD_DIR": os.environ.get("BOOKSHOP_UPLOAD_DIR"),
        "SECRET_KEY": os.environ.get("BOOKSHOP_SECRET_KEY"),
        "LOG_PATH": os.environ.get("BOOKSHOP_LOG_PATH"),
    }
    if overrides:
        values.update(overrides)
    secret = _secret_bytes(values.get("SECRET_KEY"))
    database = _absolute_path(values.get("DATABASE_PATH"), "数据库路径")
    uploads = _absolute_path(values.get("UPLOAD_DIR"), "上传目录", directory=True)
    if database == uploads or database in uploads.parents:
        raise ValueError("数据库路径与上传目录不可重叠")
    try:
        with database.open("ab"):
            pass
        with tempfile.TemporaryFile(dir=uploads):
            pass
    except OSError as exc:
        raise ValueError("数据库或上传目录不可写") from exc
    log_path = _absolute_path(values.get("LOG_PATH") or database.parent / "logs" / "bookshop.log",
                              "日志路径")
    app = SafeFlask(__name__, static_folder=None)
    app.config.update(values)
    app.config["DATABASE_PATH"] = str(database)
    app.config["UPLOAD_DIR"] = str(uploads)
    app.config["LOG_PATH"] = str(log_path)
    app.config["SECRET_KEY"] = secret
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_PATH"] = "/BookShop"

    handler = RotatingFileHandler(log_path, maxBytes=1024 * 1024, backupCount=7, encoding="utf-8")
    handler.setFormatter(JsonFormatter())
    for previous in app.logger.handlers[:]:
        app.logger.removeHandler(previous)
        previous.close()
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    app.logger.propagate = False

    @app.before_request
    def begin_request():
        g.request_id = secrets.token_hex(8)

    @app.after_request
    def finish_request(response):
        request_id = getattr(g, "request_id", secrets.token_hex(8))
        response.headers["X-Request-ID"] = request_id
        app.logger.info("请求完成", extra={
            "request_id": request_id,
            "error_category": str(response.status_code) if response.status_code >= 400 else None,
            "request_method": request.method,
            "request_path": request.path,
            "response_status": response.status_code,
        })
        return response

    @app.errorhandler(400)
    def bad_request(_):
        return "请求参数错误", 400

    @app.errorhandler(404)
    def not_found(_):
        return "页面或资源不存在", 404

    @app.errorhandler(405)
    def not_allowed(_):
        return "请求方法不允许", 405

    @app.errorhandler(500)
    def internal_error(_):
        return "服务内部错误", 500

    register_foundation_routes(app)
    return app

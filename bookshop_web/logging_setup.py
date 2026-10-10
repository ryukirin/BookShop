"""日志（REQ-PLATFORM-013、MIG-RULE-017、DEC-018）。

只记录方法、路径（不含查询串）、状态码和异常类型；不记录表单、会话、SQL 和口令。
"""
from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOGGER = logging.getLogger("bookshop")
_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def configure(data_dir: Path) -> None:
    """服务进程启动时调用：写到 stdout 和数据目录下的轮转日志文件。"""
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    if not any(getattr(h, "_bookshop", False) for h in root.handlers):
        log_dir = Path(data_dir) / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        fmt = logging.Formatter(_FORMAT)
        for h in (logging.StreamHandler(sys.stdout),
                  RotatingFileHandler(log_dir / "bookshop.log", maxBytes=5 * 1024 * 1024, backupCount=5,
                                      encoding="utf-8")):
            h.setFormatter(fmt)
            h._bookshop = True
            root.addHandler(h)


def log_request(response):
    from flask import request

    LOGGER.info("%s %s %s", request.method, request.path, response.status_code)
    return response


def log_unhandled(exc_type: type, method: str, path: str) -> None:
    LOGGER.error("unhandled %s at %s %s", exc_type.__name__, method, path)

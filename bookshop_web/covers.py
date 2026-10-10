"""图片和封面的存取（REQ-CATALOG-007、REQ-CATALOG-008、MIG-RULE-009、DEC-021）。"""
from __future__ import annotations

import re
from pathlib import Path

STATIC_IMG = Path(__file__).resolve().parent / "static" / "img"
NAME = re.compile(r"[A-Za-z0-9_-]{1,64}\.(?:jpg|jpeg|png)", re.IGNORECASE)
PNG = b"\x89PNG\r\n\x1a\n"
JPEG = b"\xff\xd8\xff"


def is_valid_name(name: str) -> bool:
    return bool(NAME.fullmatch(name or ""))


def sniff(head: bytes) -> str | None:
    if head.startswith(PNG):
        return "image/png"
    if head.startswith(JPEG):
        return "image/jpeg"
    return None


def _inside(base: Path, name: str) -> Path | None:
    base = base.resolve()
    target = (base / name).resolve()
    if target.parent != base or not target.is_file():
        return None
    return target


def _typed(path: Path | None):
    if path is None:
        return None
    with path.open("rb") as f:
        mime = sniff(f.read(8))
    return (path, mime) if mime else None


def covers_dir() -> Path:
    from flask import current_app

    return Path(current_app.config["BOOKSHOP"].data_dir) / "covers"


def find_cover(name: str):
    """jsp/showpic.jsp?img=<name>：只在数据目录的 covers/ 下找。返回 (路径, MIME) 或 None。"""
    if not is_valid_name(name):
        return None
    return _typed(_inside(covers_dir(), name))


def find_public(name: str):
    """/BookShop/img/<name>：先找静态图片（轮播图、默认头像），再找封面。"""
    if not is_valid_name(name):
        return None
    return _typed(_inside(STATIC_IMG, name)) or _typed(_inside(covers_dir(), name))

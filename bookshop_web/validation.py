"""输入长度与取值范围（REQ-DATA-005、MIG-RULE-018）。长度按 Unicode 字符计。"""
from __future__ import annotations

import re

TEXT_LIMITS = {
    "uname": (1, 20),
    "upwd": (1, 64),
    "bname": (1, 100),
    "publishers": (1, 100),
    "cont": (1, 4000),
    "q_book": (0, 100),    # 书名搜索词
    "q_member": (0, 20),   # 会员搜索词
    "tname": (0, 20),      # 分类筛选参数
}
_STOCK = re.compile(r"0|[1-9][0-9]{0,5}")
_ID = re.compile(r"[1-9][0-9]{0,17}")


def text(kind: str, value: str | None) -> str | None:
    lo, hi = TEXT_LIMITS[kind]
    if value is None or "\x00" in value or not lo <= len(value) <= hi:
        return None
    return value


def stock(value: str | None) -> int | None:
    return int(value) if value is not None and _STOCK.fullmatch(value) else None


def positive_id(value: str | None) -> int | None:
    return int(value) if value is not None and _ID.fullmatch(value) else None

"""金额：存整数分，显示两位小数（REQ-DATA-004、MIG-RULE-007、DEC-008）。"""
from __future__ import annotations

import re
from decimal import Decimal

MAX_CENTS = 9_999_999  # 99999.99
_PRICE = re.compile(r"(0|[1-9][0-9]{0,4})(\.[0-9]{1,2})?")


def parse_price(text: str | None) -> int | None:
    """把 0～99999.99、最多两位小数的十进制串转成整数分；不合规返回 None。"""
    if text is None or not _PRICE.fullmatch(text):
        return None
    cents = int(Decimal(text) * 100)
    return cents if 0 <= cents <= MAX_CENTS else None


def fmt(cents: int) -> str:
    return f"{cents // 100}.{cents % 100:02d}"

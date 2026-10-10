"""TEST-017（转写核对）：seed_data.py 与 BookShop/db/seed.sql 一致（REQ-DATA-003、DEC-010）。

只核对“转写没有出错”，这些值本身是演示占位（MIG-RULE-015）。
"""
import hashlib
import re
from decimal import Decimal
from pathlib import Path

import pytest

pytestmark = pytest.mark.batch(2)
ROOT = Path(__file__).resolve().parents[2]
VALUE = re.compile(r"'((?:[^']|'')*)'|(-?\d+(?:\.\d+)?)")


def rows(sql: str, table: str):
    block = re.search(rf"INSERT INTO `{table}` \([^)]*\) VALUES\s*(.*?);", sql, re.S).group(1)
    out = []
    for line in re.findall(r"^\s*\((.*)\)[,;]?\s*(?:--.*)?$", block, re.M):
        out.append([s.replace("''", "'") if s or n == "" else (Decimal(n) if "." in n else int(n))
                    for s, n in VALUE.findall(line)])
    return out


@pytest.fixture(scope="module")
def sql():
    return (ROOT / "BookShop" / "db" / "seed.sql").read_text(encoding="utf-8")


def test_tags(sql):
    from bookshop_web.seed.seed_data import TAGS

    assert [tuple(r) for r in rows(sql, "tag")] == TAGS


def test_books(sql):
    from bookshop_web.seed.seed_data import BOOKS

    expected = [(bid, bname, pub, stock, int(price * 100), tid, url, cont)
                for bid, bname, pub, stock, price, tid, url, cont in rows(sql, "book")]
    assert BOOKS == expected
    assert len(BOOKS) == 10


def test_cover_files_identical_to_legacy():
    src = ROOT / "bookshop_web" / "seed" / "covers"
    for p in src.iterdir():
        legacy = ROOT / "BookShop" / "WebContent" / "img" / p.name
        assert hashlib.sha256(p.read_bytes()).digest() == hashlib.sha256(legacy.read_bytes()).digest(), p.name


def test_placeholder_notice():
    text = (ROOT / "bookshop_web" / "seed" / "seed_data.py").read_text(encoding="utf-8")
    assert "占位" in text and "不是原书店的数据" in text

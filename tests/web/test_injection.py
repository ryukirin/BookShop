"""TEST-010（页面部分）：注入载荷只被当作字面值（REQ-PLATFORM-009、MIG-RULE-002、LEGACY-048）。"""
from urllib.parse import quote

import pytest

from tests.conftest import alert_of, db, login, parse, register

BOOK = "/BookShop/jsp/book.action"


def details(client):
    return [t for a, t in parse(client.get("/BookShop/jsp/buy.jsp")).links if t == "查看详情 »"]


@pytest.mark.batch(4)
def test_search_union_injection(member_client):
    r = member_client.get(f"{BOOK}?opttype=queryByname&bname=" + quote("x' UNION SELECT upwd FROM user --"))
    assert r.status_code == 302
    body = member_client.get("/BookShop/jsp/buy.jsp").get_data(as_text=True)
    assert "scrypt:" not in body and details(member_client) == []


@pytest.mark.batch(4)
def test_tag_or_injection(member_client):
    member_client.get(f"{BOOK}?opttype=queryBytag&tname=" + quote("散文"))
    assert len(details(member_client)) == 3
    member_client.get(f"{BOOK}?opttype=queryBytag&tname=" + quote("' OR '1'='1"))
    assert details(member_client) == []


@pytest.mark.batch(4)
def test_bid_injection_rejected(member_client):
    assert member_client.get(f"{BOOK}?opttype=bookDetail&bid=" + quote("1 OR 1=1")).status_code == 400


# 登录和注册在 BATCH-003 已实现。
def test_register_name_is_literal(seeded_app):
    c = seeded_app.test_client()
    assert register(c, "x');--", "abc123").status_code == 302
    conn = db(seeded_app.config["BOOKSHOP"].data_dir)
    assert conn.execute("SELECT COUNT(*) FROM user").fetchone()[0] == 2
    assert conn.execute("SELECT uname FROM user WHERE uname = ?", ("x');--",)).fetchone()[0] == "x');--"
    conn.close()
    assert login(seeded_app.test_client(), "x');--", "abc123").status_code == 302


# 登录和注册在 BATCH-003 已实现。
def test_login_injection(seeded_app):
    assert alert_of(login(seeded_app.test_client(), "' OR '1'='1' --", "x")) == ("username or password error!", "login.jsp")

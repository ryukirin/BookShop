"""TEST-005：UTF-8 编码（REQ-PLATFORM-002、LEGACY-002、LEGACY-063）。"""
import pytest

from tests.conftest import login, parse, register, resolve


@pytest.mark.parametrize("url", ["/BookShop/login.jsp", "/BookShop/register.jsp", "/BookShop/index.jsp"])
def test_charset(client, url):
    r = client.get(url)
    assert r.headers["Content-Type"] == "text/html; charset=utf-8"
    body = r.get_data()
    assert b'<meta charset="utf-8">' in body
    assert "网上书店" in body.decode("utf-8") or "登录" in body.decode("utf-8") or "注册" in body.decode("utf-8")


@pytest.mark.batch(3)
def test_post_chinese_roundtrip(seeded_app):
    c = seeded_app.test_client()
    assert register(c, "张三", "abc123").status_code == 302
    assert login(c, "张三", "abc123").status_code == 302
    r = c.get("/BookShop/jsp/my.action?opttype=initMypage")
    doc = parse(c.get(resolve("/BookShop/jsp/my.action", r.headers["Location"])))
    assert "张三" in doc.headings.get("h4", [])


@pytest.mark.batch(4)
def test_chinese_query_param(member_client):
    r = member_client.get("/BookShop/jsp/book.action?opttype=queryBytag&tname=%E6%95%A3%E6%96%87")
    assert r.status_code == 302
    doc = parse(member_client.get("/BookShop/jsp/buy.jsp"))
    names = doc.headings.get("h4", [])
    assert names == ["清欢", "林泉", "玄想"]

"""TEST-032：我的订单（REQ-ORDER-003、LEGACY-021、LEGACY-042）。"""
import pytest

from tests.conftest import db, login, make_member, parse, post

pytestmark = pytest.mark.batch(5)
BUY = "/BookShop/jsp/book.action?opttype=buybook"


def my_orders(client):
    r = client.get("/BookShop/jsp/my.action?opttype=queryMyorder")
    assert r.status_code == 302 and r.headers["Location"] == "myorder.jsp"
    doc = parse(client.get("/BookShop/jsp/myorder.jsp"))
    return doc.table_headers, doc.table_rows


def test_rows_snapshot_and_offshelf(member_client):
    post(member_client, BUY, {"bid": "9"})
    post(member_client, BUY, {"bid": "1"})
    c = db(member_client.application.config["BOOKSHOP"].data_dir)
    c.execute("UPDATE book SET on_sale = 0, price_cents = 1 WHERE bid = 1")
    c.execute("UPDATE book SET price_cents = 9900 WHERE bid = 9")
    headers, rows = my_orders(member_client)
    assert headers == [["用户名", "书名", "订单金额"]]
    assert rows == [["zhangsan", "月亮和六便士", "39.80"], ["zhangsan", "你一生的故事", "39.50"]]


def test_only_own_orders(seeded_app, member_client):
    make_member(seeded_app, "lisi", "abc123")
    other = seeded_app.test_client()
    login(other, "lisi", "abc123")
    post(other, BUY, {"bid": "3"})
    post(member_client, BUY, {"bid": "9"})
    _, rows = my_orders(member_client)
    assert rows == [["zhangsan", "月亮和六便士", "39.80"]]


def test_empty(member_client):
    headers, rows = my_orders(member_client)
    assert headers == [["用户名", "书名", "订单金额"]] and rows == []


def test_reopen_shows_current(member_client):
    member_client.get("/BookShop/jsp/my.action?opttype=queryMyorder")
    post(member_client, BUY, {"bid": "9"})
    assert parse(member_client.get("/BookShop/jsp/myorder.jsp")).table_rows == [["zhangsan", "月亮和六便士", "39.80"]]

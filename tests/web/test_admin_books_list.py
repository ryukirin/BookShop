"""TEST-035：书籍列表与搜索（REQ-BOOK-001、REQ-BOOK-002、LEGACY-024、LEGACY-025、LEGACY-046）。"""
import pytest

from tests.conftest import db, parse

pytestmark = pytest.mark.batch(7)
ADMIN = "/BookShop/jsp/admin.action"


def table(client, query):
    r = client.get(f"{ADMIN}?{query}")
    assert r.status_code == 302 and r.headers["Location"] == "bookadmin.jsp"
    doc = parse(client.get("/BookShop/jsp/bookadmin.jsp"))
    return doc, doc.table_rows


def test_list(admin_client):
    c = db(admin_client.application.config["BOOKSHOP"].data_dir)
    c.execute("INSERT INTO orders (bid, uid, unit_price_cents) VALUES (9, 1, 3980), (9, 1, 3980)")
    c.execute("UPDATE book SET on_sale = 0 WHERE bid = 2")
    c.close()
    doc, rows = table(admin_client, "opttype=queryAllbooks")
    assert [r[0] for r in rows] == ["1", "3", "4", "5", "6", "7", "8", "9", "11"]
    assert rows[0][:8] == ["1", "你一生的故事", "[美]特德·姜 著。科幻小说集。", "译林出版社", "小说", "100", "39.50", "0"]
    assert rows[7][:8] == ["9", "月亮和六便士", "[英]毛姆 著。长篇小说。", "晨光出版社", "小说", "100", "39.80", "2"]
    forms = [f for f in doc.forms if "deleteBooks" in (f.action or "")]
    assert len(forms) == 9 and forms[0].hidden()["bid"] == "1" and forms[0].method == "post"


def test_search(admin_client):
    _, rows = table(admin_client, "opttype=queryBooks&bname=%E7%8E%84")
    assert [r[0] for r in rows] == ["8"]
    with admin_client.session_transaction("/BookShop/") as s:
        assert s["q_admin_books"] == {"op": "name", "q": "玄"}


def test_search_too_long(admin_client):
    assert admin_client.get(f"{ADMIN}?opttype=queryBooks&bname=" + "a" * 101).status_code == 400


def test_reopen_without_query(admin_client):
    r = admin_client.get("/BookShop/jsp/bookadmin.jsp")
    assert r.status_code == 200 and parse(r).table_rows == []

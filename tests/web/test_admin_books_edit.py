"""TEST-037：修改书籍（REQ-BOOK-005、LEGACY-028、DEC-016）。"""
import pytest

from tests.conftest import alert_of, db, parse, post

pytestmark = pytest.mark.batch(7)
ADMIN = "/BookShop/jsp/admin.action"
EDIT = f"{ADMIN}?opttype=editBooks"


def conn_of(client):
    return db(client.application.config["BOOKSHOP"].data_dir)


def test_show_and_form(admin_client):
    r = admin_client.get(f"{ADMIN}?opttype=showBooks&bid=9")
    assert r.status_code == 302 and r.headers["Location"] == "editbook.jsp"
    with admin_client.session_transaction("/BookShop/") as s:
        assert s["edit_bid"] == 9
    f = parse(admin_client.get("/BookShop/jsp/editbook.jsp")).form(name="addbook")
    assert f.input("bid")["value"] == "9" and "readonly" in f.input("bid")
    assert (f.input("publishers")["value"], f.input("stock")["value"], f.input("price")["value"]) == ("晨光出版社", "100", "39.80")


def test_edit_success_keeps_order_snapshot(admin_client):
    c = conn_of(admin_client)
    c.execute("INSERT INTO orders (bid, uid, unit_price_cents) VALUES (9, 1, 3980)")
    r = post(admin_client, EDIT, {"bid": "9", "publishers": "新出版社", "stock": "50", "price": "45.00"})
    assert r.status_code == 302 and r.headers["Location"] == "admin.action?opttype=queryAllbooks"
    row = c.execute("SELECT publishers, stock, price_cents, bname FROM book WHERE bid = 9").fetchone()
    assert tuple(row) == ("新出版社", 50, 4500, "月亮和六便士")
    assert c.execute("SELECT unit_price_cents FROM orders").fetchone()[0] == 3980


@pytest.mark.parametrize("field,value", [("stock", "-1"), ("price", "25.555"), ("publishers", ""), ("stock", "abc")])
def test_edit_invalid(admin_client, field, value):
    data = dict({"bid": "9", "publishers": "x", "stock": "1", "price": "1.00"}, **{field: value})
    assert alert_of(post(admin_client, EDIT, data)) == ("please check book info!", "admin.action?opttype=showBooks&bid=9")
    assert tuple(conn_of(admin_client).execute("SELECT publishers, stock, price_cents FROM book WHERE bid = 9").fetchone()) \
        == ("晨光出版社", 100, 3980)


@pytest.mark.parametrize("bid,status", [("999", 404), ("abc", 400), ("0", 400)])
def test_edit_bad_bid(admin_client, bid, status):
    assert admin_client.get(f"{ADMIN}?opttype=showBooks&bid={bid}").status_code == status
    assert post(admin_client, EDIT, {"bid": bid, "publishers": "x", "stock": "1", "price": "1.00"}).status_code == status


def test_offshelf_404_before_validation(admin_client):
    conn_of(admin_client).execute("UPDATE book SET on_sale = 0 WHERE bid = 2")
    assert admin_client.get(f"{ADMIN}?opttype=showBooks&bid=2").status_code == 404
    assert post(admin_client, EDIT, {"bid": "2", "publishers": "", "stock": "-1", "price": "x"}).status_code == 404

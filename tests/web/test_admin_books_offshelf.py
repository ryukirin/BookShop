"""TEST-038：下架书籍（REQ-BOOK-006、LEGACY-029、LEGACY-043、MIG-RULE-008）。"""
import pytest

from tests.conftest import db, parse, post

pytestmark = pytest.mark.batch(7)
ADMIN = "/BookShop/jsp/admin.action"
OFF = f"{ADMIN}?opttype=deleteBooks"


def test_offshelf_keeps_history(admin_client, member_client):
    assert post(member_client, "/BookShop/jsp/book.action?opttype=buybook", {"bid": "1"}).status_code == 302
    r = post(admin_client, OFF, {"bid": "1"})
    assert r.status_code == 302 and r.headers["Location"] == "admin.action?opttype=queryAllbooks"
    data_dir = admin_client.application.config["BOOKSHOP"].data_dir
    c = db(data_dir)
    assert c.execute("SELECT on_sale FROM book WHERE bid = 1").fetchone()[0] == 0
    assert c.execute("SELECT COUNT(*) FROM orders WHERE bid = 1").fetchone()[0] == 1
    assert (data_dir / "covers" / "b1.jpg").is_file()
    admin_client.get(f"{ADMIN}?opttype=queryAllbooks")
    assert "1" not in [r[0] for r in parse(admin_client.get("/BookShop/jsp/bookadmin.jsp")).table_rows]
    member_client.get("/BookShop/jsp/book.action?opttype=queryAllbook")
    assert "你一生的故事" not in parse(member_client.get("/BookShop/jsp/buy.jsp")).headings.get("h4", [])
    assert member_client.get("/BookShop/jsp/book.action?opttype=bookDetail&bid=1").status_code == 404
    assert post(member_client, "/BookShop/jsp/book.action?opttype=buybook", {"bid": "1"}).status_code == 404
    admin_client.get(f"{ADMIN}?opttype=showAllmoney")
    assert any(row[2] == "你一生的故事" for row in parse(admin_client.get("/BookShop/jsp/oderadmin.jsp")).table_rows)
    member_client.get("/BookShop/jsp/my.action?opttype=queryMyorder")
    assert parse(member_client.get("/BookShop/jsp/myorder.jsp")).table_rows == [["zhangsan", "你一生的故事", "39.50"]]


def test_repeat_offshelf_404(admin_client):
    assert post(admin_client, OFF, {"bid": "1"}).status_code == 302
    assert post(admin_client, OFF, {"bid": "1"}).status_code == 404


@pytest.mark.parametrize("bid,status", [("999", 404), ("abc", 400), ("", 400)])
def test_bad_bid(admin_client, bid, status):
    assert post(admin_client, OFF, {"bid": bid}).status_code == status

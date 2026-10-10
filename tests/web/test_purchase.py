"""TEST-030：购买（REQ-ORDER-001、REQ-ORDER-002、LEGACY-019、LEGACY-020、LEGACY-040、LEGACY-041、LEGACY-042、EXP-003）。"""
import pytest

from tests.conftest import alert_of, db, post

pytestmark = pytest.mark.batch(5)
BUY = "/BookShop/jsp/book.action?opttype=buybook"


def conn_of(client):
    return db(client.application.config["BOOKSHOP"].data_dir)


def uid_of(conn, uname):
    return conn.execute("SELECT uid FROM user WHERE uname = ?", (uname,)).fetchone()[0]


def test_success(member_client):
    r = post(member_client, BUY, {"bid": "9"})
    assert r.status_code == 302 and r.headers["Location"] == "my.action?opttype=queryMyorder"
    c = conn_of(member_client)
    assert c.execute("SELECT stock FROM book WHERE bid = 9").fetchone()[0] == 99
    rows = [tuple(x) for x in c.execute("SELECT bid, uid, unit_price_cents FROM orders")]
    assert rows == [(9, uid_of(c, "zhangsan"), 3980)]


def test_out_of_stock(member_client):
    c = conn_of(member_client)
    c.execute("UPDATE book SET stock = 0 WHERE bid = 9")
    assert alert_of(post(member_client, BUY, {"bid": "9"})) == ("out of stock!", "book.action?opttype=bookDetail&bid=9")
    assert c.execute("SELECT stock FROM book WHERE bid = 9").fetchone()[0] == 0
    assert c.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0


def test_last_copy_then_out(member_client):
    c = conn_of(member_client)
    c.execute("UPDATE book SET stock = 1 WHERE bid = 9")
    assert post(member_client, BUY, {"bid": "9"}).status_code == 302
    assert alert_of(post(member_client, BUY, {"bid": "9"}))[0] == "out of stock!"
    assert c.execute("SELECT stock FROM book WHERE bid = 9").fetchone()[0] == 0


@pytest.mark.parametrize("bid,status", [("999", 404), ("abc", 400), ("", 400), ("0", 400), ("-1", 400)])
def test_bad_bid(member_client, bid, status):
    assert post(member_client, BUY, {"bid": bid}).status_code == status
    assert conn_of(member_client).execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0


def test_offshelf_404(member_client):
    c = conn_of(member_client)
    c.execute("UPDATE book SET on_sale = 0 WHERE bid = 2")
    assert post(member_client, BUY, {"bid": "2"}).status_code == 404
    assert c.execute("SELECT stock FROM book WHERE bid = 2").fetchone()[0] == 100


def test_price_snapshot(member_client):
    post(member_client, BUY, {"bid": "9"})
    c = conn_of(member_client)
    c.execute("UPDATE book SET price_cents = 9900 WHERE bid = 9")
    assert c.execute("SELECT unit_price_cents FROM orders").fetchone()[0] == 3980


def test_get_is_405(member_client):
    assert member_client.get(BUY + "&bid=9").status_code == 405
    c = conn_of(member_client)
    assert c.execute("SELECT stock FROM book WHERE bid = 9").fetchone()[0] == 100
    assert post(member_client, BUY, {"bid": "9"}).status_code == 302
    assert c.execute("SELECT stock FROM book WHERE bid = 9").fetchone()[0] == 99


def test_admin_can_buy(admin_client):
    assert post(admin_client, BUY, {"bid": "1"}).status_code == 302

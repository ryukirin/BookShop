"""TEST-009（页面部分）：输出转义（REQ-PLATFORM-008、MIG-RULE-005、LEGACY-052、EXP-005）。"""
import pytest

from tests.conftest import db, login, make_member, register

XSS_NAME = "<script>alert(1)</script>"
XSS_CONT = "<img src=x onerror=alert(2)>"
XSS_PUB = "<b>pub</b>"


@pytest.fixture
def xss_book(member_client):
    c = db(member_client.application.config["BOOKSHOP"].data_dir)
    c.execute("INSERT INTO book (bname, publishers, stock, price_cents, tid, url, cont) VALUES (?, ?, 1, 1, 1, 'b1.jpg', ?)",
              (XSS_NAME, XSS_PUB, XSS_CONT))
    c.close()
    return member_client


@pytest.mark.batch(4)
def test_buy_page_escaped(xss_book):
    xss_book.get("/BookShop/jsp/book.action?opttype=queryAllbook")
    body = xss_book.get("/BookShop/jsp/buy.jsp").get_data(as_text=True)
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in body and XSS_NAME not in body
    assert "&lt;img src=x onerror=alert(2)&gt;" in body and XSS_CONT not in body


@pytest.mark.batch(4)
def test_detail_page_escaped(xss_book):
    xss_book.get("/BookShop/jsp/book.action?opttype=bookDetail&bid=12")
    body = xss_book.get("/BookShop/jsp/bookdetails.jsp").get_data(as_text=True)
    assert XSS_NAME not in body and XSS_CONT not in body and XSS_PUB not in body
    assert "&lt;b&gt;pub&lt;/b&gt;" in body


@pytest.mark.batch(6)
def test_member_name_escaped_in_admin(seeded_app, admin_client):
    c = seeded_app.test_client()
    assert register(c, "<b>x</b>", "abc123").status_code == 302
    admin_client.get("/BookShop/jsp/admin.action?opttype=queryAllcustomers")
    body = admin_client.get("/BookShop/jsp/admin.jsp").get_data(as_text=True)
    assert "&lt;b&gt;x&lt;/b&gt;" in body and "<b>x</b>" not in body

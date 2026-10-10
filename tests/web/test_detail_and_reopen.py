"""TEST-028：详情页与直接打开结果页（REQ-CATALOG-005、REQ-CATALOG-006、LEGACY-017、LEGACY-032、DEC-016）。"""
import pytest

from tests.conftest import db, parse

pytestmark = pytest.mark.batch(4)
BOOK = "/BookShop/jsp/book.action"


def conn_of(client):
    return db(client.application.config["BOOKSHOP"].data_dir)


def test_detail_fields(member_client):
    r = member_client.get(f"{BOOK}?opttype=bookDetail&bid=9")
    assert r.status_code == 302 and r.headers["Location"] == "bookdetails.jsp"
    doc = parse(member_client.get("/BookShop/jsp/bookdetails.jsp"))
    h4 = doc.headings["h4"]
    assert h4 == ["书名：月亮和六便士", "出版商：晨光出版社", "价格：39.80", "库存：100", "简介：[英]毛姆 著。长篇小说。", "销量：0"]
    assert [i["src"] for i in doc.imgs if "showpic" in i["src"]] == ["showpic.jsp?img=b9.jpg"]


def test_detail_sales_count(member_client):
    c = conn_of(member_client)
    c.execute("INSERT INTO orders (bid, uid, unit_price_cents) VALUES (9, 1, 3980)")
    c.close()
    member_client.get(f"{BOOK}?opttype=bookDetail&bid=9")
    assert "销量：1" in parse(member_client.get("/BookShop/jsp/bookdetails.jsp")).headings["h4"]


@pytest.mark.parametrize("bid,status", [("999", 404), ("abc", 400), ("0", 400)])
def test_detail_errors(member_client, bid, status):
    assert member_client.get(f"{BOOK}?opttype=bookDetail&bid={bid}").status_code == status


def test_detail_offshelf_404(member_client):
    c = conn_of(member_client)
    c.execute("UPDATE book SET on_sale = 0 WHERE bid = 2")
    c.close()
    assert member_client.get(f"{BOOK}?opttype=bookDetail&bid=2").status_code == 404


def test_reopen_buy_requeries(member_client):
    c = conn_of(member_client)
    c.execute("INSERT INTO book (bname, publishers, stock, price_cents, tid, url, cont) VALUES ('清欢', 'x', 1, 1, 2, 'b6.jpg', 'x')")
    member_client.get(f"{BOOK}?opttype=queryByname&bname=%E6%B8%85%E6%AC%A2")
    assert len([t for a, t in parse(member_client.get("/BookShop/jsp/buy.jsp")).links if t == "查看详情 »"]) == 2
    c.execute("UPDATE book SET on_sale = 0 WHERE bid = 6")
    c.close()
    links = [a["href"] for a, t in parse(member_client.get("/BookShop/jsp/buy.jsp")).links if t == "查看详情 »"]
    assert links == ["book.action?opttype=bookDetail&bid=12"]


def test_reopen_without_query_empty(member_client):
    r = member_client.get("/BookShop/jsp/buy.jsp")
    assert r.status_code == 200
    assert not [t for a, t in parse(r).links if t == "查看详情 »"]


def test_reopen_detail(member_client):
    r = member_client.get("/BookShop/jsp/bookdetails.jsp")
    assert r.status_code == 200 and "书名：" not in r.get_data(as_text=True)
    member_client.get(f"{BOOK}?opttype=bookDetail&bid=9")
    c = conn_of(member_client)
    c.execute("UPDATE book SET stock = 42 WHERE bid = 9")
    assert "库存：42" in parse(member_client.get("/BookShop/jsp/bookdetails.jsp")).headings["h4"]
    c.execute("UPDATE book SET on_sale = 0 WHERE bid = 9")
    c.close()
    assert member_client.get("/BookShop/jsp/bookdetails.jsp").status_code == 404


def test_detail_bid_in_session(member_client):
    member_client.get(f"{BOOK}?opttype=bookDetail&bid=9")
    with member_client.session_transaction("/BookShop/") as s:
        assert s["detail_bid"] == 9

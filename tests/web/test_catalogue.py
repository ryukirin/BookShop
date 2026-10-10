"""TEST-027：书目、购买页、筛选、搜索（REQ-CATALOG-001～REQ-CATALOG-004、LEGACY-013～LEGACY-016、LEGACY-046、EXP-003）。"""
import pytest

from tests.conftest import db, parse, resolve

pytestmark = pytest.mark.batch(4)
BOOK = "/BookShop/jsp/book.action"
ALL_BIDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11]


def conn_of(client):
    return db(client.application.config["BOOKSHOP"].data_dir)


def listed(client, query):
    r = client.get(f"{BOOK}?{query}")
    assert r.status_code == 302 and r.headers["Location"] == "buy.jsp", (r.status_code, r.headers.get("Location"))
    doc = parse(client.get("/BookShop/jsp/buy.jsp"))
    return [int(h.rsplit("=", 1)[1]) for t, h in
            [(t, resolve("/BookShop/jsp/buy.jsp", a["href"])) for a, t in doc.links] if t == "查看详情 »"]


def add_orders(client, *bids):
    c = conn_of(client)
    for bid in bids:
        c.execute("INSERT INTO orders (bid, uid, unit_price_cents) VALUES (?, 1, 100)", (bid,))
    c.close()


def test_order_by_sales_then_bid(member_client):
    add_orders(member_client, 9, 9, 1)
    assert listed(member_client, "opttype=queryAllbook") == [9, 1, 2, 3, 4, 5, 6, 7, 8, 11]


def test_same_name_listed_separately(member_client):
    c = conn_of(member_client)
    c.execute("INSERT INTO book (bname, publishers, stock, price_cents, tid, url, cont) VALUES ('清欢', '另一出版社', 5, 3000, 2, 'b7.jpg', '同名书')")
    c.close()
    assert listed(member_client, "opttype=queryAllbook").count(6) == 1
    assert 12 in listed(member_client, "opttype=queryAllbook")
    assert listed(member_client, "opttype=queryByname&bname=%E6%B8%85%E6%AC%A2") == [6, 12]


def test_offshelf_hidden_everywhere(member_client):
    c = conn_of(member_client)
    c.execute("UPDATE book SET on_sale = 0 WHERE bid = 6")
    c.close()
    assert 6 not in listed(member_client, "opttype=queryAllbook")
    assert listed(member_client, "opttype=queryBytag&tname=%E6%95%A3%E6%96%87") == [7, 8]
    assert listed(member_client, "opttype=queryByname&bname=%E6%B8%85%E6%AC%A2") == []


def test_tag_filter(member_client):
    assert listed(member_client, "opttype=queryBytag&tname=%E8%AF%97%E6%AD%8C") == [3, 4]
    assert listed(member_client, "opttype=queryBytag&tname=nope") == []


def test_tag_filter_ascii_case_insensitive(member_client):
    c = conn_of(member_client)
    c.execute("INSERT INTO tag (tid, tname) VALUES (10, 'Poetry')")
    c.execute("INSERT INTO book (bname, publishers, stock, price_cents, tid, url, cont) VALUES ('Leaves', 'P', 1, 1, 10, 'b1.jpg', 'x')")
    c.close()
    assert listed(member_client, "opttype=queryBytag&tname=poetry") == [12]


@pytest.mark.parametrize("q,expected", [("%E5%85%AD%E4%BE%BF%E5%A3%AB", [9]), ("python", [12]), ("PYTHON", [12]),
                                        ("%25", ALL_BIDS + [12]), ("", ALL_BIDS + [12]), ("_", ALL_BIDS + [12]),
                                        ("nope", [])])
def test_name_search(member_client, q, expected):
    c = conn_of(member_client)
    c.execute("INSERT INTO book (bname, publishers, stock, price_cents, tid, url, cont) VALUES ('Python入门', 'P', 1, 1, 1, 'b1.jpg', 'x')")
    c.close()
    assert sorted(listed(member_client, f"opttype=queryByname&bname={q}")) == sorted(expected)


def test_tags_sidebar_in_tid_order(member_client):
    member_client.get(f"{BOOK}?opttype=queryAllbook")
    doc = parse(member_client.get("/BookShop/jsp/buy.jsp"))
    tags = [t for a, t in doc.links if "queryBytag" in a.get("href", "")]
    assert tags == ["小说", "散文", "诗歌"]


def test_criteria_stored_not_results(member_client):
    member_client.get(f"{BOOK}?opttype=queryByname&bname=%E5%85%AD")
    with member_client.session_transaction("/BookShop/") as s:
        assert s["q_catalogue"] == {"op": "name", "q": "六"}


def test_no_price_on_buy_page(member_client):
    assert len(listed(member_client, "opttype=queryAllbook")) == 10
    text = parse(member_client.get("/BookShop/jsp/buy.jsp")).text
    assert "39.80" not in text and "价格" not in text

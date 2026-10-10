"""TEST-039：账目统计（REQ-REVENUE-001、LEGACY-031、LEGACY-042、LEGACY-045、EXP-003）。"""
import pytest

from tests.conftest import db, make_member, parse

pytestmark = pytest.mark.batch(6)


def revenue(client):
    r = client.get("/BookShop/jsp/admin.action?opttype=showAllmoney")
    assert r.status_code == 302 and r.headers["Location"] == "oderadmin.jsp"
    doc = parse(client.get("/BookShop/jsp/oderadmin.jsp"))
    return doc.table_headers, doc.table_rows


def test_exact_total_with_soft_deleted(seeded_app, admin_client):
    make_member(seeded_app, "zhangsan", "abc123")
    make_member(seeded_app, "lisi", "abc123")
    c = db(seeded_app.config["BOOKSHOP"].data_dir)
    z = c.execute("SELECT uid FROM user WHERE uname = 'zhangsan'").fetchone()[0]
    l = c.execute("SELECT uid FROM user WHERE uname = 'lisi'").fetchone()[0]
    c.execute("INSERT INTO orders (bid, uid, unit_price_cents) VALUES (1, ?, 10), (2, ?, 20), (9, ?, 3980)", (z, l, z))
    c.execute("UPDATE book SET on_sale = 0 WHERE bid = 1")
    c.execute("UPDATE user SET active = 0 WHERE uid = ?", (l,))
    c.execute("UPDATE book SET price_cents = 9900 WHERE bid = 9")
    c.close()
    headers, rows = revenue(admin_client)
    assert headers == [["订单id", "用户名", "书名", "订单金额"]]
    assert rows[:3] == [["1", "zhangsan", "你一生的故事", "0.10"], ["2", "lisi", "盛夏的方程式", "0.20"],
                        ["3", "zhangsan", "月亮和六便士", "39.80"]]
    assert rows[3][0] == "总金额：40.10元"


def test_empty_total(admin_client):
    headers, rows = revenue(admin_client)
    assert rows == [["总金额：0.00元", "", "", ""]]

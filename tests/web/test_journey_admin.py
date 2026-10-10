"""TEST-041：管理端端到端旅程（REQ-MEMBER-001～REQ-MEMBER-003、REQ-BOOK-001～REQ-BOOK-006、REQ-REVENUE-001）。"""
import io

from tests.conftest import ADMIN_PASSWORD, login, make_member, post
from tests.web.journey import Browser

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


def test_admin_journey(seeded_app):
    make_member(seeded_app, "zhangsan", "abc123")
    shopper = seeded_app.test_client()
    login(shopper, "zhangsan", "abc123")
    assert post(shopper, "/BookShop/jsp/book.action?opttype=buybook", {"bid": "9"}).status_code == 302

    b = Browser(seeded_app.test_client())
    b.open("/BookShop/login.jsp")
    b.submit(b.form(name="signin"), {"inputName": "admin", "inputPassword": ADMIN_PASSWORD})
    assert b.path == "/BookShop/jsp/admin.jsp"
    assert [r[1] for r in b.doc.table_rows] == ["zhangsan"]

    # 会员搜索与停用
    b.submit(b.form(action_contains="admin.action"), {"uname": "ZHANGSAN"})
    assert [r[1] for r in b.doc.table_rows] == ["zhangsan"]
    b.submit(b.form(action_contains="deleteCustomers"))
    assert b.path == "/BookShop/jsp/admin.jsp" and b.doc.table_rows == []

    # 书籍：搜索、两步新增、修改、下架
    b.click("书籍管理")
    assert b.path == "/BookShop/jsp/bookadmin.jsp" and len(b.doc.table_rows) == 10
    b.submit(b.form(action_contains="admin.action"), {"bname": "玄"})
    assert [r[1] for r in b.doc.table_rows] == ["玄想"]
    b.click("添加")
    assert b.path == "/BookShop/jsp/add.jsp"
    b.submit(b.form(name="addbook"), {"bname": "旅程测试书", "publishers": "测试社", "cont": "简介", "stock": "3", "price": "12.30"})
    assert b.path == "/BookShop/jsp/addnext.jsp"
    b.submit(b.form(action_contains="addBooksimg"), files={"file": (io.BytesIO(PNG), "cover.png")})
    assert b.path == "/BookShop/jsp/bookadmin.jsp"
    new_row = [r for r in b.doc.table_rows if r[1] == "旅程测试书"]
    assert new_row and new_row[0][:8] == ["12", "旅程测试书", "简介", "测试社", "小说", "3", "12.30", "0"]

    b.open("/BookShop/jsp/admin.action?opttype=queryAllbooks")
    b.click("修改", index=[r[0] for r in b.doc.table_rows].index("12"))
    assert b.path == "/BookShop/jsp/editbook.jsp"
    b.submit(b.form(name="addbook"), {"price": "15.00", "stock": "4"})
    assert [r[5:7] for r in b.doc.table_rows if r[0] == "12"] == [["4", "15.00"]]
    forms = [f for f in b.doc.forms if "deleteBooks" in (f.action or "")]
    b.submit([f for f in forms if f.hidden()["bid"] == "12"][0])
    assert "12" not in [r[0] for r in b.doc.table_rows]

    # 账目统计：停用会员的订单仍计入
    b.click("账目统计")
    assert b.path == "/BookShop/jsp/oderadmin.jsp"
    assert b.doc.table_rows[0][1:] == ["zhangsan", "月亮和六便士", "39.80"]
    assert b.doc.table_rows[-1][0] == "总金额：39.80元"

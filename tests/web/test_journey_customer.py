"""TEST-040：会员端端到端旅程（REQ-ACCOUNT-001、REQ-ACCOUNT-002、REQ-ACCOUNT-005、REQ-ACCOUNT-006、REQ-ACCOUNT-007、
REQ-CATALOG-001、REQ-CATALOG-004、REQ-CATALOG-005、REQ-ORDER-001、REQ-ORDER-003）。"""
import re

from tests.helpers import alert_of
from tests.web.journey import Browser


def test_customer_journey(sclient):
    b = Browser(sclient)
    b.open("/BookShop/")
    assert "最新上架" in b.doc.headings["h1"]

    # 未登录点“个人”，被带到登录页；从登录页的“注册”进入注册页
    b.click("个人")
    assert b.path == "/BookShop/login.jsp"
    onclick = [a for a, t in b.form(name="signin").buttons if t == "注册"][0]["onclick"]
    b.open("/BookShop/" + re.search(r"'([^']+)'", onclick).group(1))
    assert b.path == "/BookShop/register.jsp"

    b.submit(b.form(name="register"), {"inputUname": "zhangsan", "inputPassword": "abc123", "checkPassword": "abc123"})
    assert b.path == "/BookShop/login.jsp"
    b.submit(b.form(name="signin"), {"inputName": "zhangsan", "inputPassword": "abc123"})
    assert b.path == "/BookShop/index.jsp"

    # 浏览、搜索、筛选、详情
    b.click("购买")
    assert b.path == "/BookShop/jsp/buy.jsp" and len(b.doc.headings["h4"]) == 10
    b.submit(b.form(action_contains="book.action"), {"bname": "六便士"})
    assert b.doc.headings["h4"] == ["月亮和六便士"]
    b.click("散文")
    assert b.doc.headings["h4"] == ["清欢", "林泉", "玄想"]
    b.submit(b.form(action_contains="book.action"), {"bname": "月亮"})
    b.click("查看详情 »")
    assert b.path == "/BookShop/jsp/bookdetails.jsp" and "价格：39.80" in b.doc.headings["h4"]

    # 购买后进入我的订单
    b.submit(b.form(action_contains="buybook"))
    assert b.path == "/BookShop/jsp/myorder.jsp"
    assert b.doc.table_rows == [["zhangsan", "月亮和六便士", "39.80"]]

    # 个人页、修改密码
    b.click("个人信息")
    assert b.path == "/BookShop/jsp/my.jsp" and "zhangsan" in b.doc.headings["h4"] and "会员" in b.doc.text
    b.click("修改密码")
    r = b.submit(b.form(name="changepwd"), {"oldpwd": "abc123", "newpwd": "New#456", "anewpwd": "New#456"})
    assert alert_of(r) == ("success!", "changepwd.jsp")

    # 退出后受保护页面回到登录页
    b.open("/BookShop/jsp/changepwd.jsp")
    b.submit(b.form(action_contains="logout.action"))
    assert b.path == "/BookShop/login.jsp"
    b.open("/BookShop/jsp/my.jsp")
    assert b.path == "/BookShop/login.jsp"
    b.submit(b.form(name="signin"), {"inputName": "zhangsan", "inputPassword": "New#456"})
    assert b.path == "/BookShop/index.jsp"

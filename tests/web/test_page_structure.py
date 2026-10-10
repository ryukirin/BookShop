"""TEST-012：页面结构与文案（REQ-PLATFORM-011、REQ-PLATFORM-001 及各页面需求）。

判定依据：migration-plans/bookshop/legacy-baseline.md 中各页面的标题、导航、侧栏、
表格列名、字段名、按钮文字和链接目标。链接一律解析成站内路径后再比对。
"""
import pytest

from tests.conftest import ADMIN_PASSWORD, login, make_member, parse, resolve

CUSTOMER_NAV = [
    ("网上书店", "/BookShop/index.jsp"),
    ("主页", "/BookShop/index.jsp"),
    ("购买", "/BookShop/jsp/book.action?opttype=queryAllbook"),
    ("个人", "/BookShop/jsp/my.action?opttype=initMypage"),
]
PERSONAL_SIDEBAR = [
    ("个人信息", "/BookShop/jsp/my.jsp"),
    ("修改密码", "/BookShop/jsp/changepwd.jsp"),
    ("我的订单", "/BookShop/jsp/my.action?opttype=queryMyorder"),
]
ADMIN_SIDEBAR = [
    ("会员管理", "/BookShop/jsp/admin.action?opttype=queryAllcustomers"),
    ("书籍管理", "/BookShop/jsp/admin.action?opttype=queryAllbooks"),
    ("账目统计", "/BookShop/jsp/admin.action?opttype=showAllmoney"),
]


def links(doc, page):
    return [(t, resolve(page, a["href"])) for a, t in doc.links if a.get("href") is not None]


def assert_links(doc, page, expected):
    got = links(doc, page)
    for item in expected:
        assert item in got, f"缺少链接 {item}；实际 {got}"


def assert_strict(doc):
    assert not doc.balance_errors, doc.balance_errors


def assert_logout(doc, page, present=True):
    f = doc.form(action_contains="logout.action")
    if not present:
        assert f is None
        return
    assert f is not None, "缺少“退出”表单"
    assert resolve(page, f.action) == "/BookShop/logout.action"
    assert f.method == "post"
    assert f.hidden().get("csrf_token")
    assert "退出" in f.button_texts()


def follow(client, url):
    r = client.get(url)
    assert r.status_code == 302, (url, r.status_code)
    target = resolve(url.split("?")[0], r.headers["Location"])
    return target, client.get(target)


# ---------------- BATCH-001：首页、登录、注册 ----------------

@pytest.mark.parametrize("url", ["/BookShop/", "/BookShop/index.jsp"])
def test_index_anonymous(client, url):
    r = client.get(url)
    assert r.status_code == 200
    doc = parse(r)
    assert doc.title == "主页"
    page = "/BookShop/index.jsp"
    assert_links(doc, page, CUSTOMER_NAV[:1] + [("购买", "/BookShop/jsp/book.action?opttype=queryAllbook"),
                                                 ("个人", "/BookShop/jsp/my.action?opttype=initMypage"),
                                                 ("了解更多", "/BookShop/jsp/book.action?opttype=queryAllbook")])
    assert "最新上架" in doc.headings.get("h1", []) and "销量最高" in doc.headings.get("h1", [])
    srcs = [resolve(page, i["src"]) for i in doc.imgs]
    assert "/BookShop/img/1.jpg" in srcs and "/BookShop/img/2.jpg" in srcs
    assert "畅销热榜，点击了解详情" in doc.text
    assert_logout(doc, page, present=False)
    assert_strict(doc)


def test_login_page(client):
    r = client.get("/BookShop/login.jsp")
    assert r.status_code == 200
    doc = parse(r)
    assert doc.title == "登录"
    assert "请登录" in doc.headings.get("h2", [])
    f = doc.form(name="signin")
    assert f is not None and f.method == "post"
    assert resolve("/BookShop/login.jsp", f.action) == "/BookShop/login.action?opttype=checkUsers"
    assert f.input("inputName")["type"] == "text" and f.input("inputName")["placeholder"] == "用户名"
    assert f.input("inputPassword")["type"] == "password" and f.input("inputPassword")["placeholder"] == "密码"
    assert "required" in f.input("inputName") and "required" in f.input("inputPassword")
    assert f.hidden().get("csrf_token")
    assert f.button_texts() == ["登录", "注册"]
    reg = [a for a, t in f.buttons if t == "注册"][0]
    assert reg.get("type") == "button" and "register.jsp" in reg.get("onclick", "")
    assert_strict(doc)


def test_register_page(client):
    r = client.get("/BookShop/register.jsp")
    assert r.status_code == 200
    doc = parse(r)
    assert doc.title == "注册"
    assert "注册" in doc.headings.get("h2", [])
    f = doc.form(name="register")
    assert f is not None and f.method == "post"
    assert resolve("/BookShop/register.jsp", f.action) == "/BookShop/login.action?opttype=addusers"
    assert [f.input(n)["placeholder"] for n in ("inputUname", "inputPassword", "checkPassword")] == ["用户名", "输入密码", "确认密码"]
    assert f.input("inputPassword")["type"] == "password" and f.input("checkPassword")["type"] == "password"
    assert f.hidden().get("csrf_token")
    assert f.button_texts() == ["注册"]
    assert_strict(doc)


# ---------------- BATCH-003：登录后首页、个人页、修改密码 ----------------

@pytest.mark.batch(3)
def test_index_logged_in_has_logout(member_client):
    doc = parse(member_client.get("/BookShop/index.jsp"))
    assert_logout(doc, "/BookShop/index.jsp")


@pytest.mark.batch(3)
def test_my_page(member_client):
    page, r = follow(member_client, "/BookShop/jsp/my.action?opttype=initMypage")
    assert page == "/BookShop/jsp/my.jsp" and r.status_code == 200
    doc = parse(r)
    assert doc.title == "个人"
    assert_links(doc, page, CUSTOMER_NAV + PERSONAL_SIDEBAR)
    assert "个人信息" in doc.headings.get("h1", [])
    assert "/BookShop/img/default.jpg" in [resolve(page, i["src"]) for i in doc.imgs]
    assert "zhangsan" in doc.headings.get("h4", []) and "会员" in doc.text
    assert doc.form(action_contains="queryByname") is None
    assert_logout(doc, page)
    assert_strict(doc)


@pytest.mark.batch(3)
def test_changepwd_page(member_client):
    page = "/BookShop/jsp/changepwd.jsp"
    doc = parse(member_client.get(page))
    assert doc.title == "个人" and "修改密码" in doc.headings.get("h1", [])
    assert_links(doc, page, CUSTOMER_NAV + PERSONAL_SIDEBAR)
    f = doc.form(name="changepwd")
    assert f.method == "post" and resolve(page, f.action) == "/BookShop/jsp/my.action?opttype=updatePwd"
    assert [f.input(n)["placeholder"] for n in ("oldpwd", "newpwd", "anewpwd")] == ["旧密码", "新密码", "确认密码"]
    assert all(f.input(n)["type"] == "password" for n in ("oldpwd", "newpwd", "anewpwd"))
    assert f.button_texts() == ["提交"]
    assert_logout(doc, page)
    assert_strict(doc)


# ---------------- BATCH-004：购买页、详情页 ----------------

@pytest.mark.batch(4)
def test_buy_page(member_client):
    page, r = follow(member_client, "/BookShop/jsp/book.action?opttype=queryAllbook")
    assert page == "/BookShop/jsp/buy.jsp"
    doc = parse(r)
    assert doc.title == "购买" and "购买" in doc.headings.get("h1", [])
    assert_links(doc, page, CUSTOMER_NAV)
    search = doc.form(action_contains="book.action")
    assert search.method == "get" and search.hidden() == {"opttype": "queryByname"}
    assert search.input("bname")["placeholder"] == "查询..." and search.button_texts() == ["搜索"]
    details = [(t, h) for t, h in links(doc, page) if t == "查看详情 »"]
    assert len(details) == 10 and all(h.startswith("/BookShop/jsp/book.action?opttype=bookDetail&bid=") for _, h in details)
    assert sum(1 for i in doc.imgs if i["src"].startswith("showpic.jsp?img=")) == 10
    assert_links(doc, page, [("小说", "/BookShop/jsp/book.action?opttype=queryBytag&tname=%E5%B0%8F%E8%AF%B4")])
    assert "价格" not in doc.text
    assert_logout(doc, page)
    assert_strict(doc)


@pytest.mark.batch(4)
def test_bookdetails_page(member_client):
    page, r = follow(member_client, "/BookShop/jsp/book.action?opttype=bookDetail&bid=9")
    assert page == "/BookShop/jsp/bookdetails.jsp"
    doc = parse(r)
    assert doc.title == "购买"
    h4 = doc.headings.get("h4", [])
    for label in ("书名：", "出版商：", "价格：", "库存：", "简介：", "销量："):
        assert any(h.startswith(label) for h in h4), (label, h4)
    assert "书名：月亮和六便士" in h4
    buy = doc.form(action_contains="buybook")
    assert buy.method == "post" and buy.hidden().get("bid") == "9" and buy.hidden().get("csrf_token")
    assert buy.button_texts() == ["立即购买 »"]
    assert "showpic.jsp?img=b9.jpg" in [i["src"] for i in doc.imgs]
    assert_logout(doc, page)
    assert_strict(doc)


# ---------------- BATCH-005：我的订单 ----------------

@pytest.mark.batch(5)
def test_myorder_page(member_client):
    page, r = follow(member_client, "/BookShop/jsp/my.action?opttype=queryMyorder")
    assert page == "/BookShop/jsp/myorder.jsp"
    doc = parse(r)
    assert doc.title == "个人" and "我的订单" in doc.headings.get("h1", [])
    assert ["用户名", "书名", "订单金额"] in doc.table_headers
    assert_links(doc, page, CUSTOMER_NAV + PERSONAL_SIDEBAR)
    assert_logout(doc, page)
    assert_strict(doc)


# ---------------- BATCH-006：会员管理、账目统计 ----------------

def assert_admin_frame(doc, page):
    assert doc.title == "网上书店管理站"
    assert "网上书店管理站" not in [t for a, t in doc.links if a.get("href") is not None]
    assert "网上书店管理站" in doc.text
    assert_links(doc, page, ADMIN_SIDEBAR)
    assert_logout(doc, page)
    assert_strict(doc)


@pytest.mark.batch(6)
def test_admin_members_page(admin_client):
    page, r = follow(admin_client, "/BookShop/jsp/admin.action?opttype=queryAllcustomers")
    assert page == "/BookShop/jsp/admin.jsp"
    doc = parse(r)
    assert_admin_frame(doc, page)
    assert "会员管理" in doc.headings.get("h1", [])
    assert ["会员id", "会员名", "操作"] in doc.table_headers
    search = doc.form(action_contains="admin.action")
    assert search.method == "get" and search.hidden() == {"opttype": "queryCustomers"}
    assert search.input("uname")["placeholder"] == "查询..." and search.button_texts() == ["搜索"]


@pytest.mark.batch(6)
def test_orderadmin_page(admin_client):
    page, r = follow(admin_client, "/BookShop/jsp/admin.action?opttype=showAllmoney")
    assert page == "/BookShop/jsp/oderadmin.jsp"
    doc = parse(r)
    assert_admin_frame(doc, page)
    assert "账目统计" in doc.headings.get("h1", [])
    assert ["订单id", "用户名", "书名", "订单金额"] in doc.table_headers
    assert "总金额：0.00元" in doc.text
    assert not [f for f in doc.forms if "logout" not in (f.action or "")]


# ---------------- BATCH-007：书籍管理 ----------------

@pytest.mark.batch(7)
def test_bookadmin_page(admin_client):
    page, r = follow(admin_client, "/BookShop/jsp/admin.action?opttype=queryAllbooks")
    assert page == "/BookShop/jsp/bookadmin.jsp"
    doc = parse(r)
    assert_admin_frame(doc, page)
    assert "书籍管理" in doc.headings.get("h1", [])
    assert ["书籍id", "书名", "简介", "出版社", "分类", "库存", "售价", "销量", "操作"] in doc.table_headers
    assert_links(doc, page, [("添加", "/BookShop/jsp/add.jsp"),
                             ("修改", "/BookShop/jsp/admin.action?opttype=showBooks&bid=1")])
    search = doc.form(action_contains="admin.action")
    assert search.method == "get" and search.hidden() == {"opttype": "queryBooks"} and search.input("bname")


@pytest.mark.batch(7)
def test_add_page(admin_client):
    page = "/BookShop/jsp/add.jsp"
    doc = parse(admin_client.get(page))
    assert_admin_frame(doc, page)
    assert "书籍管理" in doc.headings.get("h1", [])
    f = doc.form(name="addbook")
    assert f.method == "post" and resolve(page, f.action) == "/BookShop/jsp/admin.action?opttype=addBooks"
    assert {"bname", "publishers", "tid", "cont", "stock", "price"} <= set(f.field_names())
    assert [t for _, t in f.selects["tid"]] == ["小说", "散文", "诗歌"]
    assert f.button_texts() == ["下一步"]
    dead = [x for x in doc.forms if x.attrs.get("action") is None and x.inputs]
    assert dead and all(not i.get("name") for i in dead[0].inputs)


@pytest.mark.batch(7)
def test_addnext_page(admin_client):
    page = "/BookShop/jsp/addnext.jsp"
    doc = parse(admin_client.get(page))
    assert_admin_frame(doc, page)
    f = doc.form(action_contains="addBooksimg")
    assert f.method == "post" and f.attrs.get("enctype") == "multipart/form-data"
    assert f.input("file")["type"] == "file" and f.button_texts() == ["提交"]
    assert "上传书籍图：" in doc.headings.get("h4", [])
    assert any(i.get("id") == "preview" for i in doc.imgs)


@pytest.mark.batch(7)
def test_editbook_page(admin_client):
    page, r = follow(admin_client, "/BookShop/jsp/admin.action?opttype=showBooks&bid=9")
    assert page == "/BookShop/jsp/editbook.jsp"
    doc = parse(r)
    assert_admin_frame(doc, page)
    assert "书籍编辑" in doc.headings.get("h1", []) and "书籍id" in doc.headings.get("h4", [])
    f = doc.form(name="addbook")
    assert resolve(page, f.action) == "/BookShop/jsp/admin.action?opttype=editBooks"
    assert "readonly" in f.input("bid") and f.input("bid")["value"] == "9"
    assert {"publishers", "stock", "price"} <= set(f.field_names())
    assert "bname" not in f.field_names() and "cont" not in f.field_names()
    assert f.button_texts() == ["提交"]

"""TEST-008：CSRF（REQ-PLATFORM-007、MIG-RULE-004、LEGACY-051、LEGACY-070）。"""
import pytest

from tests.conftest import csrf, db, parse, post

MSG = "表单令牌无效"


def test_login_page_renders_session_token(client):
    doc = parse(client.get("/BookShop/login.jsp"))
    token = doc.form(name="signin").hidden()["csrf_token"]
    with client.session_transaction("/BookShop/") as s:
        assert s["csrf"] == token
    assert len(token) >= 40


@pytest.mark.parametrize("data", [{}, {"csrf_token": "wrong"}, {"csrf_token": ""}])
def test_bad_token_rejected(client, data):
    client.get("/BookShop/login.jsp")
    r = client.post("/BookShop/login.action?opttype=checkUsers", data=dict(data, inputName="admin", inputPassword="x"))
    assert r.status_code == 400 and MSG in r.get_data(as_text=True)


def test_no_session_rejected(app):
    """没先打开登录页、直接 POST 登录（LEGACY-070 的结论）。"""
    c = app.test_client()
    r = c.post("/BookShop/login.action?opttype=checkUsers", data={"csrf_token": "x", "inputName": "admin", "inputPassword": "x"})
    assert r.status_code == 400 and MSG in r.get_data(as_text=True)
    assert c.get_cookie("session") is None or "uid" not in (c.get_cookie("session").value or "")


def test_token_from_other_session_rejected(app):
    a, b = app.test_client(), app.test_client()
    token_a = csrf(a)
    csrf(b)
    r = b.post("/BookShop/login.action?opttype=checkUsers", data={"csrf_token": token_a})
    assert r.status_code == 400


def test_logout_requires_token(client):
    client.get("/BookShop/login.jsp")
    assert client.post("/BookShop/logout.action", data={"csrf_token": "wrong"}).status_code == 400
    r = post(client, "/BookShop/logout.action")
    assert r.status_code == 302 and r.headers["Location"].endswith("/BookShop/login.jsp")


@pytest.mark.batch(3)
def test_register_requires_token(sclient):
    sclient.get("/BookShop/register.jsp")
    r = sclient.post("/BookShop/login.action?opttype=addusers",
                     data={"inputUname": "x1", "inputPassword": "a", "checkPassword": "a"})
    assert r.status_code == 400
    assert db(sclient.application.config["BOOKSHOP"].data_dir).execute(
        "SELECT COUNT(*) FROM user WHERE uname = 'x1'").fetchone()[0] == 0
    r = post(sclient, "/BookShop/login.action?opttype=addusers", {"inputUname": "x1", "inputPassword": "a", "checkPassword": "a"})
    assert r.status_code == 302


@pytest.mark.batch(5)
def test_buy_requires_token(member_client):
    r = member_client.post("/BookShop/jsp/book.action?opttype=buybook", data={"bid": "9", "csrf_token": "wrong"})
    assert r.status_code == 400
    conn = db(member_client.application.config["BOOKSHOP"].data_dir)
    assert conn.execute("SELECT stock FROM book WHERE bid = 9").fetchone()[0] == 100
    assert conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0
    assert post(member_client, "/BookShop/jsp/book.action?opttype=buybook", {"bid": "9"}).status_code == 302
    assert conn.execute("SELECT stock FROM book WHERE bid = 9").fetchone()[0] == 99


@pytest.mark.batch(7)
def test_admin_offshelf_requires_token(admin_client):
    r = admin_client.post("/BookShop/jsp/admin.action?opttype=deleteBooks", data={"bid": "1", "csrf_token": "wrong"})
    assert r.status_code == 400
    conn = db(admin_client.application.config["BOOKSHOP"].data_dir)
    assert conn.execute("SELECT on_sale FROM book WHERE bid = 1").fetchone()[0] == 1
    assert post(admin_client, "/BookShop/jsp/admin.action?opttype=deleteBooks", {"bid": "1"}).status_code == 302
    assert conn.execute("SELECT on_sale FROM book WHERE bid = 1").fetchone()[0] == 0

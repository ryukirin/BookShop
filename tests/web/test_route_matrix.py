"""TEST-004：路由矩阵与检查顺序（REQ-PLATFORM-003、REQ-PLATFORM-004、REQ-PLATFORM-015、MIG-RULE-019）。

期望值按 spec 独立写出，不从实现里读，再和实现的分派表核对一致。
“通过检查”是指请求越过了检查顺序的前 8 步：既不是跳到登录页、403、405，
也不是 opttype 或 CSRF 引起的 400。
"""
import pytest

from tests.conftest import ADMIN_PASSWORD, csrf, db, login, make_member, parse

SPEC_OPS = {
    "/BookShop/login.action": {"addusers": "POST", "checkUsers": "POST"},
    "/BookShop/jsp/book.action": {"queryAllbook": "GET", "queryByname": "GET", "queryBytag": "GET",
                                  "bookDetail": "GET", "buybook": "POST"},
    "/BookShop/jsp/my.action": {"initMypage": "GET", "queryMyorder": "GET", "updatePwd": "POST"},
    "/BookShop/jsp/admin.action": {"queryAllcustomers": "GET", "queryCustomers": "GET", "queryAllbooks": "GET",
                                   "queryBooks": "GET", "showBooks": "GET", "showAllmoney": "GET",
                                   "deleteCustomers": "POST", "addBooks": "POST", "addBooksimg": "POST",
                                   "editBooks": "POST", "deleteBooks": "POST"},
}
PROTECTED_PAGES = ["buy.jsp", "bookdetails.jsp", "my.jsp", "myorder.jsp", "changepwd.jsp"]
ADMIN_PAGES = ["admin.jsp", "bookadmin.jsp", "add.jsp", "addnext.jsp", "editbook.jsp", "oderadmin.jsp"]
REMOVED = ["/BookShop/jsp/upload.jsp", "/BookShop/jsp/download.jsp", "/BookShop/jsp/wirte.jsp",
           "/BookShop/jsp/useredit.jsp", "/BookShop/jsp/ckeditor/ckeditor.js", "/BookShop/uploadServlet.do",
           "/BookShop/downloadServlet.do", "/BookShop/nope.jsp", "/BookShop/jsp/user.action"]

MSG_OPTTYPE = "无效的操作"
MSG_CSRF = "表单令牌无效"


def other(method):
    return "POST" if method == "GET" else "GET"


def call(client, url, method, *, token=True):
    if method == "GET":
        return client.get(url)
    data = {"csrf_token": csrf(client)} if token else {}
    return client.post(url, data=data)


def is_login_redirect(r):
    return r.status_code == 302 and r.headers["Location"].endswith("/BookShop/login.jsp")


def passed_checks(r):
    if is_login_redirect(r) or r.status_code in (403, 405):
        return False
    if r.status_code == 400:
        text = r.get_data(as_text=True)
        return MSG_OPTTYPE not in text and MSG_CSRF not in text
    return True


def test_dispatch_table_matches_spec(app):
    from bookshop_web.dispatch import ACTIONS

    actual = {url: {op: spec.method for op, spec in action.ops.items()} for url, action in ACTIONS.items()}
    assert actual == SPEC_OPS


# ---------------- 未登录（BATCH-001） ----------------

@pytest.mark.parametrize("url", REMOVED)
@pytest.mark.parametrize("method", ["GET", "POST"])
def test_removed_paths_404_before_login(client, url, method):
    r = client.get(url) if method == "GET" else client.post(url)
    assert r.status_code == 404


@pytest.mark.parametrize("url", ["/BookShop/jsp/book.action", "/BookShop/jsp/my.action", "/BookShop/jsp/admin.action"])
@pytest.mark.parametrize("query", ["", "?opttype=nope", "?opttype=queryAllbook", "?opttype=buybook&bid=1",
                                   "?opttype=deleteBooks&bid=1"])
@pytest.mark.parametrize("method", ["GET", "POST"])
@pytest.mark.parametrize("token", [True, False])
def test_anonymous_protected_actions_redirect(client, url, query, method, token):
    r = call(client, url + query, method, token=token)
    assert is_login_redirect(r), (r.status_code, r.headers.get("Location"))


@pytest.mark.parametrize("page", PROTECTED_PAGES + ADMIN_PAGES)
@pytest.mark.parametrize("method", ["GET", "POST"])
def test_anonymous_protected_pages_redirect(client, page, method):
    r = call(client, "/BookShop/jsp/" + page, method)
    assert is_login_redirect(r)


@pytest.mark.parametrize("query", ["", "?opttype=", "?opttype=nope", "?opttype=queryAllbook"])
@pytest.mark.parametrize("method", ["GET", "POST"])
def test_login_action_bad_opttype_400(client, query, method):
    r = call(client, "/BookShop/login.action" + query, method)
    assert r.status_code == 400 and MSG_OPTTYPE in r.get_data(as_text=True)


@pytest.mark.parametrize("op", ["addusers", "checkUsers"])
def test_login_action_get_405(client, op):
    assert client.get(f"/BookShop/login.action?opttype={op}").status_code == 405


@pytest.mark.parametrize("op", ["addusers", "checkUsers"])
def test_login_action_post_without_token_400(client, op):
    client.get("/BookShop/login.jsp")
    r = client.post(f"/BookShop/login.action?opttype={op}", data={})
    assert r.status_code == 400 and MSG_CSRF in r.get_data(as_text=True)


@pytest.mark.parametrize("op", ["addusers", "checkUsers"])
def test_login_action_valid_passes_checks(client, op):
    assert passed_checks(call(client, f"/BookShop/login.action?opttype={op}", "POST"))


def test_logout_get_405_and_post_without_token_400(client):
    assert client.get("/BookShop/logout.action").status_code == 405
    client.get("/BookShop/login.jsp")
    r = client.post("/BookShop/logout.action", data={})
    assert r.status_code == 400 and MSG_CSRF in r.get_data(as_text=True)


@pytest.mark.parametrize("url", ["/BookShop/", "/BookShop/index.jsp", "/BookShop/login.jsp", "/BookShop/register.jsp",
                                 "/BookShop/css/signin.css", "/BookShop/img/1.jpg"])
def test_public_pages_200(client, url):
    assert client.get(url).status_code == 200


# ---------------- 登录后各身份（BATCH-003 起） ----------------
# 这些用例只检查放行和拦截，不改动数据（POST 一律带错误令牌或用错方法），所以四种身份按模块共享。

@pytest.fixture(scope="module")
def identities(tmp_path_factory, seeded_template):
    from bookshop_web import create_app
    from bookshop_web.config import Config
    from tests.conftest import TEST_SECRET, copy_seed

    d = copy_seed(seeded_template, tmp_path_factory.mktemp("route-matrix"))
    app = create_app(Config(data_dir=d, secret_key=TEST_SECRET))
    make_member(app, "zhangsan", "abc123")
    make_member(app, "lisi", "abc123")
    member = app.test_client()
    assert login(member, "zhangsan", "abc123").status_code == 302
    disabled = app.test_client()
    assert login(disabled, "lisi", "abc123").status_code == 302
    conn = db(d)
    conn.execute("UPDATE user SET active = 0 WHERE uname = 'lisi'")
    conn.close()
    admin = app.test_client()
    assert login(admin, "admin", ADMIN_PASSWORD).status_code == 302
    return {"member": member, "disabled": disabled, "admin": admin}


ALL_OPS = [(url, op, m) for url, ops in SPEC_OPS.items() for op, m in ops.items() if url != "/BookShop/login.action"]


@pytest.mark.batch(3)
@pytest.mark.parametrize("url,op,method", ALL_OPS)
def test_disabled_member_redirects(identities, url, op, method):
    assert is_login_redirect(call(identities["disabled"], f"{url}?opttype={op}", method))


@pytest.mark.batch(3)
@pytest.mark.parametrize("op", list(SPEC_OPS["/BookShop/jsp/admin.action"]) + ["nope", ""])
@pytest.mark.parametrize("method", ["GET", "POST"])
def test_member_on_admin_action_403(identities, op, method):
    r = call(identities["member"], f"/BookShop/jsp/admin.action?opttype={op}", method)
    assert r.status_code == 403


@pytest.mark.batch(3)
@pytest.mark.parametrize("page", ADMIN_PAGES)
def test_member_on_admin_pages_403(identities, page):
    assert identities["member"].get("/BookShop/jsp/" + page).status_code == 403


@pytest.mark.batch(3)
@pytest.mark.parametrize("who", ["member", "admin"])
@pytest.mark.parametrize("url", ["/BookShop/jsp/book.action", "/BookShop/jsp/my.action"])
def test_customer_actions_order(identities, who, url):
    c = identities[who]
    for q in ("", "?opttype=nope"):
        r = c.get(url + q)
        assert r.status_code == 400 and MSG_OPTTYPE in r.get_data(as_text=True)
    for op, method in SPEC_OPS[url].items():
        assert call(c, f"{url}?opttype={op}", other(method)).status_code == 405, op
        if method == "POST":
            r = c.post(f"{url}?opttype={op}", data={"csrf_token": "wrong"})
            assert r.status_code == 400 and MSG_CSRF in r.get_data(as_text=True)


@pytest.mark.batch(3)
def test_admin_action_order(identities):
    c = identities["admin"]
    url = "/BookShop/jsp/admin.action"
    assert c.get(url + "?opttype=nope").status_code == 400
    for op, method in SPEC_OPS[url].items():
        assert call(c, f"{url}?opttype={op}", other(method)).status_code == 405, op
        if method == "POST":
            r = c.post(f"{url}?opttype={op}", data={"csrf_token": "wrong"})
            assert r.status_code == 400 and MSG_CSRF in r.get_data(as_text=True)


@pytest.mark.batch(3)
def test_spec_order_scenarios(identities, client):
    assert identities["member"].get("/BookShop/jsp/admin.action?opttype=deleteBooks&bid=1").status_code == 403
    assert identities["member"].get("/BookShop/jsp/admin.action?opttype=nope").status_code == 403
    assert client.get("/BookShop/jsp/upload.jsp").status_code == 404
    assert is_login_redirect(client.post("/BookShop/jsp/book.action?opttype=buybook&bid=1", data={}))


@pytest.mark.batch(3)
@pytest.mark.parametrize("who", ["member", "admin"])
@pytest.mark.parametrize("page", PROTECTED_PAGES)
def test_customer_pages_get_ok_post_405(identities, who, page):
    c = identities[who]
    r = c.get("/BookShop/jsp/" + page)
    assert not is_login_redirect(r) and r.status_code not in (403, 405)
    assert c.post("/BookShop/jsp/" + page, data={"csrf_token": csrf(c)}).status_code == 405

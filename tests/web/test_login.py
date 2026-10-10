"""TEST-021：登录（REQ-ACCOUNT-002、LEGACY-008、LEGACY-057、LEGACY-065、EXP-006）。"""
import pytest

from tests.conftest import ADMIN_PASSWORD, alert_of, db, login, make_member

pytestmark = pytest.mark.batch(3)


def session_uid(client):
    with client.session_transaction("/BookShop/") as s:
        return s.get("uid")


def test_member_login(seeded_app):
    make_member(seeded_app)
    c = seeded_app.test_client()
    c.get("/BookShop/login.jsp")
    before = c.get_cookie("session", path="/BookShop").value
    r = login(c, "zhangsan", "abc123")
    assert r.status_code == 302 and r.headers["Location"] == "index.jsp"
    assert c.get_cookie("session", path="/BookShop").value != before
    assert session_uid(c) is not None


def test_admin_login(sclient):
    r = login(sclient, "admin", ADMIN_PASSWORD)
    assert r.status_code == 302 and r.headers["Location"] == "jsp/admin.action?opttype=queryAllcustomers"


def test_case_insensitive_name(seeded_app):
    make_member(seeded_app)
    c = seeded_app.test_client()
    assert login(c, "ZHANGSAN", "abc123").status_code == 302


@pytest.mark.parametrize("uname,pwd", [("zhangsan", "wrong"), ("nobody", "abc123"), ("zhangsan", ""),
                                       ("' OR '1'='1", "x"), ("a" * 30, "abc123")])
def test_failures_same_message(seeded_app, uname, pwd):
    make_member(seeded_app)
    c = seeded_app.test_client()
    assert alert_of(login(c, uname, pwd)) == ("username or password error!", "login.jsp")
    assert session_uid(c) is None


def test_disabled_member_cannot_login(seeded_app):
    make_member(seeded_app)
    conn = db(seeded_app.config["BOOKSHOP"].data_dir)
    conn.execute("UPDATE user SET active = 0 WHERE uname = 'zhangsan'")
    conn.close()
    c = seeded_app.test_client()
    assert alert_of(login(c, "zhangsan", "abc123")) == ("username or password error!", "login.jsp")
    assert session_uid(c) is None


def test_anonymous_session_replaced(seeded_app):
    """登录前植入的会话里没有 uid，登录后签发的是新会话（防会话固定）。"""
    make_member(seeded_app)
    c = seeded_app.test_client()
    c.get("/BookShop/login.jsp")
    with c.session_transaction("/BookShop/") as s:
        old_token = s["csrf"]
    login(c, "zhangsan", "abc123")
    with c.session_transaction("/BookShop/") as s:
        assert s["csrf"] != old_token and s["uid"] and s["sv"] == 0 and isinstance(s["login_at"], int)

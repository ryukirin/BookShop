"""TEST-024：退出登录（REQ-ACCOUNT-005、LEGACY-006、LEGACY-010、LEGACY-057）。"""
import pytest

from tests.conftest import login, make_member, parse, post

pytestmark = pytest.mark.batch(3)


def to_login(r):
    return r.status_code == 302 and r.headers["Location"].endswith("/BookShop/login.jsp")


def test_logout_invalidates_all_sessions(seeded_app):
    make_member(seeded_app)
    a, b = seeded_app.test_client(), seeded_app.test_client()
    login(a, "zhangsan", "abc123")
    login(b, "zhangsan", "abc123")
    assert b.get("/BookShop/jsp/my.jsp").status_code == 200
    r = post(a, "/BookShop/logout.action")
    assert r.status_code == 302 and r.headers["Location"].endswith("/BookShop/login.jsp")
    assert to_login(a.get("/BookShop/jsp/my.jsp"))
    assert to_login(b.get("/BookShop/jsp/my.jsp"))


def test_get_logout_405_keeps_session(member_client):
    assert member_client.get("/BookShop/logout.action").status_code == 405
    assert member_client.get("/BookShop/jsp/my.jsp").status_code == 200


@pytest.mark.parametrize("page", ["/BookShop/index.jsp", "/BookShop/jsp/my.jsp", "/BookShop/jsp/changepwd.jsp"])
def test_logout_button_present(member_client, page):
    f = parse(member_client.get(page)).form(action_contains="logout.action")
    assert f is not None and f.method == "post" and "退出" in f.button_texts()

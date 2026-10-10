"""TEST-026：修改密码（REQ-ACCOUNT-007、LEGACY-012、LEGACY-049）。"""
import pytest

from tests.conftest import alert_of, db, login, make_member, post

pytestmark = pytest.mark.batch(3)
URL = "/BookShop/jsp/my.action?opttype=updatePwd"


def change(client, old, new, again=None):
    return alert_of(post(client, URL, {"oldpwd": old, "newpwd": new, "anewpwd": new if again is None else again}))


def test_success_keeps_current_and_kills_others(seeded_app):
    make_member(seeded_app)
    a, b = seeded_app.test_client(), seeded_app.test_client()
    login(a, "zhangsan", "abc123")
    login(b, "zhangsan", "abc123")
    assert change(a, "abc123", "New#456") == ("success!", "changepwd.jsp")
    assert a.get("/BookShop/jsp/my.jsp").status_code == 200
    r = b.get("/BookShop/jsp/my.jsp")
    assert r.status_code == 302 and r.headers["Location"].endswith("/BookShop/login.jsp")
    c = seeded_app.test_client()
    assert alert_of(login(c, "zhangsan", "abc123")) == ("username or password error!", "login.jsp")
    assert login(seeded_app.test_client(), "zhangsan", "New#456").status_code == 302
    row = db(seeded_app.config["BOOKSHOP"].data_dir).execute("SELECT upwd FROM user WHERE uname = 'zhangsan'").fetchone()
    assert row[0].startswith("scrypt:") and "New#456" not in row[0]


def test_wrong_old_password(member_client):
    assert change(member_client, "bad", "New#456") == ("password error!", "changepwd.jsp")
    assert login(member_client.application.test_client(), "zhangsan", "abc123").status_code == 302


def test_old_checked_before_new_match(member_client):
    assert change(member_client, "bad", "x1", "x2") == ("password error!", "changepwd.jsp")


def test_new_mismatch(member_client):
    assert change(member_client, "abc123", "x1", "x2") == ("check new password!", "changepwd.jsp")


@pytest.mark.parametrize("new", ["", "p" * 65])
def test_new_length(member_client, new):
    assert change(member_client, "abc123", new) == ("check new password!", "changepwd.jsp")

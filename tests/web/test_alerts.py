"""TEST-007：alert 提示机制与文案（REQ-PLATFORM-006、MIG-RULE-020、LEGACY-034）。"""
import pytest

from tests.conftest import alert_of, login, post, register

LEGACY_TEXTS = [
    "please change uer name!",
    "please check password!",
    "fail,try again!",
    "username or password error!",
    "success!",
    "password error!",
    "check new password!",
]
NEW_TEXTS = [
    "please check user name or password!",
    "out of stock!",
    "please check book info!",
    "please fill in book info first!",
    "please upload a png or jpg image!",
]


def test_mechanism_format(app):
    from bookshop_web.responses import alert

    with app.test_request_context():
        resp = alert("username_error", "login.jsp")
    assert resp.status_code == 200
    assert resp.mimetype == "text/html" and resp.mimetype_params.get("charset") == "utf-8"
    assert resp.get_data(as_text=True) == "<script>alert('username or password error!'); window.location='login.jsp' </script>"


def test_mechanism_texts_are_fixed(app):
    from bookshop_web.responses import ALERTS, alert

    for text in LEGACY_TEXTS + NEW_TEXTS:
        assert text in ALERTS.values(), text
    with app.test_request_context(), pytest.raises(KeyError):
        alert("arbitrary text from user", "login.jsp")


@pytest.mark.batch(3)
def test_legacy_login_error(sclient):
    assert alert_of(login(sclient, "admin", "wrong")) == ("username or password error!", "login.jsp")


@pytest.mark.batch(3)
def test_legacy_register_texts(sclient):
    assert register(sclient, "zhangsan", "abc123").status_code == 302
    assert alert_of(register(sclient, "zhangsan", "abc123")) == ("please change uer name!", "register.jsp")
    assert alert_of(register(sclient, "lisi", "abc123", check="abc124")) == ("please check password!", "register.jsp")


@pytest.mark.batch(3)
def test_legacy_change_password_texts(member_client):
    url = "/BookShop/jsp/my.action?opttype=updatePwd"
    assert alert_of(post(member_client, url, {"oldpwd": "bad", "newpwd": "x1", "anewpwd": "x1"})) == ("password error!", "changepwd.jsp")
    assert alert_of(post(member_client, url, {"oldpwd": "abc123", "newpwd": "x1", "anewpwd": "x2"})) == ("check new password!", "changepwd.jsp")
    assert alert_of(post(member_client, url, {"oldpwd": "abc123", "newpwd": "x1", "anewpwd": "x1"})) == ("success!", "changepwd.jsp")


@pytest.mark.batch(3)
def test_new_register_length_text(sclient):
    assert alert_of(register(sclient, "a" * 21, "abc123")) == ("please check user name or password!", "register.jsp")

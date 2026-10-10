"""TEST-020：注册（REQ-ACCOUNT-001、LEGACY-007、LEGACY-049、LEGACY-065、LEGACY-073、EXP-004）。"""
import pytest

from tests.conftest import alert_of, db, register

pytestmark = pytest.mark.batch(3)


def users(app):
    c = db(app.config["BOOKSHOP"].data_dir)
    try:
        return {r["uname"]: dict(r) for r in c.execute("SELECT * FROM user")}
    finally:
        c.close()


def test_success(sclient, seeded_app):
    r = register(sclient, "zhangsan", "abc123")
    assert r.status_code == 302 and r.headers["Location"] == "login.jsp"
    u = users(seeded_app)["zhangsan"]
    assert (u["role"], u["active"], u["session_version"]) == (1, 1, 0)
    assert u["upwd"].startswith("scrypt:32768:8:1$") and u["upwd"] != "abc123"


def test_no_auto_login(sclient):
    assert register(sclient, "zhangsan", "abc123").status_code == 302
    r = sclient.get("/BookShop/jsp/my.jsp")
    assert r.status_code == 302 and r.headers["Location"].endswith("/BookShop/login.jsp")


@pytest.mark.parametrize("name", ["zhangsan", "ZhangSan", "ZHANGSAN"])
def test_duplicate_case_insensitive(sclient, seeded_app, name):
    register(sclient, "zhangsan", "abc123")
    assert alert_of(register(sclient, name, "abc123")) == ("please change uer name!", "register.jsp")
    assert len(users(seeded_app)) == 2


def test_name_checked_before_password_match(sclient):
    register(sclient, "zhangsan", "abc123")
    assert alert_of(register(sclient, "zhangsan", "abc123", check="zzz")) == ("please change uer name!", "register.jsp")


def test_password_mismatch(sclient, seeded_app):
    assert alert_of(register(sclient, "lisi", "abc123", check="abc124")) == ("please check password!", "register.jsp")
    assert "lisi" not in users(seeded_app)


@pytest.mark.parametrize("uname,pwd", [("a" * 21, "abc123"), ("", "abc123"), ("ok", ""), ("ok", "p" * 65)])
def test_lengths(sclient, seeded_app, uname, pwd):
    assert alert_of(register(sclient, uname, pwd)) == ("please check user name or password!", "register.jsp")
    assert len(users(seeded_app)) == 1


def test_length_limits_inclusive(sclient, seeded_app):
    assert register(sclient, "a" * 20, "p" * 64).status_code == 302
    assert "a" * 20 in users(seeded_app)


def test_disabled_member_name_still_taken(sclient, seeded_app):
    register(sclient, "lisi", "abc123")
    c = db(seeded_app.config["BOOKSHOP"].data_dir)
    c.execute("UPDATE user SET active = 0 WHERE uname = 'lisi'")
    c.close()
    assert alert_of(register(sclient, "LiSi", "abc123")) == ("please change uer name!", "register.jsp")


def test_other_write_failure(sclient, monkeypatch):
    import bookshop_web.views.account as account

    monkeypatch.setattr(account, "generate_password_hash", lambda pw: "x" * 300)
    assert alert_of(register(sclient, "wangwu", "abc123")) == ("fail,try again!", "register.jsp")


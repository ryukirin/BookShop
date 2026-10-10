"""TEST-022：会话有效性、吊销与 Cookie 大小（REQ-ACCOUNT-003、MIG-RULE-021、DEC-004、DEC-016、EXP-006、EXP-011）。"""
import random
import secrets
import time

import pytest

from tests.conftest import db, login, make_member, post

MY = "/BookShop/jsp/my.action?opttype=initMypage"


def to_login(r):
    return r.status_code == 302 and r.headers["Location"].endswith("/BookShop/login.jsp")


# BATCH-001 的检查顺序已实现这一项。
def test_unauthenticated(sclient):
    assert to_login(sclient.get("/BookShop/jsp/my.jsp"))


@pytest.mark.batch(3)
def test_valid_session(member_client):
    r = member_client.get(MY)
    assert r.status_code == 302 and r.headers["Location"] == "my.jsp"


@pytest.mark.batch(3)
def test_replay_after_logout(member_client):
    cookie = member_client.get_cookie("session", path="/BookShop").value
    assert post(member_client, "/BookShop/logout.action").status_code == 302
    member_client.set_cookie("session", cookie, path="/BookShop")
    assert to_login(member_client.get(MY))


@pytest.mark.batch(3)
def test_session_version_mismatch(member_client):
    conn = db(member_client.application.config["BOOKSHOP"].data_dir)
    conn.execute("UPDATE user SET session_version = session_version + 1 WHERE uname = 'zhangsan'")
    conn.close()
    assert to_login(member_client.get(MY))


@pytest.mark.batch(3)
def test_absolute_lifetime(member_client, monkeypatch):
    import bookshop_web.security as security

    real = time.time()
    monkeypatch.setattr(security, "clock", lambda: real + 8 * 3600 + 5)
    assert to_login(member_client.get(MY))


@pytest.mark.batch(3)
def test_idle_timeout(member_client, monkeypatch):
    import itsdangerous.timed

    real = time.time
    monkeypatch.setattr(itsdangerous.timed.time, "time", lambda: real() + 31 * 60)
    assert to_login(member_client.get(MY))


@pytest.mark.batch(3)
def test_disabled_session_invalidated(member_client):
    conn = db(member_client.application.config["BOOKSHOP"].data_dir)
    conn.execute("UPDATE user SET active = 0 WHERE uname = 'zhangsan'")
    conn.close()
    assert to_login(member_client.get(MY))
    with member_client.session_transaction("/BookShop/") as s:
        assert "uid" not in s


@pytest.mark.batch(3)
def test_cookie_attributes(seeded_app):
    make_member(seeded_app)
    c = seeded_app.test_client()
    r = login(c, "zhangsan", "abc123")
    sc = r.headers["Set-Cookie"]
    for part in ("HttpOnly", "SameSite=Lax", "Path=/BookShop", "Expires="):
        assert part in sc, sc


@pytest.mark.batch(3)
def test_session_holds_only_allowed_keys(member_client):
    with member_client.session_transaction("/BookShop/") as s:
        assert set(s) <= {"uid", "sv", "login_at", "csrf", "_permanent", "q_catalogue", "q_admin_books",
                          "q_admin_customers", "detail_bid", "edit_bid"}
        assert "uname" not in s and "role" not in s


@pytest.mark.batch(3)
def test_cookie_size_worst_case(member_client):
    rng = random.Random(0)

    def cjk(n):
        return "".join(chr(rng.randint(0x4E00, 0x9FFF)) for _ in range(n))

    with member_client.session_transaction("/BookShop/") as s:
        s["q_catalogue"] = {"op": "queryByname", "q": cjk(100)}
        s["q_admin_books"] = {"q": cjk(100)}
        s["q_admin_customers"] = {"q": cjk(20)}
        s["detail_bid"] = 10 ** 17
        s["edit_bid"] = 10 ** 17
    r = member_client.get(MY)
    assert len(r.headers["Set-Cookie"]) <= 3000, len(r.headers["Set-Cookie"])

"""TEST-006：错误页与数据库异常（REQ-PLATFORM-005、LEGACY-033、DEC-017）。"""
import logging
import time

import pytest

from tests.conftest import csrf


def test_error_pages_have_code_and_message(client):
    cases = [
        (client.get("/BookShop/nope.jsp"), 404, "页面不存在"),
        (client.get("/BookShop/login.action"), 400, "无效的操作"),
        (client.get("/BookShop/login.action?opttype=checkUsers"), 405, "不支持该请求方法"),
        (client.post("/BookShop/login.action?opttype=checkUsers", data={"csrf_token": csrf(client), "x": "y" * (6 * 1024 * 1024)}),
         413, "请求内容过大"),
    ]
    for r, code, text in cases:
        body = r.get_data(as_text=True)
        assert r.status_code == code and str(code) in body and text in body, (code, body[:200])


@pytest.mark.batch(2)
def test_database_error_gives_500_and_log(seeded_app, seeded, caplog):
    from bookshop_web.db import db_path

    p = db_path(seeded)
    for suffix in ("-wal", "-shm"):
        q = p.with_name(p.name + suffix)
        if q.exists():
            q.unlink()
    p.write_bytes(b"this is not a sqlite database" * 100)
    c = seeded_app.test_client()
    with c.session_transaction("/BookShop/") as s:
        s.update(uid=1, sv=0, login_at=int(time.time()), csrf="t")
    caplog.set_level(logging.INFO)
    r = c.get("/BookShop/index.jsp")
    body = r.get_data(as_text=True)
    assert r.status_code == 500 and "500" in body and "服务器内部错误" in body
    messages = [x.getMessage() for x in caplog.records]
    assert any("DatabaseError" in m and "/BookShop/index.jsp" in m for m in messages), messages


@pytest.mark.batch(3)
def test_403_page(member_client):
    r = member_client.get("/BookShop/jsp/admin.jsp")
    assert r.status_code == 403 and "没有权限" in r.get_data(as_text=True)

"""TEST-013：日志脱敏（REQ-PLATFORM-013、MIG-RULE-017、LEGACY-038）。"""
import logging

import pytest

from tests.conftest import login, post, register


def endpoint_for(app, path):
    return next(r.endpoint for r in app.url_map.iter_rules() if r.rule == path)


def test_framework_request_log_has_no_query(client, caplog):
    caplog.set_level(logging.INFO, logger="bookshop")
    client.get("/BookShop/login.jsp?token=SECRET-QS")
    messages = [r.getMessage() for r in caplog.records if r.name.startswith("bookshop")]
    assert "GET /BookShop/login.jsp 200" in messages
    assert not any("SECRET-QS" in m for m in messages)


def test_framework_500_logs_type_and_path_only(app, client, caplog):
    def boom():
        raise RuntimeError("SELECT upwd FROM user WHERE uname = 'zhangsan'")

    app.view_functions[endpoint_for(app, "/BookShop/login.jsp")] = boom
    caplog.set_level(logging.INFO)
    r = client.get("/BookShop/login.jsp")
    assert r.status_code == 500 and "500" in r.get_data(as_text=True)
    text = "\n".join(r.getMessage() + (r.exc_text or "") for r in caplog.records)
    assert "RuntimeError" in text and "/BookShop/login.jsp" in text
    assert "SELECT" not in text and "zhangsan" not in text
    assert all(r.exc_info is None for r in caplog.records)


@pytest.mark.batch(3)
def test_passwords_not_logged(seeded_app, caplog):
    caplog.set_level(logging.DEBUG)
    c = seeded_app.test_client()
    assert register(c, "zhangsan", "Secret#123").status_code == 302
    assert login(c, "zhangsan", "Secret#123").status_code == 302
    r = post(c, "/BookShop/jsp/my.action?opttype=updatePwd", {"oldpwd": "Secret#123", "newpwd": "Other#456", "anewpwd": "Other#456"})
    assert "success!" in r.get_data(as_text=True)
    text = "\n".join(r.getMessage() + (r.exc_text or "") for r in caplog.records)
    assert "Secret#123" not in text and "Other#456" not in text
    assert "INSERT" not in text and "SELECT" not in text

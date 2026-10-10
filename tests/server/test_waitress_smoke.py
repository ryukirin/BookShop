"""TEST-003：waitress 冒烟（REQ-PLATFORM-001、REQ-PLATFORM-012、DEC-013、EXP-009）。"""
import urllib.request

import pytest

pytestmark = pytest.mark.server


def get(srv, path):
    return urllib.request.urlopen(f"http://127.0.0.1:{srv.effective_port}{path}", timeout=10)


def test_pages_over_real_http(live):
    for path, text in (("/BookShop/", "最新上架"), ("/BookShop/login.jsp", "请登录")):
        r = get(live, path)
        assert r.status == 200
        assert r.headers["Content-Type"] == "text/html; charset=utf-8"
        assert text in r.read().decode("utf-8")


def test_bound_to_loopback(live):
    assert live.effective_host == "127.0.0.1"


def test_request_body_limit_configured(live):
    from bookshop_web.server import MAX_REQUEST_BODY

    assert MAX_REQUEST_BODY == 6 * 1024 * 1024
    assert live.adj.max_request_body_size == MAX_REQUEST_BODY

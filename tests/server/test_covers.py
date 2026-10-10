"""TEST-029（真实 waitress 部分）：封面类型与路径穿越（REQ-CATALOG-007、REQ-CATALOG-008、EXP-012）。"""
import http.client

import pytest

pytestmark = [pytest.mark.server, pytest.mark.batch(4)]


def get(srv, path):
    conn = http.client.HTTPConnection("127.0.0.1", srv.effective_port, timeout=10)
    conn.request("GET", path)
    r = conn.getresponse()
    r.read()
    conn.close()
    return r


def test_png_content_type(live_seeded):
    r = get(live_seeded, "/BookShop/img/b6.jpg")
    assert r.status == 200 and r.getheader("Content-Type") == "image/png"


def test_jpeg_content_type(live_seeded):
    r = get(live_seeded, "/BookShop/img/b1.jpg")
    assert r.status == 200 and r.getheader("Content-Type") == "image/jpeg"


@pytest.mark.parametrize("path", ["/BookShop/img/..%2Fbookshop.db", "/BookShop/img/%2e%2e%5cbookshop.db",
                                  "/BookShop/img/../bookshop.db"])
def test_traversal(live_seeded, path):
    assert get(live_seeded, "/BookShop/img/b1.jpg").status == 200
    assert get(live_seeded, path).status == 404

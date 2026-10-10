"""TEST-014（测试客户端部分）：应用层 5 MiB 上限（REQ-PLATFORM-014、MIG-RULE-009）。"""
import io

import pytest

from tests.conftest import csrf

BIG = 6 * 1024 * 1024


def test_public_post_over_limit_413(client):
    token = csrf(client)
    r = client.post("/BookShop/login.action?opttype=checkUsers", data={"csrf_token": token, "inputName": "x" * BIG})
    assert r.status_code == 413 and "请求内容过大" in r.get_data(as_text=True)


# 两层上限在 BATCH-001 已实现，上传请求同样适用。
def test_upload_over_limit_413(admin_client):
    token = csrf(admin_client)
    data = {"csrf_token": token, "file": (io.BytesIO(b"\xff\xd8\xff" + b"0" * BIG), "a.jpg")}
    r = admin_client.post("/BookShop/jsp/admin.action?opttype=addBooksimg", data=data, content_type="multipart/form-data")
    assert r.status_code == 413

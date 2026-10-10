"""TEST-016（请求部分）：每个请求的连接在结束时关闭（REQ-DATA-002、COMP-006）。"""
import os
import time

import pytest

pytestmark = pytest.mark.batch(2)


def test_request_connection_has_foreign_keys(seeded_app):
    from bookshop_web.db import get_db

    with seeded_app.test_request_context("/BookShop/index.jsp"):
        assert get_db().execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_db_files_deletable_after_requests(seeded_app, seeded):
    c = seeded_app.test_client()
    with c.session_transaction("/BookShop/") as s:
        s.update(uid=1, sv=0, login_at=int(time.time()), csrf="t")
    for _ in range(3):
        assert c.get("/BookShop/index.jsp").status_code == 200
    from bookshop_web.db import db_path

    p = str(db_path(seeded))
    for suffix in ("", "-wal", "-shm"):
        if os.path.exists(p + suffix):
            os.remove(p + suffix)
    assert not os.path.exists(p)

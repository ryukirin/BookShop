"""公共夹具。

批次控制：标了 ``@pytest.mark.batch(n)`` 的用例属于 BATCH-00n。n 大于 CURRENT_BATCH 时，
按严格 xfail 处理：批次开始前确认它们确实失败（先红），批次完成、把 CURRENT_BATCH
加一以后，它们必须真正通过（后绿），意外通过会被当作失败。
"""
from __future__ import annotations

import secrets
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests import helpers  # noqa: E402

CURRENT_BATCH = 8

TEST_SECRET = secrets.token_hex(32)
ADMIN_PASSWORD = "Admin#2026"


def pytest_configure(config):
    config.addinivalue_line("markers", "batch(n): 用例属于 BATCH-00n，批次完成前按严格 xfail 处理")
    config.addinivalue_line("markers", "server: 需要启动真实 waitress 的用例")


def pytest_collection_modifyitems(config, items):
    for item in items:
        mark = item.get_closest_marker("batch")
        if mark and mark.args[0] > CURRENT_BATCH:
            item.add_marker(pytest.mark.xfail(strict=True, reason=f"BATCH-{mark.args[0]:03d} 尚未实现（先红后绿）"))


@pytest.fixture
def data_dir(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    return d


@pytest.fixture
def config(data_dir):
    from bookshop_web.config import Config

    return Config(data_dir=data_dir, secret_key=TEST_SECRET, host="127.0.0.1", port=8080)


@pytest.fixture(scope="session")
def seeded_template(tmp_path_factory):
    """整个测试会话只真正执行一次 init-db；各用例复制这份模板库（init-db 本身由 TEST-017 直接测试）。"""
    from bookshop_web.initdb import init_db

    d = tmp_path_factory.mktemp("seed-template")
    init_db(d, ADMIN_PASSWORD)
    assert not (d / "bookshop.db-wal").exists()
    return d


def copy_seed(template: Path, target: Path) -> Path:
    import shutil

    shutil.copyfile(template / "bookshop.db", target / "bookshop.db")
    shutil.copytree(template / "covers", target / "covers")
    return target


@pytest.fixture
def seeded(data_dir, seeded_template):
    """演示数据和管理员已就位的数据目录（BATCH-002 起可用）。"""
    return copy_seed(seeded_template, data_dir)


@pytest.fixture
def app(config):
    from bookshop_web import create_app

    return create_app(config)


@pytest.fixture
def seeded_app(seeded, config):
    from bookshop_web import create_app

    return create_app(config)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sclient(seeded_app):
    return seeded_app.test_client()


def csrf(client) -> str:
    """取当前会话的 CSRF 令牌；没有时先打开登录页让服务端生成。"""
    with client.session_transaction("/BookShop/") as s:
        token = s.get("csrf")
    if not token:
        client.get("/BookShop/login.jsp")
        with client.session_transaction("/BookShop/") as s:
            token = s.get("csrf")
    return token


def post(client, url, data=None, *, token=True, **kw):
    data = dict(data or {})
    if token and "csrf_token" not in data:
        data["csrf_token"] = csrf(client)
    return client.post(url, data=data, **kw)


def login(client, uname, pwd):
    client.get("/BookShop/login.jsp")
    return post(client, "/BookShop/login.action?opttype=checkUsers", {"inputName": uname, "inputPassword": pwd})


def register(client, uname, pwd, check=None):
    client.get("/BookShop/register.jsp")
    return post(client, "/BookShop/login.action?opttype=addusers",
                {"inputUname": uname, "inputPassword": pwd, "checkPassword": pwd if check is None else check})


def make_member(app, uname="zhangsan", pwd="abc123"):
    c = app.test_client()
    r = register(c, uname, pwd)
    assert r.status_code == 302, r.get_data(as_text=True)
    return uname, pwd


@pytest.fixture
def admin_client(seeded_app):
    c = seeded_app.test_client()
    r = login(c, "admin", ADMIN_PASSWORD)
    assert r.status_code == 302
    return c


@pytest.fixture
def member_client(seeded_app):
    make_member(seeded_app)
    c = seeded_app.test_client()
    r = login(c, "zhangsan", "abc123")
    assert r.status_code == 302
    return c


def db(data_dir):
    import sqlite3

    conn = sqlite3.connect(Path(data_dir) / "bookshop.db", isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


parse = helpers.parse
alert_of = helpers.alert_of
resolve = helpers.resolve

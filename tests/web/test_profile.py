"""TEST-025：个人页（REQ-ACCOUNT-006、LEGACY-011）。"""
import pytest

from tests.conftest import db, parse

pytestmark = pytest.mark.batch(3)


def profile(client):
    r = client.get("/BookShop/jsp/my.action?opttype=initMypage")
    assert r.status_code == 302 and r.headers["Location"] == "my.jsp"
    return parse(client.get("/BookShop/jsp/my.jsp"))


def test_member_profile(member_client):
    doc = profile(member_client)
    assert "zhangsan" in doc.headings["h4"] and "会员" in doc.text


def test_admin_profile(admin_client):
    doc = profile(admin_client)
    assert "admin" in doc.headings["h4"] and "管理员" in doc.text


def test_reads_name_from_database(member_client):
    profile(member_client)
    conn = db(member_client.application.config["BOOKSHOP"].data_dir)
    conn.execute("UPDATE user SET uname = 'zhangsan2' WHERE uname = 'zhangsan'")
    conn.close()
    assert "zhangsan2" in parse(member_client.get("/BookShop/jsp/my.jsp")).headings["h4"]

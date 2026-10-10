"""TEST-023：管理端授权（REQ-ACCOUNT-004、MIG-RULE-003、LEGACY-050、LEGACY-011）。"""
import pytest

from tests.conftest import db

ADMIN_URLS = ["/BookShop/jsp/admin.action?opttype=queryAllcustomers", "/BookShop/jsp/admin.jsp",
              "/BookShop/jsp/bookadmin.jsp", "/BookShop/jsp/add.jsp", "/BookShop/jsp/addnext.jsp",
              "/BookShop/jsp/editbook.jsp", "/BookShop/jsp/oderadmin.jsp"]


@pytest.mark.batch(3)
@pytest.mark.parametrize("url", ADMIN_URLS)
def test_member_forbidden(member_client, url):
    assert member_client.get(url).status_code == 403


@pytest.mark.batch(3)
@pytest.mark.parametrize("url", ADMIN_URLS)
def test_admin_passes_gate_after_profile(admin_client, url):
    assert admin_client.get("/BookShop/jsp/my.action?opttype=initMypage").status_code == 302
    assert admin_client.get("/BookShop/jsp/my.jsp").status_code == 200
    r = admin_client.get(url)
    assert r.status_code != 403 and not (r.status_code == 302 and r.headers["Location"].endswith("/BookShop/login.jsp"))


@pytest.mark.batch(3)
def test_role_read_from_database(member_client):
    url = "/BookShop/jsp/admin.jsp"
    assert member_client.get(url).status_code == 403
    conn = db(member_client.application.config["BOOKSHOP"].data_dir)
    conn.execute("UPDATE user SET role = 2 WHERE uname = 'zhangsan'")
    conn.close()
    r = member_client.get(url)
    assert r.status_code != 403 and not (r.status_code == 302 and r.headers["Location"].endswith("/BookShop/login.jsp"))


@pytest.mark.batch(6)
def test_admin_profile_then_revenue(admin_client):
    r1 = admin_client.get("/BookShop/jsp/my.action?opttype=initMypage")
    r2 = admin_client.get("/BookShop/jsp/admin.action?opttype=showAllmoney")
    assert (r1.status_code, r1.headers["Location"]) == (302, "my.jsp")
    assert (r2.status_code, r2.headers["Location"]) == (302, "oderadmin.jsp")

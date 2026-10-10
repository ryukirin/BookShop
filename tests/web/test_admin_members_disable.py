"""TEST-034：停用会员（REQ-MEMBER-003、LEGACY-030、LEGACY-044、MIG-RULE-008）。"""
import pytest

from tests.conftest import alert_of, db, login, make_member, post, register

pytestmark = pytest.mark.batch(6)
DISABLE = "/BookShop/jsp/admin.action?opttype=deleteCustomers"


@pytest.fixture
def member_with_orders(seeded_app):
    make_member(seeded_app)
    c = db(seeded_app.config["BOOKSHOP"].data_dir)
    uid = c.execute("SELECT uid FROM user WHERE uname = 'zhangsan'").fetchone()[0]
    c.execute("INSERT INTO orders (bid, uid, unit_price_cents) VALUES (9, ?, 3980), (1, ?, 3950)", (uid, uid))
    c.close()
    return uid


def test_disable(seeded_app, admin_client, member_with_orders):
    uid = member_with_orders
    member = seeded_app.test_client()
    assert login(member, "zhangsan", "abc123").status_code == 302
    r = post(admin_client, DISABLE, {"uid": str(uid)})
    assert r.status_code == 302 and r.headers["Location"] == "admin.action?opttype=queryAllcustomers"
    c = db(seeded_app.config["BOOKSHOP"].data_dir)
    row = c.execute("SELECT active, session_version FROM user WHERE uid = ?", (uid,)).fetchone()
    assert (row["active"], row["session_version"]) == (0, 1)
    assert c.execute("SELECT COUNT(*) FROM orders WHERE uid = ?", (uid,)).fetchone()[0] == 2
    r = member.get("/BookShop/jsp/my.action?opttype=initMypage")
    assert r.status_code == 302 and r.headers["Location"].endswith("/BookShop/login.jsp")
    assert alert_of(login(seeded_app.test_client(), "zhangsan", "abc123")) == ("username or password error!", "login.jsp")
    assert alert_of(register(seeded_app.test_client(), "ZhangSan", "abc123"))[0] == "please change uer name!"


def test_cannot_disable_self_or_admin(admin_client, seeded_app):
    assert post(admin_client, DISABLE, {"uid": "1"}).status_code == 404
    c = db(seeded_app.config["BOOKSHOP"].data_dir)
    assert c.execute("SELECT active FROM user WHERE uid = 1").fetchone()[0] == 1


def test_already_disabled_404(admin_client, member_with_orders):
    assert post(admin_client, DISABLE, {"uid": str(member_with_orders)}).status_code == 302
    assert post(admin_client, DISABLE, {"uid": str(member_with_orders)}).status_code == 404


@pytest.mark.parametrize("uid,status", [("999", 404), ("abc", 400), ("", 400), ("0", 400)])
def test_bad_uid(admin_client, uid, status):
    assert post(admin_client, DISABLE, {"uid": uid}).status_code == status

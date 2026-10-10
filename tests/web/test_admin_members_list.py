"""TEST-033：会员列表与搜索（REQ-MEMBER-001、REQ-MEMBER-002、LEGACY-022、LEGACY-023）。"""
import pytest

from tests.conftest import db, make_member, parse

pytestmark = pytest.mark.batch(6)
ADMIN = "/BookShop/jsp/admin.action"


@pytest.fixture
def members(seeded_app, admin_client):
    for name in ("zhangsan", "lisi", "wangwu"):
        make_member(seeded_app, name, "abc123")
    c = db(seeded_app.config["BOOKSHOP"].data_dir)
    c.execute("UPDATE user SET active = 0 WHERE uname = 'lisi'")
    ids = {r["uname"]: r["uid"] for r in c.execute("SELECT uid, uname FROM user")}
    c.close()
    return ids


def rows(client, query):
    r = client.get(f"{ADMIN}?{query}")
    assert r.status_code == 302 and r.headers["Location"] == "admin.jsp"
    doc = parse(client.get("/BookShop/jsp/admin.jsp"))
    return doc, [row[:2] for row in doc.table_rows]


def test_list_active_members_by_uid(admin_client, members):
    doc, got = rows(admin_client, "opttype=queryAllcustomers")
    assert got == [[str(members["zhangsan"]), "zhangsan"], [str(members["wangwu"]), "wangwu"]]
    forms = [f for f in doc.forms if "deleteCustomers" in (f.action or "")]
    assert len(forms) == 2 and all(f.method == "post" and f.hidden().get("csrf_token") for f in forms)
    assert forms[0].hidden()["uid"] == str(members["zhangsan"]) and forms[0].button_texts() == ["删除"]


@pytest.mark.parametrize("q,expected", [("ZHANGSAN", ["zhangsan"]), ("zhangsan", ["zhangsan"]), ("lisi", []),
                                        ("admin", []), ("", []), ("zhang", [])])
def test_search(admin_client, members, q, expected):
    _, got = rows(admin_client, f"opttype=queryCustomers&uname={q}")
    assert [name for _, name in got] == expected


def test_criteria_in_session(admin_client, members):
    admin_client.get(f"{ADMIN}?opttype=queryCustomers&uname=wangwu")
    with admin_client.session_transaction("/BookShop/") as s:
        assert s["q_admin_customers"] == {"op": "name", "q": "wangwu"}
    assert [r[1] for r in parse(admin_client.get("/BookShop/jsp/admin.jsp")).table_rows] == ["wangwu"]

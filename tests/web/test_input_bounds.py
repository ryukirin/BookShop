"""TEST-019（页面部分）：各表单和查询参数的上下限（REQ-DATA-005、MIG-RULE-018、LEGACY-059）。"""
import pytest

from tests.conftest import alert_of, csrf, post, register


@pytest.mark.batch(3)
@pytest.mark.parametrize("uname,pwd,ok", [("a" * 20, "p" * 64, True), ("a" * 21, "abc", False), ("ab", "p" * 65, False)])
def test_register_bounds(sclient, uname, pwd, ok):
    r = register(sclient, uname, pwd)
    assert (r.status_code == 302) is ok
    if not ok:
        assert alert_of(r)[0] == "please check user name or password!"


@pytest.mark.batch(4)
@pytest.mark.parametrize("query,status", [
    ("opttype=queryByname&bname=" + "a" * 100, 302), ("opttype=queryByname&bname=" + "a" * 101, 400),
    ("opttype=queryBytag&tname=" + "a" * 20, 302), ("opttype=queryBytag&tname=" + "a" * 21, 400),
    ("opttype=bookDetail&bid=0", 400), ("opttype=bookDetail&bid=abc", 400),
    ("opttype=bookDetail&bid=99999999999999999999", 400), ("opttype=bookDetail&bid=999", 404),
])
def test_catalogue_params(member_client, query, status):
    assert member_client.get("/BookShop/jsp/book.action?" + query).status_code == status


@pytest.mark.batch(6)
@pytest.mark.parametrize("q,status", [("a" * 20, 302), ("a" * 21, 400)])
def test_member_search_bounds(admin_client, q, status):
    assert admin_client.get("/BookShop/jsp/admin.action?opttype=queryCustomers&uname=" + q).status_code == status


@pytest.mark.batch(7)
@pytest.mark.parametrize("field,value", [("bname", "书" * 101), ("publishers", ""), ("cont", "简" * 4001),
                                         ("stock", "-1"), ("stock", "1000000"), ("stock", "99999999999999999999"),
                                         ("stock", "1.5"), ("price", "25.555"), ("price", "100000"), ("price", "abc"),
                                         ("tid", "99"), ("tid", "abc")])
def test_add_book_bounds(admin_client, field, value):
    data = {"bname": "测试书", "publishers": "测试出版社", "tid": "1", "cont": "简介", "stock": "10", "price": "25.50"}
    data[field] = value
    r = post(admin_client, "/BookShop/jsp/admin.action?opttype=addBooks", data)
    assert alert_of(r) == ("please check book info!", "add.jsp")

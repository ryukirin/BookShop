"""TEST-036：两步新增书籍（REQ-BOOK-003、REQ-BOOK-004、LEGACY-026、LEGACY-027、LEGACY-055、LEGACY-071、LEGACY-072、COMP-024、DEC-021）。"""
import io
import re

import pytest

from tests.conftest import alert_of, csrf, db, post

pytestmark = pytest.mark.batch(7)
STEP1 = "/BookShop/jsp/admin.action?opttype=addBooks"
STEP2 = "/BookShop/jsp/admin.action?opttype=addBooksimg"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 64
GOOD = {"bname": "测试书", "publishers": "测试出版社", "tid": "1", "cont": "简" * 4000, "stock": "10", "price": "25.50"}


def conn_of(client):
    return db(client.application.config["BOOKSHOP"].data_dir)


def covers_of(client):
    return sorted(p.name for p in (client.application.config["BOOKSHOP"].data_dir / "covers").iterdir())


def upload(client, content, filename):
    data = {"csrf_token": csrf(client), "file": (io.BytesIO(content), filename)}
    return client.post(STEP2, data=data, content_type="multipart/form-data")


def test_step1_saves_server_draft(admin_client):
    r = post(admin_client, STEP1, GOOD)
    assert r.status_code == 302 and r.headers["Location"] == "addnext.jsp"
    assert len(r.headers.get("Set-Cookie", "")) <= 3000
    row = conn_of(admin_client).execute("SELECT * FROM addbook_draft WHERE uid = 1").fetchone()
    assert (row["bname"], row["tid"], row["stock"], row["price_cents"], len(row["cont"])) == ("测试书", 1, 10, 2550, 4000)
    with admin_client.session_transaction("/BookShop/") as s:
        assert not {"bname", "publishers", "cont", "stock", "price", "tname", "tid"} & set(s)


@pytest.mark.parametrize("field,value", [("price", "25.555"), ("tid", "99"), ("stock", "-1"), ("bname", "")])
def test_step1_invalid(admin_client, field, value):
    r = post(admin_client, STEP1, dict(GOOD, **{field: value}))
    assert alert_of(r) == ("please check book info!", "add.jsp")
    assert conn_of(admin_client).execute("SELECT COUNT(*) FROM addbook_draft").fetchone()[0] == 0


def test_step2_without_draft(admin_client):
    assert alert_of(upload(admin_client, PNG, "a.png")) == ("please fill in book info first!", "add.jsp")


def test_full_add_with_png(admin_client, client):
    before = covers_of(admin_client)
    post(admin_client, STEP1, GOOD)
    r = upload(admin_client, PNG, "封面.PNG")
    assert r.status_code == 302 and r.headers["Location"] == "admin.action?opttype=queryAllbooks"
    c = conn_of(admin_client)
    book = c.execute("SELECT * FROM book WHERE bid = 12").fetchone()
    assert book["bname"] == "测试书" and book["on_sale"] == 1 and book["price_cents"] == 2550
    assert re.fullmatch(r"[0-9a-f]{32}\.png", book["url"])
    assert set(covers_of(admin_client)) - set(before) == {book["url"]}
    assert c.execute("SELECT COUNT(*) FROM addbook_draft").fetchone()[0] == 0
    pub = client.get("/BookShop/img/" + book["url"])
    assert pub.status_code == 200 and pub.mimetype == "image/png"


def test_jpeg_gets_jpg_extension(admin_client):
    post(admin_client, STEP1, GOOD)
    assert upload(admin_client, JPEG, "photo.JPEG").status_code == 302
    url = conn_of(admin_client).execute("SELECT url FROM book WHERE bid = 12").fetchone()[0]
    assert re.fullmatch(r"[0-9a-f]{32}\.jpg", url)


@pytest.mark.parametrize("content,filename", [(b"GIF89a" + b"\x00" * 32, "a.jpg"), (b"", ""), (b"hello", "a.png")])
def test_step2_rejects_non_image(admin_client, content, filename):
    post(admin_client, STEP1, GOOD)
    before = covers_of(admin_client)
    assert alert_of(upload(admin_client, content, filename)) == ("please upload a png or jpg image!", "addnext.jsp")
    assert covers_of(admin_client) == before
    c = conn_of(admin_client)
    assert c.execute("SELECT COUNT(*) FROM book").fetchone()[0] == 10
    assert c.execute("SELECT COUNT(*) FROM addbook_draft").fetchone()[0] == 1


def test_transaction_failure_cleans_file(admin_client, monkeypatch):
    import bookshop_web.views.admin_books as admin_books

    post(admin_client, STEP1, GOOD)
    before = covers_of(admin_client)
    monkeypatch.setattr(admin_books, "INSERT_BOOK", "INSERT INTO no_such_table VALUES (?, ?, ?, ?, ?, ?, ?)")
    r = upload(admin_client, PNG, "a.png")
    assert r.status_code == 500
    assert covers_of(admin_client) == before
    assert conn_of(admin_client).execute("SELECT COUNT(*) FROM addbook_draft").fetchone()[0] == 1


def test_client_filename_never_used(admin_client):
    post(admin_client, STEP1, GOOD)
    assert upload(admin_client, PNG, "..\\..\\evil.png").status_code == 302
    assert not [n for n in covers_of(admin_client) if "evil" in n]

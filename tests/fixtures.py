"""所有业务测试仅使用临时 SQLite 与上传目录。"""
import secrets
import logging
import sqlite3
import tempfile
import unittest
from pathlib import Path
from html.parser import HTMLParser


class TokenParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.token = None

    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        if tag == "input" and fields.get("name") == "csrf_token":
            self.token = fields.get("value")

class BookShopCase(unittest.TestCase):
    def setUp(self):
        from bookshop_app import create_app
        from bookshop_app.db import init_db
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(logging.shutdown)
        self.root = Path(self.temp.name)
        self.database = self.root / "bookshop.db"
        self.uploads = self.root / "uploads"
        self.app = create_app({
            "TESTING": True, "PROPAGATE_EXCEPTIONS": False,
            "DATABASE_PATH": str(self.database), "UPLOAD_DIR": str(self.uploads),
            "SECRET_KEY": secrets.token_hex(32),
        })
        init_db(self.database)
        self.client = self.app.test_client()

    def connect(self):
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def post_form(self, action, data=None, page="/BookShop/login.jsp"):
        response = self.client.get(page)
        self.assertEqual(response.status_code, 200)
        parser = TokenParser()
        parser.feed(response.get_data(as_text=True))
        self.assertTrue(parser.token, "状态变更表单必须提供 CSRF token")
        return self.client.post(action, data={**(data or {}), "csrf_token": parser.token})

    def register_and_login(self, name="测试用户"):
        registered = self.post_form(
            "/BookShop/login.action?opttype=addusers",
            {"inputUname": name, "inputPassword": "abc12345", "checkPassword": "abc12345"},
            page="/BookShop/register.jsp")
        self.assertEqual(registered.status_code, 302)
        response = self.post_form(
            "/BookShop/login.action?opttype=checkUsers",
            {"inputName": name, "inputPassword": "abc12345"})
        self.assertEqual(response.status_code, 302)

    def seed_catalog(self):
        """GOLD-014～020：两本同名书、重复标签和一本零销量书。"""
        with self.connect() as db:
            db.executemany("INSERT INTO tag(tid,tname) VALUES (?,?)",
                           [(1, "文学"), (2, "文学"), (3, "科技")])
            db.executemany(
                "INSERT INTO book(bid,bname,publishers,stock,price_cents,tid,url,cont) VALUES (?,?,?,?,?,?,?,?)",
                [(11, "同名书", "甲", 5, 1200, 1, "a.png", "甲简介"),
                 (12, "同名书", "乙", 8, 2300, 2, "b.png", "乙简介"),
                 (13, "零销量", "丙", 3, 3400, 3, "c.png", "丙简介")])
            db.executemany("INSERT INTO user(uid,uname,password_hash,role) VALUES (?,?,?,?)",
                           [(1, "甲用户", "test-hash", 1), (2, "乙用户", "test-hash", 1)])
            db.executemany("INSERT INTO customer(uid) VALUES (?)", [(1,), (2,)])
            db.executemany("INSERT INTO orders(oid,bid,uid) VALUES (?,?,?)",
                           [(1, 11, 1), (2, 11, 1), (3, 12, 2)])

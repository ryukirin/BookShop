"""TEST-008：UTF-8、SQL 输入与弱密钥。"""
import tempfile
from pathlib import Path
from tests.fixtures import BookShopCase

class IdentityInputTests(BookShopCase):
    def test_chinese_and_supplementary_character_roundtrip(self):
        name = "中文📚用户"
        response = self.post_form("/BookShop/login.action?opttype=addusers",
            data={"inputUname": name, "inputPassword": "abc12345", "checkPassword": "abc12345"},
            page="/BookShop/register.jsp")
        self.assertEqual(response.status_code, 302)
        with self.connect() as db:
            self.assertEqual(db.execute("SELECT uname FROM user").fetchone()[0], name)

    def test_weak_or_placeholder_secret_rejected(self):
        from bookshop_app import create_app
        with tempfile.TemporaryDirectory() as temp:
            for secret in ("", "x" * 31, "CHANGE_ME" * 8):
                with self.subTest(secret=secret), self.assertRaises(ValueError):
                    create_app({"DATABASE_PATH": str(Path(temp) / "db.sqlite"),
                                "UPLOAD_DIR": str(Path(temp) / "uploads"), "SECRET_KEY": secret})

class AdministrationInputTests(BookShopCase):
    def test_injection_string_does_not_change_data(self):
        self.seed_catalog()
        # 夹具已有 uid=1／2，注册分配新键，不与历史订单归属混淆。
        self.register_and_login("搜索测试用户")
        response = self.client.get(
            "/BookShop/jsp/book.action?opttype=queryByname&bname=%27%20OR%201%3D1--")
        self.assertEqual(response.status_code, 302)
        with self.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM book").fetchone()[0], 3)

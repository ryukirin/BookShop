"""TEST-006：GOLD-002／004 核心注册分支。"""
from tests.fixtures import BookShopCase

class AuthFlowTests(BookShopCase):
    def test_password_mismatch_does_not_write(self):
        response = self.post_form("/BookShop/login.action?opttype=addusers",
            data={"inputUname": "新用户", "inputPassword": "abc12345", "checkPassword": "different"},
            page="/BookShop/register.jsp")
        self.assertEqual(response.status_code, 200)
        self.assertIn("please check password!", response.get_data(as_text=True))
        with self.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM user").fetchone()[0], 0)

    def test_registration_stores_hash_and_redirects(self):
        response = self.post_form("/BookShop/login.action?opttype=addusers",
            data={"inputUname": "新用户", "inputPassword": "abc12345", "checkPassword": "abc12345"},
            page="/BookShop/register.jsp")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/BookShop/login.jsp")
        with self.connect() as db:
            row = db.execute("SELECT uid,password_hash,role FROM user WHERE uname='新用户'").fetchone()
            self.assertIsNotNone(row)
            self.assertNotEqual(row["password_hash"], "abc12345")
            self.assertEqual(row["role"], 1)
            self.assertIsNotNone(db.execute("SELECT uid FROM customer WHERE uid=?", (row["uid"],)).fetchone())

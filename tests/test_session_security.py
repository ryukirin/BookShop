"""TEST-007：服务端 Session 与危险 GET。"""
from tests.fixtures import BookShopCase

class SessionSecurityTests(BookShopCase):
    def test_cookie_has_no_identity_and_server_has_session(self):
        self.post_form("/BookShop/login.action?opttype=addusers",
            data={"inputUname": "cookie-user", "inputPassword": "abc12345", "checkPassword": "abc12345"},
            page="/BookShop/register.jsp")
        response = self.post_form("/BookShop/login.action?opttype=checkUsers",
            data={"inputName": "cookie-user", "inputPassword": "abc12345"})
        self.assertEqual(response.status_code, 302)
        cookie = " ".join(response.headers.getlist("Set-Cookie"))
        self.assertNotIn("cookie-user", cookie)
        self.assertIn("HttpOnly", cookie)
        self.assertIn("SameSite=Lax", cookie)
        with self.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM http_session").fetchone()[0], 1)

    def test_get_cannot_change_password(self):
        self.register_and_login()
        response = self.client.get(
            "/BookShop/jsp/my.action?opttype=updatePwd&oldpwd=a&newpwd=b&anewpwd=b")
        self.assertIn(response.status_code, (401, 403, 405))

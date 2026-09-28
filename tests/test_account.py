"""TEST-011：GOLD-008／013 个人中心边界。"""
from tests.fixtures import BookShopCase

class AccountTests(BookShopCase):
    def test_unauthenticated_account_denied(self):
        response = self.client.get("/BookShop/jsp/my.action?opttype=initMypage")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/BookShop/login.jsp")

    def test_missing_password_fields_is_400(self):
        self.register_and_login()
        response = self.post_form("/BookShop/jsp/my.action?opttype=updatePwd",
                                  page="/BookShop/jsp/changepwd.jsp")
        self.assertEqual(response.status_code, 400)

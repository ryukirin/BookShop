"""TEST-002：冻结路由、参数、状态与安全方法的目标预言机。"""

import secrets
import logging
import re
import tempfile
import unittest
from pathlib import Path
from tests.fixtures import BookShopCase


PREFIX = "/BookShop"


def make_client(root: Path):
    # 保持导入在夹具内，使缺失应用骨架能够产生真实红灯。
    from bookshop_app import create_app

    app = create_app(
        {
            "TESTING": True,
            "DATABASE_PATH": str(root / "bookshop.db"),
            "UPLOAD_DIR": str(root / "uploads"),
            "SECRET_KEY": secrets.token_hex(32),
            "PROPAGATE_EXCEPTIONS": False,
        }
    )
    return app, app.test_client()


class FoundationRouteTests(unittest.TestCase):
    """BATCH-001 子集：只检验运行骨架，不冒充业务入口已完成。"""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(logging.shutdown)
        self.app, self.client = make_client(Path(self.temp.name))

    def test_health_only_under_bookshop_prefix(self):
        response = self.client.get(f"{PREFIX}/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), "ok")
        self.assertEqual(self.client.get("/health").status_code, 404)

    def test_registered_operations_exactly_match_four_active_servlets(self):
        from bookshop_app.routes import OPERATIONS
        root = Path(__file__).resolve().parents[1]
        sources = {}
        for name in ("LoginServlet", "BookServlet", "MyServlet", "AdminServlet"):
            # 旧源码存在混合编码；此处只提取 ASCII 路由／case，逐字节映射不改源文件。
            text = (root / "BookShop" / "src" / "controller" / (name + ".java")).read_text(encoding="latin-1")
            route = re.search(r'@WebServlet\("/([^"]+)"\)', text).group(1)
            sources[route] = set(re.findall(r'case "([^"]+)"', text))
        self.assertEqual({path: set(operations) for path, operations in OPERATIONS.items()}, sources)

    def test_missing_or_unknown_operation_is_parameter_error(self):
        for route in ("login.action", "jsp/book.action", "jsp/my.action", "jsp/admin.action"):
            for query in ("", "?opttype=not-a-legacy-operation"):
                with self.subTest(route=route, query=query):
                    response = self.client.get(f"{PREFIX}/{route}{query}")
                    self.assertEqual(response.status_code, 400)
                    self.assertIn("参数", response.get_data(as_text=True))

    def test_unknown_page_is_404_with_chinese_message(self):
        response = self.client.get(f"{PREFIX}/jsp/not-found.jsp")
        self.assertEqual(response.status_code, 404)
        self.assertIn("不存在", response.get_data(as_text=True))

    def test_internal_error_is_500_without_traceback(self):
        def raise_error():
            raise RuntimeError("private diagnostic marker")

        self.app.add_url_rule(f"{PREFIX}/__test_error", "__test_error", raise_error)
        response = self.client.get(f"{PREFIX}/__test_error")
        self.assertEqual(response.status_code, 500)
        body = response.get_data(as_text=True)
        self.assertIn("错误", body)
        self.assertNotIn("private diagnostic marker", body)
        self.assertNotIn("Traceback", body)


class IdentityRouteTests(BookShopCase):
    """GOLD-001～013 路由形状；具体数据与 Session 断言见 TEST-006／011。"""

    def test_active_identity_pages_and_missing_parameters(self):
        for page in ("login.jsp", "register.jsp"):
            with self.subTest(page=page):
                self.assertEqual(self.client.get(f"{PREFIX}/{page}").status_code, 200)
        for action in ("addusers", "checkUsers"):
            with self.subTest(action=action):
                page = "register.jsp" if action == "addusers" else "login.jsp"
                response = self.post_form(f"{PREFIX}/login.action?opttype={action}",
                                          page=f"{PREFIX}/{page}")
                self.assertEqual(response.status_code, 400)

    def test_dangerous_password_change_get_does_not_write(self):
        self.register_and_login()
        response = self.client.get(f"{PREFIX}/jsp/my.action?opttype=updatePwd")
        self.assertIn(response.status_code, (401, 403, 405))


class CatalogRouteTests(BookShopCase):
    """GOLD-014／015／019 对应入口及缺参语义。"""

    def setUp(self):
        super().setUp()
        self.register_and_login()

    def test_catalog_legacy_paths_and_required_parameters(self):
        self.assertEqual(self.client.get(f"{PREFIX}/index.jsp").status_code, 200)
        self.assertEqual(
            self.client.get(f"{PREFIX}/jsp/book.action?opttype=queryAllbook").status_code, 302
        )
        for operation in ("queryByname", "queryBytag", "bookDetail"):
            with self.subTest(operation=operation):
                response = self.client.get(f"{PREFIX}/jsp/book.action?opttype={operation}")
                self.assertEqual(response.status_code, 400)


class PurchaseRouteTests(BookShopCase):
    """旧 GET 购买必须拒绝；有效 POST 的业务结果由 TEST-012 验收。"""

    def setUp(self):
        super().setUp()
        self.register_and_login()

    def test_get_cannot_purchase(self):
        response = self.client.get(f"{PREFIX}/jsp/book.action?opttype=buybook&bid=1")
        self.assertIn(response.status_code, (401, 403, 405))


class AdministrationRouteTests(BookShopCase):
    """管理端活动分支与已排除路由。"""

    def test_anonymous_cannot_read_admin_operations(self):
        for operation in ("queryAllcustomers", "queryCustomers", "queryAllbooks", "queryBooks", "showBooks", "showAllmoney"):
            with self.subTest(operation=operation):
                response = self.client.get(f"{PREFIX}/jsp/admin.action?opttype={operation}")
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.headers["Location"], "/BookShop/login.jsp")

    def test_legacy_write_get_has_no_success_redirect(self):
        for operation in ("deleteCustomers", "addBooks", "addBooksimg", "editBooks", "deleteBooks"):
            with self.subTest(operation=operation):
                response = self.client.get(f"{PREFIX}/jsp/admin.action?opttype={operation}")
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.headers["Location"], "/BookShop/login.jsp")

    def test_excluded_endpoints_are_not_migrated(self):
        for route in ("uploadServlet.do", "downloadServlet.do", "jsp/user.action", "jsp/useredit.jsp"):
            with self.subTest(route=route):
                self.assertEqual(self.client.get(f"{PREFIX}/{route}").status_code, 404)

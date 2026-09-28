"""TEST-015：GOLD-017／018 会员删除保护。"""
from tests.fixtures import BookShopCase

class AdminMemberTests(BookShopCase):
    def test_member_with_orders_is_rejected_without_changes(self):
        from bookshop_app.admin import delete_customer
        self.seed_catalog()
        with self.connect() as db:
            before = tuple(db.execute("SELECT count(*) FROM " + table).fetchone()[0]
                           for table in ("user", "customer", "orders", "book"))
        result = delete_customer(self.database, uid=1, idempotency_key="delete-with-orders")
        self.assertEqual(result.status, 409)
        with self.connect() as db:
            after = tuple(db.execute("SELECT count(*) FROM " + table).fetchone()[0]
                          for table in ("user", "customer", "orders", "book"))
        self.assertEqual(after, before)

    def test_member_without_orders_is_atomically_deleted(self):
        from bookshop_app.admin import delete_customer
        self.seed_catalog()
        with self.connect() as db:
            db.execute("INSERT INTO user(uid,uname,password_hash,role) VALUES (3,'无单','hash',1)")
            db.execute("INSERT INTO customer(uid) VALUES (3)")
        result = delete_customer(self.database, uid=3, idempotency_key="delete-empty")
        self.assertEqual(result.status, 302)
        with self.connect() as db:
            self.assertIsNone(db.execute("SELECT uid FROM user WHERE uid=3").fetchone())
            self.assertIsNone(db.execute("SELECT uid FROM customer WHERE uid=3").fetchone())

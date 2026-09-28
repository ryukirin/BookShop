"""TEST-012：条件扣库存、订单及变更日志原子性。"""
from tests.fixtures import BookShopCase

class PurchaseTests(BookShopCase):
    def test_one_purchase_changes_stock_order_and_log_once(self):
        from bookshop_app.orders import purchase
        self.seed_catalog()
        result = purchase(self.database, uid=1, bid=13, idempotency_key="purchase-001")
        self.assertTrue(result.ok)
        with self.connect() as db:
            self.assertEqual(db.execute("SELECT stock FROM book WHERE bid=13").fetchone()[0], 2)
            self.assertEqual(db.execute("SELECT count(*) FROM orders WHERE bid=13 AND uid=1").fetchone()[0], 1)
            self.assertEqual(db.execute("SELECT count(*) FROM migration_change_log "
                                        "WHERE idempotency_key='purchase-001'").fetchone()[0], 1)

    def test_zero_stock_rejected_without_order(self):
        from bookshop_app.orders import purchase
        self.seed_catalog()
        with self.connect() as db:
            db.execute("UPDATE book SET stock=0 WHERE bid=13")
        result = purchase(self.database, uid=1, bid=13, idempotency_key="purchase-zero")
        self.assertFalse(result.ok)
        with self.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM orders WHERE bid=13").fetchone()[0], 0)
            self.assertEqual(db.execute("SELECT count(*) FROM migration_change_log "
                                        "WHERE idempotency_key='purchase-zero'").fetchone()[0], 0)

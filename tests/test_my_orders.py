"""TEST-013：GOLD-009 本人订单隔离与主键升序。"""
from tests.fixtures import BookShopCase

class MyOrdersTests(BookShopCase):
    def test_only_current_user_orders_are_returned(self):
        from bookshop_app.orders import list_user_orders
        self.seed_catalog()
        with self.connect() as db:
            own = list_user_orders(db, uid=1)
        self.assertEqual([row["oid"] for row in own], [1, 2])
        self.assertTrue(all(row["uid"] == 1 for row in own))

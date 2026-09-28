"""TEST-014：GOLD-016 管理列表和两位金额。"""
from tests.fixtures import BookShopCase

class AdminReadTests(BookShopCase):
    def test_duplicate_books_not_merged_in_admin_list(self):
        from bookshop_app.admin import list_admin_books
        self.seed_catalog()
        with self.connect() as db:
            rows = list_admin_books(db)
        self.assertEqual([(r["bid"], r["stock"], r["price_cents"], r["sales"]) for r in rows],
                         [(11, 5, 1200, 2), (12, 8, 2300, 1), (13, 3, 3400, 0)])

    def test_money_is_integer_cents_and_formatted(self):
        from bookshop_app.admin import account_summary
        self.seed_catalog()
        with self.connect() as db:
            summary = account_summary(db)
        self.assertEqual(summary.total_cents, 4700)
        self.assertEqual(summary.display_total, "47.00")

"""TEST-016：管理 CRUD 与 GOLD-020 最大 tid。"""
from tests.fixtures import BookShopCase

class CoreCrudTests(BookShopCase):
    def test_edit_only_three_fields_of_one_bid(self):
        from bookshop_app.admin import edit_book
        self.seed_catalog()
        edit_book(self.database, bid=12, publishers="新出版社", stock=4,
                  price_cents=2500, idempotency_key="edit-12")
        with self.connect() as db:
            row = db.execute("SELECT * FROM book WHERE bid=12").fetchone()
            self.assertEqual((row["bname"], row["url"], row["tid"]), ("同名书", "b.png", 2))
            self.assertEqual((row["publishers"], row["stock"], row["price_cents"]),
                             ("新出版社", 4, 2500))
            self.assertEqual(db.execute("SELECT stock FROM book WHERE bid=11").fetchone()[0], 5)

class AddBookTests(BookShopCase):
    def test_duplicate_tag_name_chooses_largest_tid(self):
        from bookshop_app.admin import resolve_tag_id
        self.seed_catalog()
        with self.connect() as db:
            self.assertEqual(resolve_tag_id(db, "文学"), 2)
            self.assertEqual(db.execute("SELECT count(*) FROM tag WHERE tname='文学'").fetchone()[0], 2)

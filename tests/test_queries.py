"""TEST-004：逐 bid 身份、重复标签与字面搜索。"""
from tests.fixtures import BookShopCase

class QueryTests(BookShopCase):
    def test_duplicate_books_keep_own_fields_and_sales(self):
        from bookshop_app.catalog import list_books
        self.seed_catalog()
        with self.connect() as db:
            books = list_books(db)
        self.assertEqual(
            [(b["bid"], b["url"], b["price_cents"], b["stock"], b["sales"]) for b in books],
            [(11, "a.png", 1200, 5, 2), (12, "b.png", 2300, 8, 1), (13, "c.png", 3400, 3, 0)])

    def test_duplicate_tag_names_cover_both_ids(self):
        from bookshop_app.catalog import list_tags, list_books
        self.seed_catalog()
        with self.connect() as db:
            self.assertEqual([(t["tid"], t["tname"]) for t in list_tags(db)],
                             [(1, "文学"), (2, "文学"), (3, "科技")])
            self.assertEqual([b["bid"] for b in list_books(db, tag_name="文学")], [11, 12])

    def test_percent_underscore_escape_are_literal(self):
        from bookshop_app.catalog import list_books
        self.seed_catalog()
        with self.connect() as db:
            db.executemany(
                "INSERT INTO book(bname,publishers,stock,price_cents,tid,url,cont) VALUES (?,?,?,?,?,?,?)",
                [(name, "出版社", 1, 100, 3, str(i) + ".png", "简介")
                 for i, name in enumerate(("书%名", "书_名", "书!名", "Python指南", "中文"))])
            for fragment in ("%", "_", "!"):
                with self.subTest(fragment=fragment):
                    self.assertEqual([b["bname"] for b in list_books(db, search=fragment)],
                                     ["书" + fragment + "名"])
            self.assertEqual([b["bname"] for b in list_books(db, search="python指南")],
                             ["Python指南"])

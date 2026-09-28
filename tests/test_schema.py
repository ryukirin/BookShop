"""TEST-003：目标八表约束与 GOLD-014／017／019 数据边界。"""
from tests.fixtures import BookShopCase

class SchemaTests(BookShopCase):
    def test_eight_strict_tables_and_restrict_user_delete(self):
        with self.connect() as db:
            sql = {r["name"]: r["sql"] for r in db.execute(
                "SELECT name,sql FROM sqlite_master WHERE type='table'")}
            for name in ("user", "customer", "tag", "book", "orders",
                         "http_session", "schema_version", "migration_change_log"):
                with self.subTest(table=name):
                    self.assertIn("STRICT", sql[name].upper())
            self.assertEqual(db.execute("PRAGMA foreign_keys").fetchone()[0], 1)
            fk = db.execute("PRAGMA foreign_key_list(orders)").fetchall()
            self.assertTrue(any(r["table"] == "user" and r["on_delete"] == "RESTRICT" for r in fk))

    def test_duplicate_tags_books_and_constraints(self):
        self.seed_catalog()
        with self.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM tag WHERE tname='文学'").fetchone()[0], 2)
            self.assertEqual(db.execute("SELECT count(*) FROM book WHERE bname='同名书'").fetchone()[0], 2)
            for stock, price, tid in ((-1, 100, 1), (1, -1, 1), (1, 100, 999)):
                with self.subTest(stock=stock, price=price, tid=tid):
                    with self.assertRaises(Exception):
                        db.execute("INSERT INTO book(bname,publishers,stock,price_cents,tid,url,cont) "
                                   "VALUES (?,?,?,?,?,?,?)",
                                   ("坏书", "出版社", stock, price, tid, "x.png", "简介"))
            self.assertEqual(db.execute("SELECT count(*) FROM book").fetchone()[0], 3)
            with self.assertRaises(Exception):
                db.execute("DELETE FROM user WHERE uid=1")
            self.assertEqual(db.execute("SELECT count(*) FROM orders WHERE uid=1").fetchone()[0], 2)

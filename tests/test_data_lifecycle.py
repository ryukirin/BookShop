"""TEST-005：初始化、整数分和故障回滚。"""
from tests.fixtures import BookShopCase

class DataLifecycleTests(BookShopCase):
    def test_repeatable_init(self):
        from bookshop_app.db import init_db
        with self.connect() as db:
            before = db.execute("SELECT count(*) FROM schema_version").fetchone()[0]
        init_db(self.database)
        with self.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM schema_version").fetchone()[0], before)

    def test_money_exactness(self):
        from bookshop_app.money import parse_price
        self.assertEqual(parse_price("0.01"), 1)
        self.assertEqual(parse_price("123456.78"), 12345678)
        for value in ("1.001", "-1", "NaN", "Infinity"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_price(value)

    def test_failed_write_rolls_back(self):
        from bookshop_app.db import write_transaction
        with self.assertRaises(RuntimeError):
            with write_transaction(self.database) as db:
                db.execute("INSERT INTO tag(tname) VALUES (?)", ("回滚标签",))
                raise RuntimeError("故障注入")
        with self.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM tag WHERE tname='回滚标签'").fetchone()[0], 0)

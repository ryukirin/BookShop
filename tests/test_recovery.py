"""TEST-019：一致快照与幂等重放分层验收。"""
from tests.fixtures import BookShopCase

class FoundationRecoveryTests(BookShopCase):
    def test_snapshot_restores_demo_rows(self):
        from bookshop_app.recovery import create_snapshot, restore_snapshot
        self.seed_catalog()
        backup = self.root / "backup"
        create_snapshot(self.database, self.uploads, backup)
        restored = self.root / "restored.db"
        restored_uploads = self.root / "restored-uploads"
        restore_snapshot(backup, restored, restored_uploads)
        import sqlite3
        with sqlite3.connect(restored) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM book").fetchone()[0], 3)

class PurchaseRecoveryTests(BookShopCase):
    def test_committed_purchase_survives_idempotent_replay(self):
        from bookshop_app.orders import purchase
        from bookshop_app.recovery import export_changes, replay_changes
        self.seed_catalog()
        purchase(self.database, uid=1, bid=13, idempotency_key="replay-once")
        changes = export_changes(self.database, after_seq=0)
        replay_changes(self.database, changes)
        replay_changes(self.database, changes)
        with self.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM orders WHERE bid=13").fetchone()[0], 1)

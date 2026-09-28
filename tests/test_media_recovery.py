"""TEST-018：已提交图片可从数据库副本恢复。"""
import hashlib
from tests.fixtures import BookShopCase

class MediaRecoveryTests(BookShopCase):
    def test_missing_committed_file_rebuilt_from_media_bytes(self):
        from bookshop_app.media import reconcile_uploads
        self.seed_catalog()
        payload = b"\x89PNG\r\n\x1a\n" + b"fixture"
        digest = hashlib.sha256(payload).hexdigest()
        with self.connect() as db:
            db.execute("INSERT INTO migration_change_log(event_type,business_key,payload_json,"
                       "committed_at,idempotency_key,media_id,media_sha256,media_bytes) "
                       "VALUES (?,?,?,?,?,?,?,?)",
                       ("upload", "13", "{}", "2026-09-27T00:00:00Z", "media-13",
                        "c.png", digest, payload))
        reconcile_uploads(self.database, self.uploads)
        self.assertEqual(hashlib.sha256((self.uploads / "c.png").read_bytes()).hexdigest(), digest)

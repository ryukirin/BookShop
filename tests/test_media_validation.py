"""TEST-017：真实图片、大小限制与路径隔离。"""
import io
from tests.fixtures import BookShopCase

class MediaValidationTests(BookShopCase):
    def test_false_extension_and_empty_data_rejected(self):
        from bookshop_app.media import validate_upload
        for name, data in (("fake.png", b"not an image"), ("empty.jpg", b"")):
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate_upload(name, io.BytesIO(data))

    def test_traversal_name_rejected(self):
        from bookshop_app.media import validate_upload
        with self.assertRaises(ValueError):
            validate_upload("../escape.png", io.BytesIO(b"\x89PNG\r\n\x1a\n"))

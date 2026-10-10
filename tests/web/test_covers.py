"""TEST-029（测试客户端部分）：封面输出与公开图片（REQ-CATALOG-007、REQ-CATALOG-008、LEGACY-004、LEGACY-018、LEGACY-053、LEGACY-069、EXP-007）。"""
import pytest

SHOWPIC = "/BookShop/jsp/showpic.jsp?img="
COVERS = ["b1.jpg", "b2.jpg", "b3.jpg", "b4.jpg", "b5.jpg", "b6.jpg", "b7.jpg", "b8.jpg", "b9.jpg", "b11.jpg"]


@pytest.mark.batch(4)
@pytest.mark.parametrize("name", COVERS)
def test_all_seed_covers(member_client, name):
    r = member_client.get(SHOWPIC + name)
    assert r.status_code == 200
    assert r.mimetype == ("image/png" if name in ("b6.jpg", "b8.jpg") else "image/jpeg")


@pytest.mark.batch(4)
@pytest.mark.parametrize("name", ["../bookshop.db", "..%2Fbookshop.db", "nope.jpg", "a b.jpg", "bookshop.db",
                                  "b1.gif", "", "b1.jpg/..", "%2e%2e%2fbookshop.db", "x" * 65 + ".jpg"])
def test_bad_names_404(member_client, name):
    assert member_client.get(SHOWPIC + "b1.jpg").status_code == 200  # 先确认端点可用，避免空过
    assert member_client.get(SHOWPIC + name).status_code == 404


@pytest.mark.batch(4)
def test_whitelisted_name_but_not_image(member_client):
    covers = member_client.application.config["BOOKSHOP"].data_dir / "covers"
    (covers / "fake.jpg").write_bytes(b"GIF89a....")
    assert member_client.get(SHOWPIC + "b1.jpg").status_code == 200
    assert member_client.get(SHOWPIC + "fake.jpg").status_code == 404


@pytest.mark.batch(4)
def test_showpic_requires_login(sclient):
    r = sclient.get(SHOWPIC + "b1.jpg")
    assert r.status_code == 302 and r.headers["Location"].endswith("/BookShop/login.jsp")


@pytest.mark.batch(4)
@pytest.mark.parametrize("name,mime", [("b1.jpg", "image/jpeg"), ("b8.jpg", "image/png")])
def test_public_cover(sclient, name, mime):
    r = sclient.get("/BookShop/img/" + name)
    assert r.status_code == 200 and r.mimetype == mime


@pytest.mark.batch(4)
@pytest.mark.parametrize("name", ["nope.jpg", "bookshop.db", "..%2Fbookshop.db"])
def test_public_img_404(sclient, name):
    assert sclient.get("/BookShop/img/b1.jpg").status_code == 200
    assert sclient.get("/BookShop/img/" + name).status_code == 404


# 轮播图和默认头像由 BATCH-001 的静态路由提供，一直生效。
@pytest.mark.parametrize("name", ["1.jpg", "2.jpg", "default.jpg"])
def test_public_static_images(client, name):
    r = client.get("/BookShop/img/" + name)
    assert r.status_code == 200 and r.mimetype == "image/jpeg"

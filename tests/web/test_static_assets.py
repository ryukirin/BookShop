"""TEST-011：静态资源本地化（REQ-PLATFORM-010、MIG-RULE-011、LEGACY-037、LEGACY-047）。

渲染页面，收集 src/href 引用的资源，再递归解析本地 CSS 里的 url()，逐个请求。
"""
import re
from urllib.parse import urlsplit

import pytest

from tests.conftest import parse, resolve

CSS_URL = re.compile(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)")


def crawl(client, pages):
    seen, fetched = set(), []
    queue = []
    for page in pages:
        r = client.get(page)
        assert r.status_code == 200, page
        doc = parse(r)
        refs = [s.get("href") for s in doc.stylesheets] + [s.get("src") for s in doc.scripts if s.get("src")] \
            + [i.get("src") for i in doc.imgs if i.get("src")]
        for ref in refs:
            assert not re.match(r"^(https?:)?//", ref), f"{page} 引用了外部资源 {ref}"
            assert "jquery" not in ref.lower(), ref
            queue.append(resolve(page, ref))
    while queue:
        url = queue.pop()
        path = urlsplit(url).path
        if url in seen:
            continue
        seen.add(url)
        r = client.get(url)
        assert r.status_code == 200, url
        fetched.append(path)
        if path.endswith(".css"):
            for ref in CSS_URL.findall(r.get_data(as_text=True)):
                if ref.startswith("data:"):
                    continue
                assert not re.match(r"^(https?:)?//", ref), f"{url} 引用了外部资源 {ref}"
                queue.append(resolve(path, ref))
    return fetched


def test_public_pages_assets(client):
    fetched = crawl(client, ["/BookShop/index.jsp", "/BookShop/login.jsp", "/BookShop/register.jsp"])
    assert "/BookShop/bootstrap/css/bootstrap.min.css" in fetched
    assert "/BookShop/bootstrap/js/bootstrap.bundle.min.js" in fetched
    assert "/BookShop/bootstrap-icons/fonts/bootstrap-icons.woff2" in fetched
    assert "/BookShop/img/1.jpg" in fetched


@pytest.mark.batch(4)
def test_member_pages_assets(member_client):
    member_client.get("/BookShop/jsp/book.action?opttype=queryAllbook")
    member_client.get("/BookShop/jsp/book.action?opttype=bookDetail&bid=9")
    crawl(member_client, ["/BookShop/jsp/buy.jsp", "/BookShop/jsp/bookdetails.jsp", "/BookShop/jsp/my.jsp",
                          "/BookShop/jsp/changepwd.jsp"])


@pytest.mark.batch(5)
def test_myorder_page_assets(member_client):
    crawl(member_client, ["/BookShop/jsp/myorder.jsp"])


@pytest.mark.batch(7)
def test_admin_pages_assets(admin_client):
    admin_client.get("/BookShop/jsp/admin.action?opttype=queryAllcustomers")
    admin_client.get("/BookShop/jsp/admin.action?opttype=queryAllbooks")
    admin_client.get("/BookShop/jsp/admin.action?opttype=showBooks&bid=9")
    crawl(admin_client, ["/BookShop/jsp/admin.jsp", "/BookShop/jsp/bookadmin.jsp", "/BookShop/jsp/add.jsp",
                         "/BookShop/jsp/addnext.jsp", "/BookShop/jsp/editbook.jsp", "/BookShop/jsp/oderadmin.jsp"])

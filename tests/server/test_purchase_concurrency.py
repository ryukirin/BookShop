"""TEST-031：真实 waitress 上的并发购买（REQ-ORDER-001、LEGACY-040、EXP-013）。"""
import http.client
import re
import threading
from urllib.parse import urlencode

import pytest

from tests.conftest import db, make_member

pytestmark = [pytest.mark.server, pytest.mark.batch(5)]
TOKEN = re.compile(r'name="csrf_token" value="([^"]+)"')


def http_login(port):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=30)
    conn.request("GET", "/BookShop/login.jsp")
    r = conn.getresponse()
    html = r.read().decode("utf-8")
    cookie = r.getheader("Set-Cookie").split(";", 1)[0]
    body = urlencode({"csrf_token": TOKEN.search(html).group(1), "inputName": "zhangsan", "inputPassword": "abc123"})
    conn.request("POST", "/BookShop/login.action?opttype=checkUsers", body=body,
                 headers={"Content-Type": "application/x-www-form-urlencoded", "Cookie": cookie})
    r = conn.getresponse()
    r.read()
    assert r.status == 302
    cookie = r.getheader("Set-Cookie").split(";", 1)[0]
    conn.request("GET", "/BookShop/jsp/changepwd.jsp", headers={"Cookie": cookie})
    r = conn.getresponse()
    token = TOKEN.search(r.read().decode("utf-8")).group(1)
    return conn, cookie, token


def test_twenty_buyers_five_copies(seeded_app, live_seeded):
    make_member(seeded_app)
    c = db(seeded_app.config["BOOKSHOP"].data_dir)
    c.execute("UPDATE book SET stock = 5 WHERE bid = 9")
    port = live_seeded.effective_port
    sessions = [http_login(port) for _ in range(20)]
    results, barrier = [], threading.Barrier(20)

    def buy(conn, cookie, token):
        barrier.wait()
        conn.request("POST", "/BookShop/jsp/book.action?opttype=buybook", body=urlencode({"csrf_token": token, "bid": "9"}),
                     headers={"Content-Type": "application/x-www-form-urlencoded", "Cookie": cookie})
        r = conn.getresponse()
        results.append((r.status, r.read().decode("utf-8")))
        conn.close()

    threads = [threading.Thread(target=buy, args=s) for s in sessions]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert sum(1 for s, _ in results if s == 302) == 5, results
    assert sum(1 for _, b in results if "out of stock!" in b) == 15
    assert not [s for s, _ in results if s >= 500]
    assert c.execute("SELECT stock FROM book WHERE bid = 9").fetchone()[0] == 0
    assert c.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 5

"""TEST-020（并发部分）：真实 waitress 上同时注册同一用户名（REQ-ACCOUNT-001、EXP-013）。"""
import http.client
import re
import threading

import pytest

pytestmark = [pytest.mark.server, pytest.mark.batch(3)]
TOKEN = re.compile(r'name="csrf_token" value="([^"]+)"')


def register_once(port, name, results, barrier):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=30)
    conn.request("GET", "/BookShop/register.jsp")
    r = conn.getresponse()
    html = r.read().decode("utf-8")
    cookie = r.getheader("Set-Cookie").split(";", 1)[0]
    token = TOKEN.search(html).group(1)
    from urllib.parse import urlencode

    body = urlencode({"csrf_token": token, "inputUname": name, "inputPassword": "abc123", "checkPassword": "abc123"})
    barrier.wait()
    conn.request("POST", "/BookShop/login.action?opttype=addusers", body=body,
                 headers={"Content-Type": "application/x-www-form-urlencoded", "Cookie": cookie})
    r = conn.getresponse()
    results.append((r.status, r.read().decode("utf-8")))
    conn.close()


def test_concurrent_same_name(live_seeded):
    names = ["zhangsan", "ZhangSan", "ZHANGSAN", "zhangSan", "Zhangsan", "zhangsan", "ZHANGsan", "zhangsaN", "zhangsan", "ZhAnGsAn"]
    results, barrier = [], threading.Barrier(len(names))
    threads = [threading.Thread(target=register_once, args=(live_seeded.effective_port, n, results, barrier)) for n in names]
    [t.start() for t in threads]
    [t.join() for t in threads]
    ok = [r for r in results if r[0] == 302]
    taken = [r for r in results if "please change uer name!" in r[1]]
    assert len(ok) == 1 and len(taken) == 9, results

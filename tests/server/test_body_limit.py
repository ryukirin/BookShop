"""TEST-014（真实 waitress 部分）：两层请求体上限（REQ-PLATFORM-014、EXP-012）。"""
import http.client
import socket

import pytest

from tests.conftest import csrf

pytestmark = pytest.mark.server


def status_line(raw):
    return raw.split(b"\r\n", 1)[0]


def test_between_limits_app_413(live, app):
    """5.5 MiB：越过 Flask 的 5 MiB，没到 waitress 的 6 MiB，由应用返回 413 错误页。"""
    body = b"inputName=" + b"x" * int(5.5 * 1024 * 1024)
    conn = http.client.HTTPConnection("127.0.0.1", live.effective_port, timeout=30)
    conn.request("POST", "/BookShop/login.action?opttype=checkUsers", body=body,
                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    r = conn.getresponse()
    data = r.read().decode("utf-8")
    conn.close()
    assert r.status == 413 and "请求内容过大" in data


def test_declared_huge_rejected_without_reading(live):
    s = socket.create_connection(("127.0.0.1", live.effective_port), timeout=10)
    s.sendall(b"POST /BookShop/login.action?opttype=checkUsers HTTP/1.1\r\nHost: x\r\n"
              b"Content-Type: application/octet-stream\r\nContent-Length: 104857600\r\n\r\n" + b"0" * 1024)
    raw = s.recv(4096)
    s.close()
    assert status_line(raw).startswith(b"HTTP/1.1 413")


def test_chunked_over_6mib_rejected(live):
    s = socket.create_connection(("127.0.0.1", live.effective_port), timeout=10)
    s.sendall(b"POST /BookShop/login.action?opttype=checkUsers HTTP/1.1\r\nHost: x\r\n"
              b"Content-Type: application/octet-stream\r\nTransfer-Encoding: chunked\r\n\r\n")
    chunk = b"0" * (512 * 1024)
    sent, raw = 0, b""
    s.settimeout(0.2)
    while sent < 16 * 1024 * 1024 and not raw:
        try:
            s.sendall(b"%x\r\n" % len(chunk) + chunk + b"\r\n")
            sent += len(chunk)
            raw = s.recv(4096)
        except socket.timeout:
            continue
        except OSError:
            break
    s.settimeout(5)
    if not raw:
        try:
            raw = s.recv(4096)
        except OSError:
            pass
    s.close()
    assert status_line(raw).startswith(b"HTTP/1.1 413"), raw[:80]
    assert sent <= 6 * 1024 * 1024 + 2 * len(chunk)

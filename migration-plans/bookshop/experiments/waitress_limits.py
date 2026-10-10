"""EXP-012：在真实的 waitress 上验证请求体上限、应用 413、相对 302 和封面类型。"""
import http.client
import socket
import sys
import threading
import time
from pathlib import Path

from flask import Flask, redirect, request, send_file
from waitress.server import create_server

COVERS = Path(__file__).resolve().parents[3] / "BookShop" / "WebContent" / "img"
APP_LIMIT = 5 * 1024 * 1024
SERVER_LIMIT = 6 * 1024 * 1024

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = APP_LIMIT


@app.errorhandler(413)
def too_large(_):
    return "APP-413", 413


@app.post("/BookShop/jsp/admin.action")
def upload():
    request.files.get("file")
    return "ok"


@app.get("/BookShop/jsp/book.action")
def book_action():
    return redirect("buy.jsp")


@app.get("/BookShop/jsp/showpic.jsp")
def showpic():
    path = COVERS / request.args["img"]
    head = path.read_bytes()[:8]
    return send_file(path, mimetype="image/png" if head.startswith(b"\x89PNG") else "image/jpeg")


RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))


def multipart(size):
    b = "b0undary"
    head = f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="a.jpg"\r\nContent-Type: image/jpeg\r\n\r\n'.encode()
    return head + b"\xff\xd8\xff" + b"0" * size + f"\r\n--{b}--\r\n".encode(), f"multipart/form-data; boundary={b}"


def status_line(raw):
    return raw.split(b"\r\n", 1)[0].decode("latin-1")


srv = create_server(app, host="127.0.0.1", port=0, threads=4, max_request_body_size=SERVER_LIMIT)
port = srv.effective_port
threading.Thread(target=srv.run, daemon=True).start()
try:
    body, ctype = multipart(int(5.5 * 1024 * 1024))
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=30)
    conn.request("POST", "/BookShop/jsp/admin.action?opttype=addBooksimg", body=body, headers={"Content-Type": ctype})
    r = conn.getresponse()
    data = r.read()
    conn.close()
    check("5.5 MiB 的上传（两道上限之间）由应用返回 413", r.status == 413 and data == b"APP-413", f"{r.status} {data[:16]!r}")

    s = socket.create_connection(("127.0.0.1", port), timeout=10)
    t0 = time.perf_counter()
    s.sendall(b"POST /BookShop/jsp/admin.action?opttype=addBooksimg HTTP/1.1\r\nHost: x\r\n"
              b"Content-Type: application/octet-stream\r\nContent-Length: 104857600\r\n\r\n" + b"0" * 1024)
    raw = s.recv(4096)
    ms = (time.perf_counter() - t0) * 1000
    s.close()
    check("声明 100 MiB 的请求，只发 1 KiB 后 waitress 就直接返回 413，不等收完", raw.startswith(b"HTTP/1.1 413"), f"{status_line(raw)}，{ms:.0f} ms")

    s = socket.create_connection(("127.0.0.1", port), timeout=10)
    s.sendall(b"POST /BookShop/jsp/admin.action?opttype=addBooksimg HTTP/1.1\r\nHost: x\r\n"
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
    check("不带 Content-Length 的分块上传，超过 6 MiB 后被 waitress 以 413 拒绝", raw.startswith(b"HTTP/1.1 413") and sent <= SERVER_LIMIT + 2 * len(chunk), f"{status_line(raw) if raw else '无响应'}，已发送 {sent // 1024} KiB")

    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    conn.request("GET", "/BookShop/jsp/book.action?opttype=queryAllbook")
    r = conn.getresponse()
    r.read()
    conn.close()
    check("302 的 Location 保持相对路径 buy.jsp，浏览器会解析为 /BookShop/jsp/buy.jsp", r.status == 302 and r.getheader("Location") == "buy.jsp", f"{r.status} Location={r.getheader('Location')}")

    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    conn.request("GET", "/BookShop/jsp/showpic.jsp?img=b6.jpg")
    r = conn.getresponse()
    r.read()
    conn.close()
    check("经 waitress 输出 b6.jpg 时 Content-Type 为 image/png", r.status == 200 and r.getheader("Content-Type") == "image/png", r.getheader("Content-Type"))
finally:
    srv.close()

failed = 0
for name, ok, detail in RESULTS:
    failed += not ok
    print(("PASS " if ok else "FAIL ") + "EXP-012 " + name + (f"  [{detail}]" if detail else ""))
sys.exit(1 if failed else 0)

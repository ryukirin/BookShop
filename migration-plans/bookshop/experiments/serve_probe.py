"""EXP-009：waitress 在 Windows 上起服务，用真实 HTTP 请求访问旧 URL。"""
import threading, urllib.request, urllib.error, sys
from flask import Flask
from waitress.server import create_server

app = Flask(__name__)

@app.get("/BookShop/login.jsp")
def login_page():
    return "<h2>请登录</h2>"

srv = create_server(app, host="127.0.0.1", port=0, threads=4)
port = srv.effective_port
t = threading.Thread(target=srv.run, daemon=True); t.start()
try:
    r = urllib.request.urlopen(f"http://127.0.0.1:{port}/BookShop/login.jsp", timeout=5)
    body = r.read().decode("utf-8")
    ok1 = r.status == 200 and "请登录" in body and "charset=utf-8" in r.headers["Content-Type"]
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/BookShop/uploadServlet.do", timeout=5); ok2 = False
    except urllib.error.HTTPError as e:
        ok2 = e.code == 404
    print("PASS" if ok1 else "FAIL", "EXP-009 waitress 3.0.2 在 Windows 上返回 UTF-8 中文页面", r.headers["Content-Type"], r.headers.get("Server"))
    print("PASS" if ok2 else "FAIL", "EXP-009 未迁移的 /BookShop/uploadServlet.do 返回 404")
    sys.exit(0 if ok1 and ok2 else 1)
finally:
    srv.close()

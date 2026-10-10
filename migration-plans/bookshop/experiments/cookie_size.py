"""EXP-011：用 Flask 真实的会话序列化，测签名 Cookie 在最坏情况下的大小。"""
import random
import secrets
import sys
import time

from flask import Flask, session

app = Flask(__name__)
app.config.update(SECRET_KEY=secrets.token_hex(32), SESSION_COOKIE_SAMESITE="Lax")
rng = random.Random(0)
PAYLOAD = {}
LIMIT = 4093  # Flask MAX_COOKIE_SIZE 的默认告警阈值，接近浏览器单个 Cookie 的上限
BUDGET = 3000  # 给 Cookie 名和属性留出余量


def cjk(n):
    """随机汉字，几乎无法压缩，代表最坏情况。"""
    return "".join(chr(rng.randint(0x4E00, 0x9FFF)) for _ in range(n))


@app.get("/set")
def set_session():
    session.clear()
    session.update(PAYLOAD)
    session.permanent = True
    return "ok"


def set_cookie_len(payload):
    PAYLOAD.clear()
    PAYLOAD.update(payload)
    return len(app.test_client().get("/set").headers["Set-Cookie"])


base = {"uid": 2**31 - 1, "sv": 2**31 - 1, "login_at": int(time.time()), "csrf": secrets.token_urlsafe(32)}
# 目标设计：会话只存身份、会话版本、登录时间、CSRF 令牌和三个页面的查询条件（书名搜索 ≤100 字，用户名 ≤20 字）
target = dict(base,
              catalogue={"op": "queryByname", "q": cjk(100)},
              admin_books={"op": "queryBooks", "q": cjk(100)},
              admin_customers={"op": "queryCustomers", "q": cjk(20)})
# 旧思路：新增书籍第一步的 6 个字段也放进 Cookie
draft = {"bname": cjk(100), "publishers": cjk(100), "tname": cjk(20), "stock": "999999", "price": "99999.99"}

results = []
n_target = set_cookie_len(target)
results.append((f"目标设计的最坏情况 Set-Cookie 为 {n_target} 字节（预算 {BUDGET}）", n_target <= BUDGET))
for cont in (0, 200, 500, 1000):
    n = set_cookie_len(dict(target, draft=dict(draft, cont=cjk(cont))))
    results.append((f"对照：草稿放进 Cookie，简介 {cont} 字时为 {n} 字节（{'超出' if n > LIMIT else '未超出'} {LIMIT}）", True))

failed = 0
for name, ok in results:
    failed += not ok
    print(("PASS " if ok else "FAIL ") + "EXP-011 " + name)
sys.exit(1 if failed else 0)

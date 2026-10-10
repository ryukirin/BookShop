# 可行性实验脚本

这些脚本是 `migration-strategy.md` 中 EXP-002～EXP-013 的原型。它们只用来验证可行性，不是实现代码；实施时要按 MIG-RULE-023 改写成正式的 TEST。

## 运行环境

需要 Windows 和 Python 3.12.10。本机 PATH 上的 `python` 可能是别的版本，一律通过 `py -3.12` 创建虚拟环境：

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install --require-hashes -r requirements.txt
$env:PYTHONUTF8 = "1"
```

`requirements.txt` 由 `requirements.in` 生成，命令是 `pip-compile --generate-hashes --allow-unsafe --strip-extras`。

## 脚本

| 脚本 | 实验 | 说明 |
|---|---|---|
| `proto.py` | EXP-002～EXP-007 | Flask 测试客户端；SQLite 用临时库；默认读取 `BookShop/WebContent/img` 里的封面 |
| `serve_probe.py` | EXP-009 | 真实的 waitress 服务 |
| `cookie_size.py` | EXP-011 | 会话 Cookie 在最坏情况下的大小 |
| `waitress_limits.py` | EXP-012 | waitress 的请求体上限、应用 413、302 跳转、封面类型 |
| `sqlite_tx.py` | EXP-013 | BEGIN IMMEDIATE、WAL、并发、NOCASE、Windows 上的文件清理 |

运行方式是 `.venv\Scripts\python.exe -I <脚本>`。全部通过时退出码为 0，每一项都会输出 PASS 或 FAIL。

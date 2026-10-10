"""TEST-010（静态部分）：SQL 必须是字面量，不能拼接（REQ-PLATFORM-009、MIG-RULE-002、DEC-006）。

规则：execute/executemany 的第一个参数必须是字符串字面量，或者是模块级常量名，
且这个常量只由字符串字面量（以及其他这类常量）用 + 拼成。f-string、% 格式化、
.format() 和运行期拼接一律不允许。executescript 只允许在 initdb.py 中用来执行 schema.sql。
"""
import ast
from pathlib import Path

# 这是守卫类检查：从 BATCH-002 起一直生效，不需要“先红”。
PKG = Path(__file__).resolve().parents[2] / "bookshop_web"


def literal_constants(tree):
    consts = {}

    def is_lit(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return True
        if isinstance(node, ast.Name) and node.id in consts:
            return True
        return isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add) and is_lit(node.left) and is_lit(node.right)

    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name.isupper() and is_lit(node.value):
                consts[name] = True
    return consts, is_lit


def violations():
    bad = []
    for path in PKG.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        consts, is_lit = literal_constants(tree)
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
                continue
            name = node.func.attr
            if name not in ("execute", "executemany", "executescript") or not node.args:
                continue
            rel = path.relative_to(PKG).as_posix()
            if name == "executescript":
                if rel != "initdb.py":
                    bad.append(f"{rel}:{node.lineno} executescript")
                continue
            if not is_lit(node.args[0]):
                bad.append(f"{rel}:{node.lineno} {ast.unparse(node.args[0])[:60]}")
    return bad


def test_all_sql_is_literal():
    assert violations() == []


def test_scanner_catches_fstring(tmp_path):
    tree = ast.parse("def f(c, x):\n    c.execute(f'SELECT * FROM t WHERE a = {x}')\n")
    consts, is_lit = literal_constants(tree)
    call = next(n for n in ast.walk(tree) if isinstance(n, ast.Call))
    assert not is_lit(call.args[0])

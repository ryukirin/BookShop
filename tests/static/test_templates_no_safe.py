"""TEST-009（静态部分）：模板不得关闭转义（REQ-PLATFORM-008、MIG-RULE-005）。守卫类检查，一直生效。"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_templates_do_not_disable_escaping():
    for p in (ROOT / "bookshop_web" / "templates").glob("*.html"):
        t = p.read_text(encoding="utf-8")
        assert not re.search(r"\|\s*safe\b", t), p.name
        assert "autoescape false" not in t.replace(" ", " "), p.name


def test_python_does_not_build_markup():
    for p in (ROOT / "bookshop_web").rglob("*.py"):
        t = p.read_text(encoding="utf-8")
        assert "Markup(" not in t and "render_template_string" not in t, p.name

"""测试用的 HTML 解析和会话辅助函数。只依赖标准库。"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


@dataclass
class Form:
    attrs: dict
    inputs: list = field(default_factory=list)   # 每项是 input 的属性字典
    selects: dict = field(default_factory=dict)  # name -> [(value, text)]
    textareas: list = field(default_factory=list)
    buttons: list = field(default_factory=list)  # (属性, 文本)

    @property
    def action(self):
        return self.attrs.get("action")

    @property
    def method(self):
        return (self.attrs.get("method") or "get").lower()

    def field_names(self):
        names = [i.get("name") for i in self.inputs if i.get("name")]
        return names + list(self.selects) + [t.get("name") for t in self.textareas]

    def hidden(self):
        return {i["name"]: i.get("value", "") for i in self.inputs if i.get("type") == "hidden" and i.get("name")}

    def input(self, name):
        return next((i for i in self.inputs if i.get("name") == name), None)

    def button_texts(self):
        return [t for _, t in self.buttons]


class Doc(HTMLParser):
    def __init__(self, html: str):
        super().__init__(convert_charrefs=True)
        self.raw = html
        self.title = ""
        self.links: list[tuple[dict, str]] = []
        self.forms: list[Form] = []
        self.imgs: list[dict] = []
        self.scripts: list[dict] = []
        self.stylesheets: list[dict] = []
        self.headings: dict[str, list[str]] = {}
        self.table_headers: list[list[str]] = []
        self.table_rows: list[list[str]] = []
        self.texts: list[str] = []
        self.balance_errors: list[str] = []
        self._stack: list[str] = []
        self._capture: list[list] = []  # [tag, attrs, buf]
        self._form: Form | None = None
        self._ths: list[str] | None = None
        self._row: list[str] | None = None
        self._cell: list[str] | None = None
        self.feed(html)
        self.close()
        if self._stack:
            self.balance_errors.append(f"未闭合的标签：{self._stack}")

    # ---- 解析 ----
    def handle_starttag(self, tag, attrs):
        a = {k: (v if v is not None else "") for k, v in attrs}
        if tag not in VOID:
            self._stack.append(tag)
        if tag in ("title", "a", "button", "h1", "h2", "h3", "h4", "option", "span", "label", "textarea"):
            self._capture.append([tag, a, []])
        if tag == "a":
            pass
        elif tag == "form":
            self._form = Form(a)
            self.forms.append(self._form)
        elif tag == "input" and self._form is not None:
            self._form.inputs.append(a)
        elif tag == "select" and self._form is not None:
            self._form.selects[a.get("name", "")] = []
            self._select = a.get("name", "")
        elif tag == "img":
            self.imgs.append(a)
        elif tag == "script":
            self.scripts.append(a)
        elif tag == "link" and "stylesheet" in a.get("rel", ""):
            self.stylesheets.append(a)
        elif tag == "tr":
            self._row = []
            self._ths = []
        elif tag in ("td", "th"):
            self._cell = []

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag not in VOID:
            if self._stack and self._stack[-1] == tag:
                self._stack.pop()
            else:
                self.balance_errors.append(f"标签不匹配：遇到 </{tag}>，栈顶为 {self._stack[-1:] or '空'}")
                if tag in self._stack:
                    while self._stack and self._stack.pop() != tag:
                        pass
        if self._capture and self._capture[-1][0] == tag:
            t, a, buf = self._capture.pop()
            text = norm("".join(buf))
            for outer in self._capture:
                outer[2].append(text)
            if t == "title":
                self.title = text
            elif t == "a":
                self.links.append((a, text))
            elif t == "button" and self._form is not None:
                self._form.buttons.append((a, text))
            elif t in ("h1", "h2", "h3", "h4"):
                self.headings.setdefault(t, []).append(text)
            elif t == "option" and self._form is not None:
                self._form.selects.setdefault(getattr(self, "_select", ""), []).append((a.get("value", ""), text))
            elif t == "textarea" and self._form is not None:
                self._form.textareas.append(dict(a, text=text))
        if tag == "form":
            self._form = None
        elif tag in ("td", "th") and self._cell is not None and self._row is not None:
            text = norm("".join(self._cell))
            (self._ths if tag == "th" else self._row).append(text)
            self._cell = None
        elif tag == "tr":
            if self._ths:
                self.table_headers.append(self._ths)
            if self._row:
                self.table_rows.append(self._row)
            self._row = self._ths = None

    def handle_data(self, data):
        if self._capture:
            self._capture[-1][2].append(data)
        if self._cell is not None:
            self._cell.append(data)
        if data.strip():
            self.texts.append(norm(data))

    # ---- 查询 ----
    @property
    def text(self):
        return " ".join(self.texts)

    def link_texts(self):
        return [t for _, t in self.links]

    def hrefs(self):
        return [a.get("href") for a, _ in self.links]

    def link(self, text):
        return next((a for a, t in self.links if t == text), None)

    def form(self, *, action_contains=None, name=None):
        for f in self.forms:
            if name is not None and f.attrs.get("name") != name:
                continue
            if action_contains is not None and action_contains not in (f.action or ""):
                continue
            return f
        return None


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def parse(resp_or_html) -> Doc:
    html = resp_or_html if isinstance(resp_or_html, str) else resp_or_html.get_data(as_text=True)
    return Doc(html)


def resolve(page_url: str, href: str) -> str:
    """把页面里的相对链接解析成站内路径（含查询串），便于和基线对照。"""
    u = urlsplit(urljoin("http://t" + page_url, href))
    return u.path + (("?" + u.query) if u.query else "")


ALERT_RE = re.compile(r"^<script>alert\('(?P<text>[^']*)'\); window.location='(?P<loc>[^']*)' </script>$")


def alert_of(resp):
    """解析旧系统风格的 alert 响应，返回 (文案, 跳转目标)；不是 alert 响应时返回 None。"""
    m = ALERT_RE.match(resp.get_data(as_text=True))
    return (m.group("text"), m.group("loc")) if m else None

"""端到端旅程用的小浏览器：只跟随页面上的链接和表单，不直接拼 URL。"""
from __future__ import annotations

from urllib.parse import urlsplit

from tests.helpers import alert_of, parse, resolve


class Browser:
    def __init__(self, client):
        self.client = client
        self.url = None
        self.resp = None
        self.doc = None

    def _land(self, url, resp):
        hops = 0
        while resp.status_code == 302:
            hops += 1
            assert hops < 10
            url = resolve(urlsplit(url).path, resp.headers["Location"])
            resp = self.client.get(url)
        self.url, self.resp = url, resp
        self.doc = parse(resp) if resp.mimetype == "text/html" and alert_of(resp) is None else None
        return resp

    def open(self, url):
        return self._land(url, self.client.get(url))

    def click(self, text, *, index=0):
        hrefs = [a["href"] for a, t in self.doc.links if t == text and a.get("href") is not None]
        assert len(hrefs) > index, f"页面 {self.url} 上没有链接“{text}”"
        return self.open(resolve(urlsplit(self.url).path, hrefs[index]))

    def submit(self, form, values=None, files=None):
        data = {i["name"]: i.get("value", "") for i in form.inputs if i.get("name") and i.get("type") != "file"}
        for name, options in form.selects.items():
            data[name] = options[0][0] if options else ""
        data.update(values or {})
        target = resolve(urlsplit(self.url).path, form.action or "")
        if form.method == "get":
            from urllib.parse import urlencode

            return self.open(urlsplit(target).path + "?" + urlencode(data))
        kw = {}
        if files:
            data.update(files)
            kw["content_type"] = "multipart/form-data"
        resp = self.client.post(target, data=data, **kw)
        if resp.status_code == 302:
            return self._land(target, resp)
        self.resp, self.doc = resp, None
        return resp

    def form(self, **kw):
        f = self.doc.form(**kw)
        assert f is not None, f"页面 {self.url} 上没有表单 {kw}"
        return f

    @property
    def path(self):
        return urlsplit(self.url).path

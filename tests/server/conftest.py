"""真实 waitress 的夹具：随机端口，后台线程，用完关闭。"""
import threading

import pytest


@pytest.fixture
def live(app):
    yield from _serve(app)


@pytest.fixture
def live_seeded(seeded_app):
    yield from _serve(seeded_app)


def _serve(app):
    from bookshop_web.server import make_server

    srv = make_server(app, host="127.0.0.1", port=0)
    t = threading.Thread(target=srv.run, daemon=True)
    t.start()
    try:
        yield srv
    finally:
        srv.close()
        t.join(timeout=5)

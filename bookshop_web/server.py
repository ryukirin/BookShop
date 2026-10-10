"""waitress 服务进程（REQ-PLATFORM-012、REQ-PLATFORM-014、DEC-013）。"""
from __future__ import annotations

from .config import check_interpreter, load_config
from .logging_setup import LOGGER, configure

MAX_REQUEST_BODY = 6 * 1024 * 1024  # waitress 层上限；应用层 MAX_CONTENT_LENGTH 为 5 MiB
THREADS = 4


def make_server(app, host: str, port: int):
    from waitress.server import create_server

    return create_server(app, host=host, port=port, threads=THREADS,
                         max_request_body_size=MAX_REQUEST_BODY, ident="BookShop")


def serve_from_env() -> int:
    check_interpreter()
    config = load_config()
    configure(config.data_dir)
    from . import create_app

    app = create_app(config)
    srv = make_server(app, config.host, config.port)
    LOGGER.info("BookShop 已启动：http://%s:%s/BookShop/", srv.effective_host, srv.effective_port)
    try:
        srv.run()
    except KeyboardInterrupt:
        pass
    finally:
        srv.close()
    return 0

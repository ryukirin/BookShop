"""命令行入口：python -m bookshop_web serve | init-db（DEC-010、DEC-013）。"""
from __future__ import annotations

import argparse
import sys

from .config import ConfigError


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        message = message.replace("unrecognized arguments", "未知参数")
        self.print_usage(sys.stderr)
        sys.stderr.write(f"错误：{message}\n")
        raise SystemExit(2)


def main(argv=None) -> int:
    parser = _Parser(prog="python -m bookshop_web", description="BookShop 服务与初始化")
    sub = parser.add_subparsers(dest="command", required=True, parser_class=_Parser)
    sub.add_parser("serve", help="用 waitress 启动服务（读取 BOOKSHOP_* 环境变量）")
    sub.add_parser("init-db", help="建库并导入演示数据；管理员口令取自 BOOKSHOP_ADMIN_PASSWORD 或交互输入")
    sub.add_parser("check", help="只做启动自检（解释器、数据目录、密钥、端口），不启动服务")
    args = parser.parse_args(argv)
    try:
        if args.command == "check":
            from .config import check_interpreter, load_config

            check_interpreter()
            load_config()
            print("配置检查通过。")
            return 0
        if args.command == "serve":
            from .server import serve_from_env

            return serve_from_env()
        from .initdb import main as initdb_main

        return initdb_main()
    except ConfigError as e:
        sys.stderr.write(f"配置错误：{e}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

"""固定单进程 gevent 交付入口；停止文件仅用于本机优雅退出。"""
import argparse
import os
import sys
from pathlib import Path

import gevent
from gevent.pywsgi import WSGIServer

from bookshop_app import create_app


def _pid_is_running(pid):
    if pid <= 0:
        raise ValueError("PID 必须为正整数")
    if os.name == "nt":
        # Windows 的 os.kill(pid, 0) 会调用 TerminateProcess，不可用于探活。
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
        kernel.GetExitCodeProcess.restype = wintypes.BOOL
        kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
        kernel.CloseHandle.restype = wintypes.BOOL
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            error = ctypes.get_last_error()
            if error == 87:
                return False
            if error == 5:
                return True
            raise OSError(error, "无法安全查询 PID")
        try:
            code = wintypes.DWORD()
            if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)):
                raise ctypes.WinError(ctypes.get_last_error())
            return code.value == 259
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _acquire_pid(pid_file):
    recovered = False
    if pid_file.exists():
        try:
            old_pid = int(pid_file.read_text(encoding="ascii").strip())
        except (ValueError, OSError) as exc:
            raise RuntimeError("PID 文件损坏，请人工核对") from exc
        if _pid_is_running(old_pid):
            raise RuntimeError("已有 BookShop 进程或 PID 被占用")
        pid_file.unlink()
        recovered = True
    with pid_file.open("x", encoding="ascii") as stream:
        stream.write(str(os.getpid()))
    return recovered


def serve(app, *, port=8000):
    if port != 8000 and not app.config.get("TESTING"):
        raise ValueError("交付服务只能绑定端口 8000")
    pid_file = Path(app.config["DATABASE_PATH"]).parent / "bookshop.pid"
    stop_file = pid_file.with_suffix(".stop")
    recovered = _acquire_pid(pid_file)
    if recovered:
        app.logger.warning("检测到已退出进程的残留 PID，已恢复启动入口")
    if stop_file.exists():
        stop_file.unlink()
    server = WSGIServer(("127.0.0.1", port), app, log=None, error_log=None)

    def watch_stop():
        while True:
            if stop_file.exists():
                stop_file.unlink()
                app.logger.info("收到优雅停止信号")
                server.stop(timeout=10)
                break
            gevent.sleep(0.2)

    watcher = gevent.spawn(watch_stop)
    try:
        app.logger.info("gevent 服务启动")
        server.serve_forever()
    except KeyboardInterrupt:
        app.logger.info("前台中断，等待在途请求退出")
        server.stop(timeout=10)
    finally:
        watcher.kill()
        server.close()
        if pid_file.exists() and pid_file.read_text(encoding="ascii").strip() == str(os.getpid()):
            pid_file.unlink()
        app.logger.info("gevent 服务停止")
        for handler in app.logger.handlers[:]:
            app.logger.removeHandler(handler)
            handler.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description="BookShop gevent 单进程服务")
    parser.add_argument("--test-port", type=int)
    args = parser.parse_args(argv)
    if args.test_port is not None and os.environ.get("BOOKSHOP_TESTING") != "1":
        parser.error("仅隔离测试可使用临时端口")
    app = create_app({"TESTING": True} if args.test_port is not None else None)
    serve(app, port=args.test_port if args.test_port is not None else 8000)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("BookShop 启动失败：" + type(exc).__name__, file=sys.stderr)
        raise SystemExit(1)

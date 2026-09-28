"""TEST-001：BATCH-001 运行、配置和错误边界。"""
import importlib.metadata
import logging
import os
import secrets
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from urllib.request import urlopen

EXPECTED = {"Flask": "2.3.2", "Werkzeug": "2.3.6",
            "gevent": "24.2.1", "greenlet": "3.0.3"}

class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(logging.shutdown)
        self.root = Path(self.temp.name)
        self.config = {"TESTING": True, "PROPAGATE_EXCEPTIONS": False,
                       "DATABASE_PATH": str(self.root / "bookshop.db"),
                       "UPLOAD_DIR": str(self.root / "uploads"),
                       "SECRET_KEY": secrets.token_hex(32),
                       "LOG_PATH": str(self.root / "bookshop.log")}

    def test_fixed_installed_versions(self):
        self.assertEqual(sys.version_info[:3], (3, 11, 3))
        self.assertEqual(sqlite3.sqlite_version, "3.40.1")
        for name, version in EXPECTED.items():
            with self.subTest(name=name):
                self.assertEqual(importlib.metadata.version(name), version)

    def test_health_and_context_boundary(self):
        from bookshop_app import create_app
        client = create_app(self.config).test_client()
        response = client.get("/BookShop/health")
        self.assertEqual((response.status_code, response.get_data(as_text=True)), (200, "ok"))
        self.assertEqual(client.get("/health").status_code, 404)

    def test_missing_weak_placeholder_and_invalid_paths_fail_closed(self):
        from bookshop_app import create_app
        for secret in (None, "", "x" * 31, "CHANGE_ME" * 8):
            with self.subTest(secret=secret), self.assertRaises(ValueError):
                create_app({**self.config, "SECRET_KEY": secret})
        bad_path = self.root / "not-a-directory"
        bad_path.write_text("occupied", encoding="utf-8")
        with self.assertRaises(ValueError):
            create_app({**self.config, "UPLOAD_DIR": str(bad_path)})
        with self.assertRaises(ValueError):
            create_app({**self.config, "DATABASE_PATH": str(bad_path / "database.db")})

    def test_500_is_generic_and_log_excludes_secret(self):
        from bookshop_app import create_app
        app = create_app(self.config)
        def fail():
            raise RuntimeError("private diagnostic marker")
        app.add_url_rule("/BookShop/__failure", "__failure", fail)
        response = app.test_client().get("/BookShop/__failure")
        self.assertEqual(response.status_code, 500)
        self.assertIn("错误", response.get_data(as_text=True))
        self.assertNotIn("private diagnostic marker", response.get_data(as_text=True))
        log = (self.root / "bookshop.log").read_text(encoding="utf-8")
        self.assertNotIn(self.config["SECRET_KEY"], log)
        self.assertNotIn("private diagnostic marker", log)

    def test_gevent_loopback_probe_and_graceful_stop(self):
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        env = os.environ.copy()
        env.update({
            "BOOKSHOP_TESTING": "1",
            "BOOKSHOP_DATABASE_PATH": self.config["DATABASE_PATH"],
            "BOOKSHOP_UPLOAD_DIR": self.config["UPLOAD_DIR"],
            "BOOKSHOP_SECRET_KEY": self.config["SECRET_KEY"],
            "BOOKSHOP_LOG_PATH": self.config["LOG_PATH"],
        })
        process = subprocess.Popen(
            [sys.executable, "-m", "bookshop_app.server", "--test-port", str(port)],
            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        try:
            deadline = time.monotonic() + 10
            while True:
                if process.poll() is not None:
                    self.fail("gevent 服务异常退出")
                try:
                    with urlopen("http://127.0.0.1:" + str(port) + "/BookShop/health",
                                 timeout=0.5) as response:
                        self.assertEqual(response.status, 200)
                        self.assertEqual(response.read(), b"ok")
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        self.fail("gevent 健康检查超时")
                    time.sleep(0.1)
            pid_file = self.root / "bookshop.pid"
            server_pid = int(pid_file.read_text(encoding="ascii"))
            self.assertGreater(server_pid, 0)
            # Windows 虚拟环境的 python.exe 启动器可能另起解释器进程。
            from bookshop_app.server import _pid_is_running
            self.assertTrue(_pid_is_running(server_pid))
            (self.root / "bookshop.stop").write_text("stop", encoding="ascii")
            self.assertEqual(process.wait(timeout=10), 0)
            self.assertFalse(pid_file.exists())
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)

    def test_pid_check_is_readonly_and_stale_pid_can_recover(self):
        from bookshop_app.server import _pid_is_running, _acquire_pid
        self.assertTrue(_pid_is_running(os.getpid()))
        pid_file = self.root / "bookshop.pid"
        pid_file.write_text(str(os.getpid()), encoding="ascii")
        with self.assertRaises(RuntimeError):
            _acquire_pid(pid_file)
        self.assertEqual(pid_file.read_text(encoding="ascii"), str(os.getpid()))
        pid_file.write_text("2147483647", encoding="ascii")
        _acquire_pid(pid_file)
        self.assertEqual(pid_file.read_text(encoding="ascii"), str(os.getpid()))

    def test_log_rotation_preserves_request_correlation(self):
        from bookshop_app import create_app
        app = create_app(self.config)
        response = app.test_client().get("/BookShop/health?password=never-log-this")
        log = (self.root / "bookshop.log").read_text(encoding="utf-8")
        self.assertIn(response.headers["X-Request-ID"], log)
        self.assertNotIn("never-log-this", log)
        handler = app.logger.handlers[0]
        self.assertEqual(handler.maxBytes, 1024 * 1024)
        self.assertEqual(handler.backupCount, 7)
        handler.maxBytes = 256
        for _ in range(10):
            app.logger.info("轮转验证" * 20)
        self.assertTrue((self.root / "bookshop.log.1").exists())

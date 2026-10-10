"""TEST-002：配置与启动自检（REQ-PLATFORM-012、MIG-RULE-010、MIG-RULE-022、DEC-019）。"""
import os
import secrets
import subprocess
import sys
from pathlib import Path

import pytest

from bookshop_web import config as cfg


@pytest.fixture
def env(tmp_path):
    return {"BOOKSHOP_DATA_DIR": str(tmp_path), "BOOKSHOP_SECRET_KEY": secrets.token_hex(32)}


def test_defaults(env, tmp_path):
    c = cfg.load_config(env)
    assert c.data_dir == tmp_path and c.host == "127.0.0.1" and c.port == 8080


def test_custom_host_port(env):
    env.update(BOOKSHOP_HOST="0.0.0.0", BOOKSHOP_PORT="9090")
    c = cfg.load_config(env)
    assert (c.host, c.port) == ("0.0.0.0", 9090)


@pytest.mark.parametrize("key", ["BOOKSHOP_DATA_DIR", "BOOKSHOP_SECRET_KEY"])
def test_missing(env, key):
    env.pop(key)
    with pytest.raises(cfg.ConfigError):
        cfg.load_config(env)


def test_data_dir_must_exist(env, tmp_path):
    env["BOOKSHOP_DATA_DIR"] = str(tmp_path / "nope")
    with pytest.raises(cfg.ConfigError, match="数据目录"):
        cfg.load_config(env)


def test_data_dir_must_be_writable(env, monkeypatch):
    monkeypatch.setattr(cfg, "_writable", lambda p: False)
    with pytest.raises(cfg.ConfigError, match="不可写"):
        cfg.load_config(env)


@pytest.mark.parametrize("secret", ["", "short", secrets.token_hex(16), cfg.EXAMPLE_SECRET])
def test_bad_secret(env, secret):
    env["BOOKSHOP_SECRET_KEY"] = secret
    with pytest.raises(cfg.ConfigError, match="密钥不合规"):
        cfg.load_config(env)


@pytest.mark.parametrize("port", ["abc", "0", "65536", "-1"])
def test_bad_port(env, port):
    env["BOOKSHOP_PORT"] = port
    with pytest.raises(cfg.ConfigError, match="端口"):
        cfg.load_config(env)


def test_secret_not_required_for_init(env):
    env.pop("BOOKSHOP_SECRET_KEY")
    assert cfg.load_config(env, require_secret=False).secret_key is None


@pytest.mark.parametrize("version", [(3, 12, 9), (3, 11, 3), (3, 13, 0)])
def test_interpreter_must_be_3_12_10(version):
    with pytest.raises(cfg.ConfigError, match="3.12.10"):
        cfg.check_interpreter(version)


def test_interpreter_ok():
    cfg.check_interpreter((3, 12, 10))


def test_serve_refuses_example_secret(env):
    env = {**os.environ, **env, "BOOKSHOP_SECRET_KEY": cfg.EXAMPLE_SECRET, "PYTHONUTF8": "1"}
    p = subprocess.run([sys.executable, "-m", "bookshop_web", "serve"], env=env, capture_output=True,
                       text=True, encoding="utf-8", timeout=60, cwd=Path(__file__).resolve().parents[2])
    assert p.returncode != 0
    assert "密钥不合规" in p.stderr

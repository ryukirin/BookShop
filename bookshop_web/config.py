"""配置读取与启动自检（REQ-PLATFORM-012、MIG-RULE-010、MIG-RULE-022、DEC-019）。"""
from __future__ import annotations

import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

REQUIRED_PYTHON = (3, 12, 10)
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080
# config.example.ps1 中的占位值。用它启动会被拒绝。
EXAMPLE_SECRET = "replace-with-64-hex-chars-from-python-secrets-token-hex-32"
MIN_SECRET_BYTES = 32


class ConfigError(Exception):
    """配置不合规。消息直接展示给运维人员。"""


@dataclass(frozen=True)
class Config:
    data_dir: Path
    secret_key: str | None
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT


def check_interpreter(version: tuple[int, int, int] | None = None) -> None:
    v = tuple(version if version is not None else sys.version_info[:3])
    if v != REQUIRED_PYTHON:
        raise ConfigError(
            f"解释器版本不符：需要 Python 3.12.10，当前是 {'.'.join(map(str, v))}。"
            "请用 py -3.12 创建的虚拟环境（.venv\\Scripts\\python.exe）运行。"
        )


def _writable(path: Path) -> bool:
    try:
        with tempfile.TemporaryFile(dir=path):
            return True
    except OSError:
        return False


def _secret_bytes(secret: str) -> bytes:
    if re.fullmatch(r"(?:[0-9a-fA-F]{2})+", secret):
        return bytes.fromhex(secret)
    return secret.encode("utf-8")


def _check_secret(secret: str | None) -> str:
    if not secret or secret == EXAMPLE_SECRET:
        raise ConfigError("密钥不合规：请把 BOOKSHOP_SECRET_KEY 设为自己生成的随机值，不能为空，也不能用示例值。"
                          "可以用 python -c \"import secrets; print(secrets.token_hex(32))\" 生成。")
    if len(_secret_bytes(secret)) < MIN_SECRET_BYTES:
        raise ConfigError(f"密钥不合规：BOOKSHOP_SECRET_KEY 解码后至少要 {MIN_SECRET_BYTES} 字节。")
    return secret


def _port(raw: str | None) -> int:
    if raw is None or raw == "":
        return DEFAULT_PORT
    if not re.fullmatch(r"[0-9]{1,5}", raw) or not 1 <= int(raw) <= 65535:
        raise ConfigError(f"端口不合规：BOOKSHOP_PORT 必须是 1～65535 的整数，当前是 {raw!r}。")
    return int(raw)


def load_config(env=None, *, require_secret: bool = True) -> Config:
    env = os.environ if env is None else env
    raw_dir = (env.get("BOOKSHOP_DATA_DIR") or "").strip()
    if not raw_dir:
        raise ConfigError("缺少数据目录：请设置 BOOKSHOP_DATA_DIR（放在仓库之外的目录）。")
    data_dir = Path(raw_dir)
    if not data_dir.is_dir():
        raise ConfigError(f"数据目录不存在：{data_dir}")
    if not _writable(data_dir):
        raise ConfigError(f"数据目录不可写：{data_dir}")
    secret = env.get("BOOKSHOP_SECRET_KEY")
    if require_secret:
        secret = _check_secret(secret)
    host = (env.get("BOOKSHOP_HOST") or DEFAULT_HOST).strip()
    return Config(data_dir=data_dir, secret_key=secret, host=host, port=_port(env.get("BOOKSHOP_PORT")))

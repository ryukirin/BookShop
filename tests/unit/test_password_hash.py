"""EXP-004 转写：Werkzeug 默认的口令哈希（REQ-ACCOUNT-001、LEGACY-049、COMP-009）。

这一项检查的是所用库版本的默认参数，不依赖本项目的实现，所以没有批次标记。
"""
import time

from werkzeug.security import check_password_hash, generate_password_hash


def test_scrypt_defaults_and_cost():
    t = time.perf_counter()
    h = generate_password_hash("abc123")
    assert time.perf_counter() - t < 1.0
    assert h.startswith("scrypt:32768:8:1$")
    assert check_password_hash(h, "abc123") and not check_password_hash(h, "abc124")

"""TEST-019（校验函数）：输入长度与取值范围（REQ-DATA-005、MIG-RULE-018、LEGACY-059）。"""
import pytest

pytestmark = pytest.mark.batch(2)


@pytest.mark.parametrize("kind,ok,bad", [
    ("uname", ["a", "a" * 20, "张三"], ["", "a" * 21, None]),
    ("upwd", ["a", "a" * 64], ["", "a" * 65, None]),
    ("bname", ["a", "书" * 100], ["", "书" * 101, None]),
    ("publishers", ["a", "a" * 100], ["", "a" * 101]),
    ("cont", ["a", "简" * 4000], ["", "简" * 4001]),
    ("q_book", ["", "a" * 100], ["a" * 101]),
    ("q_member", ["", "a" * 20], ["a" * 21]),
    ("tname", ["", "a" * 20], ["a" * 21]),
])
def test_text(kind, ok, bad):
    from bookshop_web.validation import text

    for v in ok:
        assert text(kind, v) == v
    for v in bad:
        assert text(kind, v) is None


def test_text_rejects_nul():
    from bookshop_web.validation import text

    assert text("uname", "a\x00b") is None


@pytest.mark.parametrize("v,expected", [("0", 0), ("1", 1), ("999999", 999999), ("1000000", None), ("-1", None),
                                         ("1.0", None), ("abc", None), ("", None), (None, None), ("007", None),
                                         ("99999999999999999999", None)])
def test_stock(v, expected):
    from bookshop_web.validation import stock

    assert stock(v) == expected


@pytest.mark.parametrize("v,expected", [("1", 1), ("9", 9), ("123456789012345678", 123456789012345678),
                                         ("0", None), ("-1", None), ("abc", None), ("", None), (None, None),
                                         ("1.5", None), ("01", None), ("99999999999999999999", None)])
def test_positive_id(v, expected):
    from bookshop_web.validation import positive_id

    assert positive_id(v) == expected

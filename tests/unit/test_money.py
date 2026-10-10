"""TEST-018：金额（REQ-DATA-004、MIG-RULE-007、LEGACY-045、DEC-008）。"""
import pytest

pytestmark = pytest.mark.batch(2)


@pytest.mark.parametrize("text,cents", [("0", 0), ("0.1", 10), ("0.10", 10), ("39.8", 3980), ("39.80", 3980),
                                        ("268", 26800), ("99999.99", 9999999)])
def test_parse_ok(text, cents):
    from bookshop_web.money import parse_price

    assert parse_price(text) == cents


@pytest.mark.parametrize("text", ["", " ", "25.555", "-1", "abc", "1e3", "100000", "01", "1.", ".5", "1,5",
                                  "99999999999999999999", None, "NaN", "Infinity", "１２"])
def test_parse_rejected(text):
    from bookshop_web.money import parse_price

    assert parse_price(text) is None


@pytest.mark.parametrize("cents,text", [(0, "0.00"), (10, "0.10"), (3980, "39.80"), (26800, "268.00"), (9999999, "99999.99")])
def test_fmt(cents, text):
    from bookshop_web.money import fmt

    assert fmt(cents) == text


def test_exact_sum():
    from bookshop_web.money import fmt, parse_price

    assert fmt(sum(parse_price(x) for x in ("0.10", "0.20", "39.80"))) == "40.10"

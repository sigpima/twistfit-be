import pytest

from app.domains.auth.identifier import classify_identifier, normalize_phone


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("0912345678", "+84912345678"),
        ("+84912345678", "+84912345678"),
        ("091 234 5678", "+84912345678"),
        ("091-234-5678", "+84912345678"),
        ("0512345678", "+84512345678"),
        ("0712345678", "+84712345678"),
        ("0812345678", "+84812345678"),
    ],
)
def test_normalize_phone_accepts_valid_vn_mobile_numbers(raw, expected):
    assert normalize_phone(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "0212345678",  # landline prefix, not mobile
        "091234567",  # too short
        "09123456789",  # too long
        "12345",
        "user@example.com",
        "",
    ],
)
def test_normalize_phone_rejects_invalid_input(raw):
    assert normalize_phone(raw) is None


def test_classify_identifier_recognizes_a_phone_number():
    assert classify_identifier("0912345678") == ("phone", "+84912345678")


def test_classify_identifier_recognizes_an_email():
    assert classify_identifier("Linh@Example.com ") == ("email", "linh@example.com")


def test_classify_identifier_rejects_garbage():
    assert classify_identifier("not-an-identifier") is None

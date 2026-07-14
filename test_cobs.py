"""Testy COBS: wektory + wlasciwosci + podroz w obie strony."""

import json
import random
from pathlib import Path

import pytest

from cobs import cobs_encode, cobs_decode

_DANE = json.loads(
    (Path(__file__).parent / "testvectors" / "cobs.json").read_text(encoding="utf-8")
)
_WEKTORY = _DANE["vectors"]
_IDS = [w["name"] for w in _WEKTORY]


@pytest.mark.parametrize("w", _WEKTORY, ids=_IDS)
def test_encode(w):
    assert cobs_encode(bytes.fromhex(w["decoded_hex"])) == bytes.fromhex(w["encoded_hex"])


@pytest.mark.parametrize("w", _WEKTORY, ids=_IDS)
def test_decode(w):
    assert cobs_decode(bytes.fromhex(w["encoded_hex"])) == bytes.fromhex(w["decoded_hex"])


def test_wynik_encode_nigdy_nie_zawiera_zera():
    """Sens istnienia COBS: w zakodowanych danych nie ma 0x00."""
    rng = random.Random(42)          # staly seed = test powtarzalny
    for _ in range(200):
        dane = bytes(rng.randrange(256) for _ in range(rng.randrange(300)))
        assert 0x00 not in cobs_encode(dane)


def test_podroz_w_obie_strony():
    """decode(encode(x)) == x dla losowych danych, w tym pelnych zer."""
    rng = random.Random(1337)
    for _ in range(200):
        dane = bytes(rng.randrange(256) for _ in range(rng.randrange(300)))
        assert cobs_decode(cobs_encode(dane)) == dane


def test_decode_odrzuca_smieci():
    """Uszkodzone dane maja rzucac ValueError, nie zwracac bzdur po cichu."""
    with pytest.raises(ValueError):
        cobs_decode(b"\x05\x11")       # licznik 5, a bajtow tylko 1 - ucieta
    with pytest.raises(ValueError):
        cobs_decode(b"\x00\x11")       # zero jako licznik - nielegalne


def test_granica_254_bajtow():
    """254 niezerowe bajty: jedna pelna grupa 0xFF, bez ogona."""
    dane = bytes(range(1, 255))                 # 01 02 ... FE (254 bajty, bez zer)
    zakodowane = cobs_encode(dane)
    assert zakodowane == b"\xff" + dane          # dokladnie 255 bajtow
    assert cobs_decode(zakodowane) == dane


def test_granica_255_bajtow():
    """255 bajtow: pelna grupa + druga grupa z jednym bajtem."""
    dane = bytes(range(1, 255)) + b"\x42"
    zakodowane = cobs_encode(dane)
    assert zakodowane == b"\xff" + bytes(range(1, 255)) + b"\x02\x42"
    assert cobs_decode(zakodowane) == dane
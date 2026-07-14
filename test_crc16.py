"""Testy CRC16 na wektorach z testvectors/crc16.json."""

import json
from pathlib import Path

import pytest

from crc16 import crc16_ccitt_false

# wczytanie wektorow NA ETAPIE ZBIERANIA testow (raz, nie w kazdym tescie)
_DANE = json.loads(
    (Path(__file__).parent / "testvectors" / "crc16.json").read_text(encoding="utf-8")
)


@pytest.mark.parametrize(
    "wektor",
    _DANE["vectors"],
    ids=[w["name"] for w in _DANE["vectors"]],   # czytelne nazwy w wydruku
)
def test_wektor(wektor):
    dane = bytes.fromhex(wektor["input_hex"])
    oczekiwany = int(wektor["expected"], 16)
    assert crc16_ccitt_false(dane) == oczekiwany


def test_rozne_dane_daja_rozny_crc():
    """Test wlasciwosci - zostaje, bo sprawdza cos innego niz wektory."""
    assert crc16_ccitt_false(b"Hello") != crc16_ccitt_false(b"Hella")


def test_wynik_miesci_sie_w_16_bitach():
    for dane in [b"", b"x", b"123456789", bytes(range(256))]:
        assert 0 <= crc16_ccitt_false(dane) <= 0xFFFF
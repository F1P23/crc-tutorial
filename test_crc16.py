"""Testy CRC16 - pytest znajdzie ten plik po nazwie test_*.py."""

from crc16 import crc16_ccitt_false


def test_wektor_standardowy():
    """Opublikowana wartosc wzorcowa dla CCITT-FALSE."""
    assert crc16_ccitt_false(b"123456789") == 0x29B1


def test_puste_dane():
    """CRC z zera bajtow = wartosc poczatkowa (nic jej nie zmienilo)."""
    assert crc16_ccitt_false(b"") == 0xFFFF


def test_jeden_bajt():
    """Wartosc CRC16/CCITT-FALSE dla pojedynczego bajtu 'A'."""
    assert crc16_ccitt_false(b"A") == 0xB915


def test_zmiana_bitu_zmienia_crc():
    """Wlasciwosc: rozne dane => rozny CRC (sens istnienia CRC)."""
    assert crc16_ccitt_false(b"Hello") != crc16_ccitt_false(b"Hella")


def test_wynik_miesci_sie_w_16_bitach():
    """CRC16 nigdy nie moze przekroczyc 0xFFFF."""
    for dane in [b"", b"x", b"123456789", bytes(range(256))]:
        assert 0 <= crc16_ccitt_false(dane) <= 0xFFFF
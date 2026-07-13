"""
CRC16/CCITT-FALSE - suma kontrolna wykrywajaca przeklamania danych.

Parametry wariantu (wazne! CRC16 ma kilkanascie odmian):
  wielomian: 0x1021, wartosc poczatkowa: 0xFFFF,
  bez odwracania bitow, bez koncowego XOR.

Standardowy wektor kontrolny: crc16("123456789") == 0x29B1
"""


def crc16_ccitt_false(data: bytes) -> int:
    """Liczy CRC16/CCITT-FALSE z podanych bajtow."""
    crc = 0x0000                          # wartosc poczatkowa
    for byte in data:
        crc ^= byte << 8                  # wciagnij bajt w gorna polowke
        for _ in range(8):                # przetworz 8 bitow
            if crc & 0x8000:              # najstarszy bit ustawiony?
                crc = (crc << 1) ^ 0x1021 # przesun i XOR z wielomianem
            else:
                crc = crc << 1            # tylko przesun
            crc &= 0xFFFF                 # utnij do 16 bitow
    return crc


if __name__ == "__main__":
    # Ten blok wykonuje sie TYLKO gdy uruchamiasz plik bezposrednio
    # (python crc16.py), a NIE gdy ktos go importuje (np. testy).
    import sys

    if len(sys.argv) > 1:
        tekst = sys.argv[1]               # tekst podany w terminalu
    else:
        tekst = "123456789"               # domyslny wektor kontrolny

    wynik = crc16_ccitt_false(tekst.encode("ascii"))
    print(f'CRC16/CCITT-FALSE("{tekst}") = 0x{wynik:04X}')
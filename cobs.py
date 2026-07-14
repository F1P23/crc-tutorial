"""
COBS (Consistent Overhead Byte Stuffing).

Idea: usun wszystkie bajty 0x00 z danych, kodujac ich pozycje
w bajtach-licznikach. Wtedy 0x00 moze sluzyc jako separator ramek.

Zasady kodowania:
- kazda grupa zaczyna sie bajtem-licznikiem N (1..255)
- po nim nastepuje N-1 bajtow danych (zadnego zera wsrod nich)
- licznik N < 255 oznacza: po grupie bylo zero (odtworz je przy dekodowaniu)
- licznik N == 255 oznacza: grupa pelna (254 bajty), zera NIE bylo
"""


def cobs_encode(data: bytes) -> bytes:
    """Koduje dane tak, by wynik nie zawieral bajtu 0x00."""
    out = bytearray([0])      # [0] to placeholder na pierwszy licznik
    code_idx = 0              # gdzie w out siedzi biezacy licznik
    code = 1                  # licznik biezacej grupy (1 = pusta grupa)
    n = len(data)

    for i, byte in enumerate(data):
        if byte != 0:
            out.append(byte)
            code += 1

        # grupe zamykamy gdy: trafilismy zero LUB grupa jest pelna (254 bajty)
        if byte == 0 or code == 0xFF:
            out[code_idx] = code          # wpisz licznik w placeholder
            code = 1
            code_idx = len(out)
            # nowy placeholder tylko jesli cos jeszcze bedzie:
            # po zerze zawsze (zero konczy grupe, wiec nastepna istnieje),
            # po pelnej grupie tylko gdy dane sie nie skonczyly
            if byte == 0 or i != n - 1:
                out.append(0)

    if code_idx < len(out):               # domknij ostatnia (niepelna) grupe
        out[code_idx] = code
    return bytes(out)


def cobs_decode(data: bytes) -> bytes:
    """Odwraca cobs_encode. Rzuca ValueError dla uszkodzonych danych."""
    out = bytearray()
    i = 0
    while i < len(data):
        code = data[i]
        if code == 0:
            raise ValueError("bajt 0x00 wewnatrz danych COBS (uszkodzona ramka?)")
        i += 1
        block = data[i:i + code - 1]
        if len(block) != code - 1:
            raise ValueError("ucieta ramka COBS (za malo bajtow)")
        out.extend(block)
        i += code - 1
        # odtworz zero po grupie - chyba ze grupa byla pelna (0xFF)
        # albo to koniec danych (ostatnia grupa nie ma zera "za soba")
        if code != 0xFF and i < len(data):
            out.append(0)
    return bytes(out)
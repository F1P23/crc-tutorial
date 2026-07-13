# Tutorial, część 2: wektory w JSON + moduł COBS + jedno CI dla wszystkiego
## Kontynuacja — od pojedynczego skryptu do mini-projektu w stylu proto/

Wymagania: ukończona część 1 (repo `crc-tutorial` z działającym `crc16.py`, `test_crc16.py` i zielonym CI).
Czas: ~1,5 godziny.
Czego się nauczysz: wektory testowe jako dane (JSON) zamiast wartości zaszytych w kodzie, `pytest.mark.parametrize`, implementacja i testowanie COBS (z testem "w obie strony"), oraz jak jedno CI pilnuje wielu modułów bez żadnych zmian w konfiguracji.

> **Po co to wszystko:** po tej części Twoje repo będzie miniaturą repo `proto/` z projektu vendingowego — te same wzorce (wektory w JSON, kodeki, testy odporne na regresje), tylko w skali ćwiczebnej. Przećwiczysz tu na spokojnie dokładnie to, co potem zrobisz "na ostro".

---

# Spis treści

1. Struktura docelowa
2. Krok 1: wektory CRC16 przenosimy do JSON
3. Krok 2: test, który wczytuje wektory (i mała perełka: parametrize)
4. Krok 3: moduł COBS — implementacja z komentarzami
5. Krok 4: wektory i testy COBS (w tym test "w obie strony")
6. Krok 5: push — i patrz, jak CI pilnuje obu modułów naraz
7. Pułapka na deser: pełny blok 254 bajtów
8. Ćwiczenia dodatkowe

---

# 1. Struktura docelowa

Na koniec tej części repo będzie wyglądać tak (nowe rzeczy oznaczone ←):

```
crc-tutorial/
├── README.md
├── .gitignore
├── crc16.py
├── cobs.py                    ← nowy modul
├── test_crc16.py              ← przerobiony: czyta wektory z JSON
├── test_cobs.py               ← nowy
├── testvectors/               ← nowy folder
│   ├── crc16.json
│   └── cobs.json
├── docs/
│   └── (tutoriale)
└── .github/workflows/testy.yml   (BEZ ZMIAN — to jest puenta)
```

> **Uwaga o kodowaniu (nauczeni doświadczeniem):** wszystkie pliki twórz i edytuj w VS Code, który zapisuje UTF-8. W komentarzach kodu celowo unikam polskich ogonków i ozdobnych myślników — ASCII w kodzie źródłowym to o jedną klasę problemów mniej. Polskie znaki zostawiamy dla plików .md i .json (tam UTF-8 i tak jest obowiązkowy i jawny).

---

# 2. Krok 1: wektory CRC16 przenosimy do JSON

Dotychczas wartości oczekiwane siedziały wprost w kodzie testów (`assert ... == 0x29B1`). To działa, ale ma wady, które w większym projekcie bolą:

- wektory są uwięzione w Pythonie — implementacja C musiałaby mieć własną kopię (a dwie kopie zawsze w końcu się rozjeżdżają),
- dodanie wektora = edycja kodu testu,
- nie widać na pierwszy rzut oka, CO jest testowane — dane giną między assertami.

Rozwiązanie: **wektory jako dane w pliku JSON, testy jako maszynka, która je czyta**. Utwórz folder `testvectors/` i w nim plik `crc16.json`:

```json
{
  "algorithm": "CRC16/CCITT-FALSE",
  "params": { "poly": "0x1021", "init": "0xFFFF", "refin": false, "refout": false, "xorout": "0x0000" },
  "vectors": [
    { "name": "wzorcowy (opublikowany)", "input_hex": "313233343536373839", "expected": "0x29B1" },
    { "name": "puste dane = init",        "input_hex": "",                   "expected": "0xFFFF" },
    { "name": "jeden bajt 'A'",           "input_hex": "41",                 "expected": "0xB915" }
  ]
}
```

Trzy rzeczy do zauważenia:

- **`input_hex` zamiast tekstu** — wektory opisują BAJTY (bo CRC działa na bajtach), a `"313233343536373839"` to po prostu ASCII "123456789" zapisane szesnastkowo. Dzięki temu format uniesie też dane niebędące tekstem (a takie będą w ramkach!).
- **Sekcja `params`** — dokumentuje wariant algorytmu w samym pliku. Za pół roku nikt nie będzie zgadywał, "który to CRC16".
- **`0xB915` dla 'A'** — wartość, którą wspólnie zweryfikowaliśmy w części 1 (pamiętasz aferę z 0x58E5?). Wektor ma swoją historię — i teraz ta historia jest utrwalona w repo, a nie w czyjejś pamięci.

> **Zasada dodawania wektorów:** wektor-kotwica (wzorcowy, opublikowany) weryfikuje WARIANT algorytmu. Wektory policzone własną, już-zaufaną implementacją chronią przed REGRESJĄ (przypadkowym zepsuciem w przyszłości) — ale nie są niezależnym dowodem poprawności. Oba rodzaje są cenne; po prostu wiedz, który jest którym. Chcesz dodać własny wektor? `python crc16.py "TwojTekst"`, przepisz wynik do JSON — od teraz każda zmiana psująca ten przypadek zostanie wykryta.

---

# 3. Krok 2: test, który wczytuje wektory

Podmień zawartość `test_crc16.py`:

```python
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
```

Nowość: **`@pytest.mark.parametrize`** — zamiast jednej funkcji z pętlą (jak w części 1), pytest tworzy **osobny test dla każdego wektora**. Różnica praktyczna jest duża — uruchom `pytest -v`:

```
test_crc16.py::test_wektor[wzorcowy (opublikowany)] PASSED
test_crc16.py::test_wektor[puste dane = init] PASSED
test_crc16.py::test_wektor[jeden bajt 'A'] PASSED
test_crc16.py::test_rozne_dane_daja_rozny_crc PASSED
test_crc16.py::test_wynik_miesci_sie_w_16_bitach PASSED
```

Każdy wektor raportuje się osobno, z własną nazwą. Gdy padnie jeden — pytest wykona pozostałe i pokaże, KTÓRY dokładnie padł (pętla z części 1 zatrzymywała się na pierwszym błędzie i resztę zostawiała w niewiedzy). Przy 50 wektorach ramek w prawdziwym proto/ ta różnica to być albo nie być diagnostyki.

Uruchom `pytest` — komplet zielony? Commit:

```
git add testvectors/crc16.json test_crc16.py
git commit -m "Przenieś wektory CRC16 do JSON + parametrize"
git push
```

---

# 4. Krok 3: moduł COBS — implementacja z komentarzami

Przypomnienie idei w jednym zdaniu (pełny wykład: przewodnik M0, rozdz. 3): COBS przekodowuje dane tak, żeby nie zawierały bajtu `0x00` — dzięki czemu `0x00` może jednoznacznie oznaczać koniec ramki na łączu. W zamian: przed każdą grupą danych stoi bajt-licznik mówiący "za ile bajtów jest (wirtualne) zero".

Utwórz `cobs.py`:

```python
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
```

Nie martw się, jeśli logika liczników nie wchodzi od razu — to jest gęste. Kluczowe do zrozumienia: `encode` wpisuje liczniki w miejsca placeholderów, `decode` czyta licznik → kopiuje bajty → wstawia zero (chyba że licznik to 0xFF albo koniec). Resztę zaraz przyszpilą testy — i to one, nie wpatrywanie się w kod, dadzą Ci pewność.

---

# 5. Krok 4: wektory i testy COBS

## 5.1 Wektory: `testvectors/cobs.json`

```json
{
  "algorithm": "COBS",
  "vectors": [
    { "name": "puste dane",          "decoded_hex": "",           "encoded_hex": "01" },
    { "name": "samo zero",           "decoded_hex": "00",         "encoded_hex": "0101" },
    { "name": "dwa zera",            "decoded_hex": "0000",       "encoded_hex": "010101" },
    { "name": "bez zer",             "decoded_hex": "112233",     "encoded_hex": "04112233" },
    { "name": "zero w srodku",       "decoded_hex": "110022",     "encoded_hex": "02110222" },
    { "name": "zero miedzy grupami", "decoded_hex": "11220033",   "encoded_hex": "0311220233" },
    { "name": "piec bajtow bez zer", "decoded_hex": "1122334455", "encoded_hex": "061122334455" }
  ]
}
```

Te pary pochodzą z opisu algorytmu (część to wręcz przykłady kanoniczne z literatury) — pełnią rolę kotwic, jak `0x29B1` dla CRC.

## 5.2 Testy: `test_cobs.py`

```python
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
```

Trzy nowe wzorce testowe, każdy wart zapamiętania:

- **Podróż w obie strony (roundtrip)** — `decode(encode(x)) == x` na losowych danych. Nie wymaga znajomości poprawnego wyniku pośredniego, a znajduje błędy, o których nie pomyślałeś pisząc wektory ręcznie. Zwróć uwagę na `random.Random(42)` — **stały seed** sprawia, że "losowe" dane są identyczne przy każdym uruchomieniu. Test niedeterministyczny (raz zielony, raz czerwony) to najgorszy rodzaj testu.
- **Test właściwości docelowej** — "wynik nie zawiera zer" to POWÓD istnienia COBS, więc ma swój bezpośredni test.
- **Test odrzucania śmieci** — `pytest.raises` sprawdza, że funkcja RZUCA wyjątek dla złych danych. W protokole na kablu obok silników dane BĘDĄ czasem uszkodzone — cichy zwrot bzdur byłby groźniejszy niż wyjątek.

> **Subtelność, uczciwie:** roundtrip przechodzi też wtedy, gdy encode i decode mają wspólny, symetryczny błąd formatu (mylą się identycznie w obie strony). Przed tym chronią wektory z 5.1 — one przyszpilają format ZEWNĘTRZNIE. Roundtrip + wektory = komplet; samo jedno albo drugie ma ślepą plamkę. To ta sama zasada, co "wspólny kodek Pythona w symulatorze i agencie nie zweryfikuje sam siebie" z przewodnika M0.

Uruchom `pytest -v` — powinno być kilkanaście pozycji (parametrize robi swoje), wszystkie zielone.

---

# 6. Krok 5: push — i patrz, jak CI pilnuje obu modułów naraz

```
git add cobs.py test_cobs.py testvectors/cobs.json
git commit -m "Dodaj modul COBS z wektorami i testami"
git push
```

Wejdź w Actions i przeczytaj log kroku "Uruchom testy". Zwróć uwagę na jedno: **w pliku `.github/workflows/testy.yml` nie zmieniłeś ANI ZNAKU** — a CI testuje już oba moduły:

```
collected 14 items

test_cobs.py::test_encode[puste dane] PASSED
test_cobs.py::test_encode[samo zero] PASSED
...
test_crc16.py::test_wektor[wzorcowy (opublikowany)] PASSED
...
```

To dlatego, że przepis CI mówi tylko `pytest -v`, a pytest **sam odkrywa** wszystkie pliki `test_*.py`. Dodasz trzeci moduł (framer!) z plikiem `test_framer.py` — CI go podchwyci automatycznie. Konfigurację CI pisze się raz; potem rośnie sam projekt, nie konfiguracja. Dokładnie tak będzie w proto/: jeden pipeline, a pod nim coraz więcej kodeków i wektorów.

---

# 7. Pułapka na deser: pełny blok 254 bajtów

W checkliście M0 przy wektorach COBS stoi: "w tym 254B, 255B". Dlaczego akurat te rozmiary? Bo licznik COBS jest jednobajtowy — maksymalna grupa to **254 bajty danych** (licznik 0xFF), i na tej granicy żyje najbardziej podstępny przypadek brzegowy algorytmu:

- grupa pełna (licznik 0xFF) NIE oznacza zera po sobie — dekoder nie może go wstawić,
- dane kończące się dokładnie na pełnej grupie kodują się BEZ dodatkowej pustej grupy na końcu.

Dopisz do `test_cobs.py`:

```python
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
```

Jeśli oba przechodzą — Twoja implementacja obsługuje granicę poprawnie (ta z rozdziału 4 obsługuje). Wiele naiwnych implementacji COBS znalezionych w internecie wykłada się dokładnie tutaj — dodając zbędne zero po pełnej grupie kończącej dane. Roundtrip na losowych danych tego nie łapie prawie nigdy (trzeba by wylosować dokładnie 254 niezerowe bajty pod rząd), wektory ręczne z rozdziału 5.1 też nie — **przypadki brzegowe trzeba testować celowo**. To jest odpowiedź na pytanie "skąd wiem, jakie wektory dodać": z analizy, gdzie algorytm ma szwy.

Commit, push, zielono — i masz w repo komplet: wektory-kotwice, roundtrip, właściwości, odrzucanie śmieci i celowane przypadki brzegowe. Pięć rodzajów siatki na pięć rodzajów błędów.

---

# 8. Ćwiczenia dodatkowe

1. **Zepsuj COBS i patrz, co łapie siatka**: w `cobs_encode` zmień warunek `code == 0xFF` na `code == 0xFE` i uruchom `pytest -v`. Które testy padły? (Podpowiedź: dopiero te z rozdziału 7 — kolejny dowód, że brzegi trzeba testować celowo). Cofnij zmianę.
2. **Dodaj własny wektor CRC**: policz `python crc16.py "VMC"` i dodaj wynik do `crc16.json`. Push — zobacz w logu CI, że pojawił się nowy test bez zmiany żadnego `.py`.
3. **Wektor przekrojowy (przedsmak framera)**: policz CRC z bajtów `01 01 05 00 07 00 08 0C 10 DE 02 18 07` (to nagłówek + payload VendRequest z przewodnika M0!). Dodaj jako wektor "naglowek ramki VendRequest". Właśnie policzyłeś prawdziwą wartość, która w przewodniku figurowała jako "XX XX".
4. **Dla ambitnych — framer**: napisz `framer.py` z funkcją `build_frame(msg_type, seq, payload) -> bytes`, która składa nagłówek + CRC + COBS + delimiter. Testy: znane wejście → znane bajty (wektor z ćwiczenia 3 nagle staje się użyteczny), roundtrip parse(build(x)) == x. To już jest dosłownie kod klasy proto/impl/.

---

## Co teraz umiesz (ponad część 1)

```
[✓] Trzymać wektory testowe jako dane (JSON), nie kod
[✓] pytest.mark.parametrize — osobny, nazwany test na kazdy wektor
[✓] Test roundtrip na losowych danych ze stalym seedem
[✓] Testowac wlasciwosci (brak zer) i obsluge bledow (pytest.raises)
[✓] Testowac celowane przypadki brzegowe (granica 254B)
[✓] Rozumiec, ze CI z "pytest" skaluje sie samo na nowe moduly
[✓] Znac slepe plamki kazdego rodzaju testu i skladac je w komplet
```

Od tego miejsca do prawdziwego `proto/` brakuje już tylko: definicji protobuf (vmc.proto), drugiej implementacji w C konsumującej TE SAME pliki JSON — i przeniesienia całości na firmowy GitLab. Wzorce masz w palcach.

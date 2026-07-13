# Tutorial: pierwsze repo na GitHub + skrypt CRC16 + testy + CI
## Kompletna ścieżka dla początkującego — od zera do zielonego (i czerwonego!) pipeline'u

Czas przejścia: ~1,5–2 godziny w spokojnym tempie.
Czego się nauczysz: git, GitHub, struktura mini-projektu Python, pytest, CI (GitHub Actions), czytanie logów po oblanym teście.

> **Uwaga kontekstowa:** ten tutorial używa GitHuba i jego systemu CI (GitHub Actions), bo to najlepsze publiczne środowisko do nauki. W firmowym GitLabie idea jest identyczna, różni się tylko plik konfiguracyjny CI (`.gitlab-ci.yml` zamiast `.github/workflows/*.yml`) — różnice pokazuję na końcu w rozdziale 11. Umiejętności przenoszą się 1:1.

---

# Spis treści

1. Przygotowanie narzędzi (raz na komputer)
2. Konto i nowe repozytorium na GitHub
3. Sklonowanie repo na komputer
4. Piszemy skrypt: crc16.py
5. Uruchamiamy i bawimy się skryptem
6. Piszemy testy: test_crc16.py
7. CI: uczymy GitHub uruchamiać nasze testy
8. Psujemy kod — czyli jak wygląda CZERWONE CI i jak je czytać
9. Naprawa, zielony pipeline, dobre nawyki
10. Git w pracy dwuosobowej: pull, gałęzie, konflikty, cofanie, tagi
11. Aneks: to samo w GitLab CI
12. Ciekawostki i pytania, które zada każdy początkujący

---

# 1. Przygotowanie narzędzi (raz na komputer)

Potrzebujesz trzech rzeczy: **git** (system kontroli wersji), **Python 3** i **edytor** (VS Code).

## 1.1 Windows

```
1. Git:     https://git-scm.com/download/win  → instaluj z domyślnymi opcjami
2. Python:  https://python.org/downloads → instalator, KONIECZNIE zaznacz
            ☑ "Add python.exe to PATH" na pierwszym ekranie instalatora
3. VS Code: https://code.visualstudio.com → zainstaluj + rozszerzenie "Python"
```

> **Wskazówka:** "Add to PATH" to najczęściej pomijany checkbox świata. Bez niego komenda `python` w terminalu nie zadziała i będziesz szukać winy wszędzie, tylko nie tu. Jeśli już zainstalowałeś bez tego — najprościej odinstalować i zainstalować jeszcze raz.

## 1.2 Sprawdzenie, że wszystko działa

Otwórz terminal (Windows: menu Start → wpisz "PowerShell") i wpisz kolejno:

```
git --version        →  git version 2.4x.x
python --version     →  Python 3.12.x (lub podobne 3.10+)
```

Jeśli obie komendy odpowiadają numerem wersji — jedziemy dalej.

## 1.3 Przedstaw się gitowi (raz)

Git podpisuje każdą zmianę Twoim nazwiskiem i mailem. Ustaw je:

```
git config --global user.name "Jan Kowalski"
git config --global user.email "jan@przyklad.pl"
```

> **Ciekawostka:** ten mail będzie widoczny publicznie w historii commitów na GitHubie. Jeśli Ci to przeszkadza, GitHub daje adres-przykrywkę: Settings → Emails → "Keep my email addresses private" — pokaże Ci adres w stylu `1234567+login@users.noreply.github.com`, którego możesz użyć w konfiguracji.

---

# 2. Konto i nowe repozytorium na GitHub

## 2.1 Konto

Wejdź na https://github.com → **Sign up** → podaj mail, hasło, login. Login wybierz z głową — będzie w adresach wszystkich Twoich projektów (github.com/twojlogin/...).

## 2.2 Nowe repozytorium

Repozytorium ("repo") to projekt: folder z plikami + cała historia ich zmian.

1. Po zalogowaniu kliknij **zielony przycisk "New"** (albo plus **+** w prawym górnym rogu → "New repository").
2. Wypełnij formularz:

```
Repository name:   crc-tutorial
Description:       Nauka: CRC16 + pytest + CI          (opcjonalne)
Visibility:        ● Public   ○ Private
                   (Public = każdy może zobaczyć; do nauki bez znaczenia,
                    a Public ma darmowe nielimitowane minuty CI)
☑ Add a README file          ← ZAZNACZ (repo nie będzie puste,
                                od razu da się je sklonować)
Add .gitignore:    Python     ← wybierz z listy (wyjaśnienie niżej)
License:           None       (do nauki nieistotne)
```

3. Kliknij **Create repository**. Gotowe — masz repo pod adresem `https://github.com/twojlogin/crc-tutorial`.

> **Co to .gitignore?** Plik z listą rzeczy, których git ma NIE śledzić. Szablon "Python" ignoruje m.in. `__pycache__/` (folder ze skompilowanymi śmieciami, który Python tworzy sam) i katalogi środowisk wirtualnych. Bez tego pliku te śmieci trafiałyby do repo przy każdym commicie i zaśmiecały historię.

---

# 3. Sklonowanie repo na komputer

"Klonowanie" = pobranie repo z GitHuba na dysk, razem z niewidzialnym połączeniem zwrotnym (będziesz mógł wysyłać zmiany z powrotem).

1. Na stronie repo kliknij zielony przycisk **"<> Code"** → zakładka **HTTPS** → skopiuj adres (`https://github.com/twojlogin/crc-tutorial.git`).
2. W terminalu przejdź tam, gdzie trzymasz projekty, i sklonuj:

```
cd ~
mkdir projekty
cd projekty
git clone https://github.com/twojlogin/crc-tutorial.git
cd crc-tutorial
```

3. Otwórz folder w VS Code:

```
code .
```

(kropka = "bieżący folder"). Zobaczysz w drzewku pliki `README.md` i `.gitignore`.

> **Wskazówka:** przy pierwszym wysyłaniu zmian (rozdz. 4.3) GitHub poprosi o logowanie. Na Windowsie otworzy się okno przeglądarki — logujesz się raz, git zapamięta (mechanizm Git Credential Manager instaluje się razem z gitem). Hasła do konta NIE podaje się w terminalu — GitHub od 2021 nie akceptuje haseł w gicie, tylko tokeny/logowanie przez przeglądarkę.

---

# 4. Piszemy skrypt: crc16.py

## 4.1 Kod

W VS Code utwórz nowy plik `crc16.py` (File → New File albo ikonka przy nazwie folderu) i wklej:

```python
"""
CRC16/CCITT-FALSE — suma kontrolna wykrywajaca przeklamania danych.

Parametry wariantu (wazne! CRC16 ma kilkanascie odmian):
  wielomian: 0x1021, wartosc poczatkowa: 0xFFFF,
  bez odwracania bitow, bez koncowego XOR.

Standardowy wektor kontrolny: crc16("123456789") == 0x29B1
"""


def crc16_ccitt_false(data: bytes) -> int:
    """Liczy CRC16/CCITT-FALSE z podanych bajtow."""
    crc = 0xFFFF                          # wartosc poczatkowa
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
```

## 4.2 Co tu się dzieje — dla ciekawych

Nie musisz rozumieć matematyki CRC, żeby przejść tutorial, ale dwa zdania intuicji: CRC traktuje dane jak jeden wielki ciąg bitów i wykonuje na nim rodzaj "dzielenia z resztą" przez ustaloną liczbę (wielomian 0x1021). Reszta z tego dzielenia to właśnie CRC — zmiana choćby jednego bitu danych daje zupełnie inną resztę, i to jest cała sztuczka wykrywania przekłamań.

- `bytes` vs `str`: CRC liczy się z **bajtów**, nie z tekstu. Dlatego `tekst.encode("ascii")` — zamiana napisu na bajty.
- `crc &= 0xFFFF`: Python ma liczby dowolnej długości, więc po przesunięciu w lewo trzeba ręcznie "uciąć" wynik do 16 bitów. W C to się dzieje samo (typ uint16_t) — klasyczna różnica między językami, o którą rozbijają się porównania implementacji.
- `if __name__ == "__main__":` — magiczna linijka odróżniająca "uruchomiono mnie" od "zaimportowano mnie". Dzięki niej testy mogą zaimportować funkcję bez odpalania części terminalowej.
- `0x{wynik:04X}` — formatowanie: szesnastkowo, wielkie litery, dopełnij zerami do 4 znaków (np. `0x29B1`, `0x00FA`).

## 4.3 Pierwszy commit i push

Zapisz plik (Ctrl+S). Teraz utrwalamy zmianę w historii i wysyłamy na GitHub. W terminalu (w folderze projektu):

```
git status                     # co się zmieniło? (zobaczysz crc16.py na czerwono)
git add crc16.py               # "zapakuj ten plik do paczki"
git commit -m "Dodaj implementację CRC16/CCITT-FALSE"
                               # "zaplombuj paczkę z opisem"
git push                       # "wyślij na GitHub"
```

Odśwież stronę repo w przeglądarce — `crc16.py` jest na serwerze, z Twoim opisem obok.

> **Ciekawostka — dlaczego trzy kroki, a nie jeden?** `add` → `commit` → `push` wydaje się biurokracją, ale każdy krok ma sens: `add` pozwala wybrać, KTÓRE zmiany wchodzą do paczki (możesz zmienić 5 plików, a zacommitować 2); `commit` tworzy trwały punkt w historii LOKALNIE (działa bez internetu); `push` synchronizuje z serwerem. Ta rozdzielność to supermoc gita, nie jego wada — docenisz ją, gdy pierwszy raz cofniesz zepsutą zmianę jednym poleceniem.

---

# 5. Uruchamiamy i bawimy się skryptem

```
python crc16.py
CRC16/CCITT-FALSE("123456789") = 0x29B1
```

**0x29B1** — to jest opublikowana, wzorcowa wartość dla tego wariantu CRC. Jeśli ją widzisz, implementacja jest poprawna. Pobaw się:

```
python crc16.py "Hello"
python crc16.py "Hella"
```

Porównaj wyniki: **jedna litera różnicy → kompletnie inny CRC**. To jest dokładnie ta właściwość, dla której CRC istnieje: przekłamanie choćby jednego bitu w transmisji daje inną sumę i odbiorca wie, że ramka jest uszkodzona.

> **Ciekawostka:** CRC to nie szyfrowanie ani "hash bezpieczeństwa" — jest trywialny do podrobienia celowo. Chroni przed PRZYPADKOWYM uszkodzeniem (zakłócenia na kablu), nie przed złośliwą modyfikacją. Do tej drugiej służą podpisy kryptograficzne — zupełnie inna liga i inny rozdział projektu.

---

# 6. Piszemy testy: test_crc16.py

## 6.1 Instalacja pytest (raz)

```
pip install pytest
```

## 6.2 Plik testów

Utwórz `test_crc16.py` obok `crc16.py`:

```python
"""Testy CRC16 — pytest znajdzie ten plik po nazwie test_*.py."""

from crc16 import crc16_ccitt_false


def test_wektor_standardowy():
    """Opublikowana wartosc wzorcowa dla CCITT-FALSE."""
    assert crc16_ccitt_false(b"123456789") == 0x29B1


def test_puste_dane():
    """CRC z zera bajtow = wartosc poczatkowa (nic jej nie zmienilo)."""
    assert crc16_ccitt_false(b"") == 0xFFFF


def test_jeden_bajt():
    """CRC16/CCITT-FALSE pojedynczego bajtu 'A' (0x41)."""
    assert crc16_ccitt_false(b"A") == 0xB915


def test_zmiana_bitu_zmienia_crc():
    """Wlasciwosc: rozne dane => rozny CRC (sens istnienia CRC)."""
    assert crc16_ccitt_false(b"Hello") != crc16_ccitt_false(b"Hella")


def test_wynik_miesci_sie_w_16_bitach():
    """CRC16 nigdy nie moze przekroczyc 0xFFFF."""
    for dane in [b"", b"x", b"123456789", bytes(range(256))]:
        assert 0 <= crc16_ccitt_false(dane) <= 0xFFFF
```

## 6.3 Uruchomienie

```
pytest
```

Wynik:

```
========================= test session starts =========================
collected 5 items

test_crc16.py .....                                              [100%]

========================== 5 passed in 0.02s ==========================
```

Każda kropka to jeden zaliczony test. Spróbuj też `pytest -v` — wypisze nazwy testów jedna pod drugą; przy dobrze nazwanych testach czyta się to jak listę wymagań, które kod spełnia.

## 6.4 Zauważ, jak różne są te testy — to celowe

- **Wektor wzorcowy** (`0x29B1`) — kotwica: przyszpila właściwy WARIANT algorytmu.
- **Przypadki brzegowe** (puste dane, jeden bajt) — tam mieszkają błędy off-by-one.
- **Test właściwości** (różne dane → różny CRC) — nie sprawdza konkretnej liczby, tylko sensowność zachowania.
- **Test niezmiennika** (wynik ≤ 0xFFFF) — łapie błąd z brakującym `&= 0xFFFF`, klasyk przy przenoszeniu kodu z C do Pythona.

Dobry zestaw testów to mieszanka wszystkich czterech rodzajów, nie pięć wariacji tego samego.

## 6.5 Commit i push

```
git add test_crc16.py
git commit -m "Dodaj testy CRC16 (wektor wzorcowy + przypadki brzegowe)"
git push
```

---

# 7. CI: uczymy GitHub uruchamiać nasze testy

Teraz najlepsze: GitHub będzie **sam** uruchamiał `pytest` po każdym pushu, na swoim serwerze, i pokazywał wynik przy każdym commicie. Mechanizm nazywa się **GitHub Actions**.

## 7.1 Plik przepisu

GitHub Actions szuka przepisów w folderze `.github/workflows/`. Utwórz plik `.github/workflows/testy.yml` (VS Code: New File → wpisz od razu całą ścieżkę `.github/workflows/testy.yml` — foldery utworzą się same):

```yaml
name: Testy                       # nazwa widoczna w zakladce Actions

on: [push, pull_request]          # KIEDY uruchamiac: po kazdym pushu
                                  # i przy kazdym pull requeście

jobs:
  testy-python:                   # nazwa zadania (dowolna)
    runs-on: ubuntu-latest        # GitHub wypozycza nam swieza maszynke
                                  # z Ubuntu (za darmo dla publicznych repo)
    steps:
      - name: Pobierz kod repo
        uses: actions/checkout@v4         # gotowy klocek: git clone naszego repo

      - name: Zainstaluj Pythona
        uses: actions/setup-python@v5     # gotowy klocek: instalacja Pythona
        with:
          python-version: "3.12"

      - name: Zainstaluj pytest
        run: pip install pytest           # run = zwykle polecenie terminala

      - name: Uruchom testy
        run: pytest -v                    # kod wyjscia != 0  =>  czerwony ❌
```

Przeczytaj to jak przepis kulinarny: "gdy ktoś pushnie → weź świeże Ubuntu → pobierz kod → zainstaluj Pythona → zainstaluj pytest → odpal testy". Klocki `uses:` to gotowe, publiczne akcje z marketplace'u GitHuba — nie piszesz instalacji Pythona ręcznie, bierzesz sprawdzony klocek.

> **Uwaga na pułapkę:** YAML jest wrażliwy na wcięcia (jak Python) i wcięcia muszą być SPACJAMI, nie tabulatorami. VS Code domyślnie wstawia spacje, więc nie powinno boleć — ale jeśli CI krzyczy o "mapping values" albo "could not find expected key", w 90% przypadków to skopane wcięcie.

## 7.2 Push i pierwszy pipeline

```
git add .github/workflows/testy.yml
git commit -m "Dodaj CI: automatyczne testy po każdym pushu"
git push
```

Teraz wejdź na stronę repo → zakładka **Actions** (u góry). Zobaczysz uruchomienie "Dodaj CI: automatyczne..." z żółtym kręcącym się kółkiem → po ~30–60 sekundach zmieni się w **zielony haczyk ✅**.

Kliknij w nie → kliknij zadanie `testy-python` → rozwiń krok "Uruchom testy". Zobaczysz **dokładnie ten sam wydruk pytest**, który miałeś w swoim terminalu — tylko że wykonany na maszynie GitHuba:

```
test_crc16.py::test_wektor_standardowy PASSED
test_crc16.py::test_puste_dane PASSED
...
========================== 5 passed in 0.02s ==========================
```

Od tej chwili zielony haczyk ✅ pojawia się też przy każdym commicie na liście commitów. To jest publiczny certyfikat: "ta wersja kodu przechodzi testy".

> **Ciekawostka:** maszyna, na której to się wykonało, żyła ~60 sekund i została skasowana. Każde uruchomienie CI dostaje świeży, czysty system — dlatego przepis musi instalować WSZYSTKO od zera (stąd krok z instalacją pytest). To brzmi rozrzutnie, ale to celowe: "u mnie działa, bo mam coś doinstalowane, o czym zapomniałem" nie ma prawa się wydarzyć na maszynie, która za każdym razem rodzi się czysta.

---

# 8. Psujemy kod — czyli jak wygląda CZERWONE CI i jak je czytać

To jest najważniejszy rozdział tutorialu. Zielone CI jest miłe, ale wartość CI objawia się, gdy jest **czerwone** — i musisz umieć to przeczytać bez paniki.

## 8.1 Wprowadzamy błąd (celowo)

Udajmy klasyczną pomyłkę: ktoś "poprawia" kod i zmienia wartość początkową CRC (myląc warianty algorytmu). W `crc16.py` zmień:

```python
    crc = 0xFFFF                          # wartosc poczatkowa
```

na:

```python
    crc = 0x0000                          # wartosc poczatkowa
```

To dokładnie różnica między wariantem CCITT-FALSE a wariantem XMODEM — jedna linijka, kod dalej "działa" (liczy JAKIEŚ CRC), tylko inne niż uzgodniono.

## 8.2 Najpierw zobacz to lokalnie

```
pytest
```

```
========================= test session starts =========================
collected 5 items

test_crc16.py F..F.                                              [100%]

============================== FAILURES ===============================
______________________ test_wektor_standardowy ________________________

    def test_wektor_standardowy():
>       assert crc16_ccitt_false(b"123456789") == 0x29B1
E       assert 12739 == 10673
E        +  where 12739 = crc16_ccitt_false(b'123456789')

test_crc16.py:8: AssertionError
==================== 2 failed, 3 passed in 0.03s ======================
```

Naucz się czytać ten wydruk, bo będziesz go widywać często:

- `F..F.` — mapka: test 1 padł (F), testy 2-3 przeszły (kropki), test 4 padł, test 5 przeszedł.
- Strzałka `>` pokazuje linię, która zawiodła.
- Linia `E assert 12739 == 10673` — **wyszło 12739 (0x31C3), oczekiwano 10673 (0x29B1)**. Pytest sam podstawił wartości — nie musisz nic drukować, widzisz obie liczby.
- `0x31C3` to akurat znany wynik wariantu XMODEM dla "123456789" — doświadczony człowiek po samej tej liczbie poznałby, JAKI błąd popełniono. Wektory wzorcowe działają jak odciski palców wariantów algorytmu.

Zwróć uwagę: 3 z 5 testów PRZESZŁY. Test właściwości ("różne dane → różny CRC") i test zakresu nie wykrywają tego błędu — bo zepsuty kod dalej liczy poprawny STRUKTURALNIE CRC, tylko w złym wariancie. Dlatego potrzebujesz wektora wzorcowego jako kotwicy. Gdybyś miał tylko testy właściwości, ten błąd przeszedłby niezauważony.

## 8.3 A teraz wysyłamy zepsuty kod — niech CI go złapie

W prawdziwym życiu nie testujesz lokalnie perfekcyjnie za każdym razem (spieszysz się, zmieniasz "tylko komentarz", jesteś pewny swego). Symulujemy to:

```
git add crc16.py
git commit -m "Popraw wartość początkową CRC"      ← ironia zamierzona
git push
```

Wejdź w **Actions**: uruchomienie kręci się... i po minucie **czerwony krzyżyk ❌**.

Na liście commitów Twój ostatni commit ma czerwone ❌. Jeśli masz w repo ustawiony mail — GitHub wysłał Ci powiadomienie "Run failed". Każdy, kto wejdzie na repo, widzi: ta wersja jest zepsuta.

## 8.4 Czytanie czerwonego logu

Actions → kliknij czerwone uruchomienie → `testy-python` → krok "Uruchom testy" jest podświetlony na czerwono → rozwiń:

Zobaczysz **identyczny wydruk pytest jak lokalnie** — z tą samą mapką `F..F.`, strzałkami i liczbami. To jest kluczowa intuicja: **CI nie jest żadną magią — to ten sam pytest, ten sam terminal, tylko wykonany automatycznie na cudzej maszynie**. Umiesz czytać lokalny wydruk = umiesz czytać CI.

> **Wskazówka na przyszłość:** gdy CI jest czerwone, a lokalnie "u Ciebie działa" — w 95% przypadków przyczyna to różnica środowisk: inna wersja Pythona, brakująca zależność w przepisie CI, plik którego zapomniałeś dodać do gita (`git status` pokaże go jako nieśledzony!). Log CI zawsze mówi prawdę o tym, co JEST w repo — nie o tym, co masz na dysku.

---

# 9. Naprawa, zielony pipeline, dobre nawyki

## 9.1 Naprawa

Przywróć w `crc16.py`:

```python
    crc = 0xFFFF                          # wartosc poczatkowa
```

Sprawdź lokalnie (`pytest` → `5 passed`), wyślij:

```
git add crc16.py
git commit -m "Przywróć poprawną wartość początkową CCITT-FALSE (0xFFFF)"
git push
```

Actions → zielony haczyk ✅. Historia commitów opowiada teraz uczciwą historię: działało → zepsuto (❌) → naprawiono (✅). To nie wstyd — to dokumentacja. Każdy projekt ma czerwone commity; projekty bez CI też je mają, tylko o nich nie wiedzą.

## 9.2 Dobre nawyki od pierwszego dnia

1. **pytest lokalnie PRZED pushem** — CI to siatka bezpieczeństwa, nie zastępstwo. Push zepsutego kodu blokuje też współpracownika, który właśnie pullował.
2. **Commituj małymi porcjami z opisowymi komunikatami.** "Poprawki" to zły komunikat; "Przywróć wartość początkową 0xFFFF (wariant CCITT-FALSE)" — dobry. Za pół roku to jedyne, co Ci powie, co się działo.
3. **Nigdy nie merguj przy czerwonym CI** — przy pracy zespołowej to żelazna zasada numer jeden.
4. **Nowa funkcja = nowy test w tym samym commicie.** Test dopisany "kiedyś" nie powstaje nigdy.
5. **Gdy znajdziesz buga — najpierw napisz test, który go łapie (czerwony), potem napraw (zielony).** Ten test zostaje na zawsze i pilnuje, żeby błąd nie wrócił. Nazywa się to testem regresyjnym.

---

# 10. Git w pracy dwuosobowej: pull, gałęzie, konflikty, cofanie, tagi

Do tej pory pracowałeś sam: `add → commit → push` i nikt Ci nie wchodził w drogę. Przy dwóch osobach dochodzi kilka mechanizmów — wszystkie proste, ale warto je przećwiczyć ZANIM będą potrzebne naprawdę.

## 10.1 git pull — druga połowa synchronizacji

Push wysyła Twoje zmiany na serwer. `git pull` pobiera zmiany, które w międzyczasie wypchnął kolega. Nawyk na całe życie:

```
rano / przed rozpoczęciem pracy:   git pull
po skończeniu porcji pracy:        git push
```

Większość początkujących problemów z gitem ("nie mogę pushnąć", "mam jakiś dziwny merge") bierze się z jednego: pracy na nieaktualnej wersji. Częsty pull = mało niespodzianek.

Jeśli przy pushu zobaczysz odmowę `rejected... fetch first` — to właśnie to: kolega wypchnął coś przed Tobą. Rozwiązanie: `git pull`, ewentualnie rozwiąż konflikt (10.3), potem `git push`.

## 10.2 Gałęzie (branches) — praca obok siebie bez deptania

Gałąź to równoległa linia historii. Zamiast commitować prosto do `main`, tworzysz gałąź na swoje zadanie, pracujesz na niej, a na koniec zmiany wracają do `main` przez Merge Request / Pull Request:

```
git checkout -b framer-python      # utwórz gałąź i przejdź na nią
...edycja, git add, git commit...   # commity lądują na gałęzi
git push -u origin framer-python    # wypchnij gałąź na serwer
                                    # (-u tylko za pierwszym razem)
```

Potem na GitHubie/GitLabie klikasz **"Create Pull Request"** (GitHub) / **"Create Merge Request"** (GitLab) — kolega widzi Twoje zmiany jako czytelną różnicę, CI je testuje, po zielonym ✅ klikacie "Merge" i zmiany wchodzą do `main`.

Efekt tego modelu:

- `main` jest ZAWSZE w stanie działającym — każdy może z niego bezpiecznie startować
- nie wchodzicie sobie w kod w trakcie pracy
- każda zmiana przechodzi przez CI zanim trafi do wspólnej bazy

Przy dwóch osobach wystarczy najprostszy wariant: **main + krótkie gałęzie na zadania** (dzień-trzy pracy, nie tygodnie). Żadnych rozbudowanych "git flow" z develop/release/hotfix — to narzuty dla dużych zespołów.

Przydatne przy gałęziach:

```
git branch                  # lista gałęzi (gwiazdka = jesteś tutaj)
git checkout main           # wróć na main
git pull                    # zaktualizuj main
git checkout -b nowe-cos    # nowa gałąź OD aktualnego main
git branch -d stara-galaz   # usuń scaloną gałąź (porządek)
```

## 10.3 Konflikty — nieuniknione, ale niegroźne

Konflikt powstaje, gdy obaj zmienicie **tę samą linię tego samego pliku**. Git nie zgaduje, kto ma rację — zatrzymuje się i prosi człowieka o decyzję.

### Jak to wygląda

Przy `git pull` albo merge zobaczysz:

```
CONFLICT (content): Merge conflict in crc16.py
Automatic merge failed; fix conflicts and then commit the result.
```

A w pliku pojawią się znaczniki:

```python
<<<<<<< HEAD
    crc = 0xFFFF    # wartosc poczatkowa CCITT-FALSE
=======
    crc = 0xFFFF    # init value (CCITT-FALSE variant)
>>>>>>> framer-python
```

Czytanie: między `<<<<<<< HEAD` a `=======` jest **Twoja** wersja; między `=======` a `>>>>>>>` — wersja **przychodzą­ca** (kolegi). 

### Jak rozwiązać

1. Otwórz plik w VS Code — konflikt jest podświetlony, nad nim przyciski: **Accept Current** (zostaw moje) / **Accept Incoming** (weź kolegi) / **Accept Both** — albo po prostu ręcznie zredaguj linię do ostatecznej postaci i usuń wszystkie trzy znaczniki.
2. Zapisz plik, potem:

```
git add crc16.py
git commit                # git sam zaproponuje komunikat "Merge..."
git push
```

**Ważne:** rozwiązanie konfliktu to decyzja merytoryczna, nie mechaniczna. Zanim klikniesz "Accept", zrozum OBIE wersje — czasem poprawna odpowiedź to połączenie obu, a czasem szybki telefon do kolegi "słuchaj, obaj ruszaliśmy framera — która wersja timeoutu jest właściwa?".

### Ćwiczenie: wywołaj konflikt na sucho (15 minut, mocno polecane)

Najlepiej oswoić konflikt w warunkach, gdzie nic nie ryzykujesz. W swoim repo `crc-tutorial`:

```
# 1. utwórz gałąź i zmień komentarz w crc16.py
git checkout -b test-konfliktu
# (zmień w edytorze linię "# wartosc poczatkowa" na "# wersja A")
git add crc16.py && git commit -m "Wersja A komentarza"

# 2. wróć na main i zmień TĘ SAMĄ linię inaczej
git checkout main
# (zmień tę samą linię na "# wersja B")
git add crc16.py && git commit -m "Wersja B komentarza"

# 3. spróbuj scalić — BUM, kontrolowany konflikt
git merge test-konfliktu
```

Rozwiąż go w VS Code jak wyżej. Pierwszy konflikt wygląda strasznie, trzeci jest rutyną — dlatego warto zaliczyć pierwszy na niby.

### Jak mieć konfliktów mało

- krótkie gałęzie, częsty pull
- podział pracy per plik/moduł (Ty framer, kolega symulator — zero wspólnych linii)
- pliki generowane i formatowanie automatyczne (formatter typu black) — mniej "kosmetycznych" różnic

## 10.4 Cofanie — trzy komendy na trzy sytuacje

**Sytuacja 1: zepsułem plik, jeszcze nie commitowałem.**

```
git restore crc16.py        # przywróć plik do stanu z ostatniego commita
```

Zmiany przepadają bezpowrotnie — upewnij się, że tego chcesz (`git diff` pokaże, co stracisz).

**Sytuacja 2: chcę poprawić ostatni commit** (literówka w kodzie albo w opisie, zapomniany plik):

```
# popraw pliki w edytorze
git add poprawiony_plik.py
git commit --amend          # "dolej" do ostatniego commita zamiast tworzyć nowy
```

Bezpieczne, dopóki commit **nie został jeszcze wypchnięty**. Po pushu — nie amenduj, patrz sytuacja 3.

**Sytuacja 3: commit już wypchnięty i okazał się zły.**

```
git log --oneline           # znajdź hash zepsutego commita, np. a1b2c3d
git revert a1b2c3d          # utwórz NOWY commit odwracający tamten
git push
```

Historia zostaje uczciwa: widać, że coś weszło i zostało wycofane. 

> **Żelazna zasada:** na wspólnych gałęziach **nigdy `git push --force`** (przepisywanie wypchniętej historii). To jedyny sposób, żeby git naprawdę narobił szkód w zespole — kolega, który ma starą wersję historii, ląduje w stanie niemożliwym do automatycznego pogodzenia. Jeśli kiedykolwiek git podpowiada Ci force-push na main — zatrzymaj się i przemyśl, co poszło nie tak krok wcześniej.

## 10.5 Tagi — etykiety wersji

Tag to trwała, nazwana etykieta przyklejona do konkretnego commita — "to jest wersja 0.1.0":

```
git tag v0.1.0              # otaguj aktualny commit
git push --tags             # tagi NIE wychodzą ze zwykłym push — trzeba jawnie
git tag                     # lista tagów
git checkout v0.1.0         # obejrzyj kod dokładnie w tej wersji
```

W przeciwieństwie do gałęzi tag się nie przesuwa — `v0.1.0` wskazuje ten sam commit dziś i za pięć lat. Dlatego to tagami wersjonuje się kontrakty (repo `proto/` w projekcie vendingowym: v0.1.0 → v0.2.x) i wydania — a inne repozytoria "przypinają się" do tagu, nie do gałęzi, żeby nic im się nie zmieniło pod nogami.

## 10.6 Codzienne okulary: log, diff, status

```
git status                  # co zmienione, co dodane, na jakiej gałęzi jestem
git diff                    # DOKŁADNIE które linie zmieniłem (przed git add)
git diff --staged           # to samo dla plików już po git add
git log --oneline           # historia w skrócie: hash + opis, jeden wiersz na commit
git log --oneline --graph --all   # + rysunek gałęzi (ładnie widać merge)
```

Ta piątka to 90% "czytania" gita. Nawyk: `git diff` przed KAŻDYM commitem — 10 sekund, które łapie zapomniane printy debugowe i przypadkowe zmiany.

## 10.7 Czego NIE musisz umieć na start

`rebase`, `cherry-pick`, `stash`, `bisect`, hooki — wszystko to istnieje, bywa przydatne i kiedyś po to sięgniesz. Ale przy dwóch osobach i krótkich gałęziach zwyczajnie nie będzie potrzebne. Nie ucz się gita "na zapas" — ucz się od problemu do problemu. Git ma opinię trudnego głównie dlatego, że ludzie próbują połknąć go w całości; podzbiór z tego rozdziału obsługuje spokojnie 95% codziennej pracy zespołowej.

---

# 11. Aneks: to samo w GitLab CI

W firmowym GitLabie zamiast `.github/workflows/testy.yml` tworzysz w korzeniu repo plik `.gitlab-ci.yml`:

```yaml
stages:
  - test

testy-python:
  stage: test
  image: python:3.12          # tu wskazujesz gotowy obraz Dockera z Pythonem
  script:                     # odpowiednik "steps", ale bez klockow uses:
    - pip install pytest
    - pytest -v
```

Różnice w pigułce:

| | GitHub Actions | GitLab CI |
|---|---|---|
| Plik | `.github/workflows/*.yml` | `.gitlab-ci.yml` (korzeń repo) |
| Maszyny | GitHub daje swoje (darmowe dla public) | Twój **runner** — trzeba go mieć zainstalowanego (self-hosted GitLab!) |
| Środowisko | `runs-on: ubuntu-latest` + klocki `uses:` | obraz Dockera w `image:` |
| Wynik | zakładka Actions, ✅/❌ przy commitach | zakładka Build → Pipelines, ✅/❌ przy commitach i w MR |

Filozofia, wydruki pytest, czytanie czerwonych logów — **identyczne**. Nauczyłeś się jednego, umiesz oba.

---

# 12. Ciekawostki i pytania, które zada każdy początkujący

**"Czy CI kosztuje?"** Dla publicznych repo na GitHubie — nie, minuty są nielimitowane. Prywatne repo mają darmowy pakiet 2000 minut/miesiąc (nasz pipeline zużywa ~1 minutę na push, czyli limit jest praktycznie nieosiągalny przy nauce). Self-hosted GitLab: płacisz prądem własnego runnera.

**"Co jeśli pushnę 5 razy pod rząd?"** Uruchomi się 5 pipeline'ów. Nic złego się nie stanie — najwyżej poczekają w kolejce. Ale to sygnał, żeby commitować przemyślanymi porcjami.

**"Czy mogę uruchomić CI bez pushowania?"** Sedno CI polega na tym, że reaguje na push — ale lokalnie masz przecież dokładnie to samo: `pytest`. Przepis CI to tylko automatyzacja tego, co robisz ręcznie.

**"Skąd CI wie, że testy padły?"** Z **kodu wyjścia** procesu. Każdy program w terminalu kończy się liczbą: 0 = sukces, cokolwiek innego = błąd. `pytest` zwraca 0 przy komplecie zaliczeń i 1, gdy coś padło. CI patrzy tylko na tę liczbę — cała reszta (kolory, logi) to prezentacja dla człowieka. Możesz to podejrzeć lokalnie: po `pytest` wpisz `echo $LASTEXITCODE` (PowerShell) albo `echo $?` (bash).

**"Dlaczego test z b'123456789', a nie '123456789'?"** Literka `b` przed cudzysłowem tworzy **bajty** zamiast tekstu. CRC działa na bajtach — tekst musiałby najpierw zostać zakodowany (`.encode()`). W protokołach binarnych zawsze myślisz bajtami, nie znakami.

**"Co jeszcze potrafi pytest?"** Dużo: parametryzacja (jeden test, wiele zestawów danych — idealne pod wektory testowe), fixtures (wspólne przygotowanie środowiska), pomiar pokrycia kodu (`pytest --cov` — ile % linii kodu testy w ogóle dotknęły). Na start nie potrzebujesz nic z tego — `assert` + konwencja nazw zawiozą Cię zaskakująco daleko.

**"Kiedy wiem, że mam dość testów?"** Praktyczna heurystyka dla początkującego: (1) każdy wektor wzorcowy/kontrakt, (2) przypadki brzegowe (puste, pojedynczy element, maksimum), (3) każdy naprawiony bug ma swój test. Nie licz procentów pokrycia na starcie — licz, czy test WYKRYŁBY błąd, którego się boisz. Zrobiliśmy dokładnie taki eksperyment w rozdziale 8: wprowadziliśmy realny błąd i sprawdziliśmy, które testy go łapią. To najlepszy sprawdzian jakości testów, jaki istnieje — od czasu do czasu psuj kod celowo i patrz, czy siatka działa.

---

## Podsumowanie — co teraz umiesz

```
[✓] Założyć repo na GitHub i sklonować je na komputer
[✓] Cykl pracy: edycja → git add → commit → push
[✓] Napisać moduł Pythona z blokiem __main__ i uruchomić go z argumentem
[✓] Napisać testy pytest (konwencje test_*, assert) i je uruchomić
[✓] Czytać wydruk pytest — mapka F../kropki, strzałki, porównanie wartości
[✓] Skonfigurować CI (GitHub Actions) i rozumieć, że to "zdalny pytest"
[✓] Przeczytać czerwony pipeline bez paniki i naprawić przyczynę
[✓] Pracować we dwóch: pull, gałęzie + MR/PR, rozwiązać konflikt
[✓] Cofać zmiany (restore / --amend / revert) i tagować wersje
[✓] Przenieść tę wiedzę na GitLab CI jedną tabelką różnic
```

Naturalne następne kroki: przenieś wektory testowe do pliku JSON (jak w projekcie vendingowym — `testvectors/crc16.json` + jeden test, który je wczytuje), dodaj do repo drugi moduł (COBS!) z własnymi testami, i zobacz jak CI pilnuje obu naraz.

# CV – Łukasz Spaczyński

Generator profesjonalnego CV w PDF, w dwóch wersjach językowych (EN / PL), z jednego szablonu.

## Struktura

```
data/en.yaml        treść wersji angielskiej
data/pl.yaml        treść wersji polskiej
template/cv.html.j2 szablon HTML (Jinja2)
template/cv.css     wygląd (A4, dwie kolumny)
build.py            render YAML → HTML → PDF (Chromium przez Playwright)
build/              pośrednie pliki HTML i podglądy (ignorowane w git)
out/                gotowe PDF-y
```

## Budowanie

```sh
python3 build.py        # obie wersje
python3 build.py pl     # tylko polska
```

Wynik: `out/Lukasz-Spaczynski-CV-EN.pdf` i `out/Lukasz-Spaczynski-CV-PL.pdf`.

Podgląd PNG do szybkiej kontroli:

```sh
pdftoppm -png -r 70 out/Lukasz-Spaczynski-CV-EN.pdf build/preview-EN
```

## Wymagania

Python 3.13 z pakietami `jinja2`, `pyyaml`, `pypdf`, `playwright` (z pobranym Chromium: `python3 -m playwright install chromium`).
Do podglądów opcjonalnie `poppler` (`brew install poppler`).

## Układ

Jedna kolumna, dwie strony A4 (ATS-friendly). Kolejność: nagłówek z kontaktem, profil, umiejętności
(cztery grupy kompetencyjne, bez numerów wersji), doświadczenie w porządku odwrotnie chronologicznym,
sekcja `ai` (praca z agentami AI, opcjonalna), projekty hobbystyczne (`projects`, opcjonalne),
wykształcenie i języki obok siebie, klauzula RODO (tylko w wersji PL – pole `consent` w EN jest puste).
Stopka z nazwiskiem i numerem strony dodawana przez Chromium. Wpisy doświadczenia nie łamią się
między stronami (`break-inside: avoid`).

Po każdej zmianie treści sprawdź liczbę stron: `pdfinfo out/*.pdf | grep Pages` – powinno być 2.
Gdy strona się nie domyka, zmierz zamiast zgadywać: `pdftotext -f 2 -l 2 -bbox-layout out/<plik>.pdf -`
daje współrzędne linii w punktach (dół obszaru treści A4 przy marginesie 17 mm to ~793,7 pt).

Pułapka: jeśli nagłówek (zdjęcie + niełamliwe stanowisko + kontakt) stanie się szerszy niż strona, Chromium
po cichu przeskalowuje cały dokument w dół, żeby zmieścić szerokość. Objaw: mniejsza czcionka i więcej treści
na stronie 1 niż zwykle. Zabezpieczenie: `.head { overflow: hidden }`, niełamliwe nazwisko i stanowisko, a lokalizacja z trybem pracy
(`person.location` · `person.availability`) renderowana pod stanowiskiem po lewej, nie w prawej kolumnie kontaktu,
która obok zdjęcia jest za wąska.
Druga pułapka: wpisy doświadczenia mają `break-inside: avoid`, więc gdy blok Preglife nie mieści się pod
umiejętnościami, przeskakuje w całości na stronę 2 i robi trzecią stronę.

## Zdjęcie

Opcjonalne pole `person.photo` (ścieżka względem `build/`, np. `../assets/photo.jpg`) wstawia okrągłe zdjęcie
po lewej stronie nagłówka. Używane tylko w wersji PL; w EN celowo pominięte (rynek UK/EU).
Źródło zdjęcia przycięte do głowy i ramion skryptem Pillow do `assets/photo.jpg`.

## Metadane PDF

Po wyrenderowaniu `build.py` nadpisuje słownik informacji PDF (pypdf): tytuł, autor, temat (nagłówek),
słowa kluczowe (umiejętności bez nawiasów), a pola Creator i Producer dostają nazwisko zamiast nazwy narzędzia.

## Edycja treści

Cała treść jest w plikach YAML. Szablon nie zawiera tekstu – zmiana treści nie wymaga ruszania HTML/CSS.
Pole `url` w projektach i wpisach doświadczenia jest opcjonalne (nazwa firmy staje się linkiem). Wpis z `compact: true` renderuje rolę, firmę i daty w jednym wierszu, bez punktów (tak jest opisany okres PHP 2008–2012). Sekcje są renderowane w kolejności zdefiniowanej w szablonie.
Wpis doświadczenia może zamiast `bullets` mieć listę `phases` (podbloki z własnym `title`, `start`, `end`, opcjonalnym `note` i `bullets`) – tak jest opisany Preglife: osobno okres React Native i osobno natywny iOS, pod jednym nagłówkiem pracodawcy. Podblok może dzielić się między strony, ale jego nagłówek z notą trzyma się razem z pierwszym punktem, więc na stronie nie zostaje osierocony tytuł fazy.

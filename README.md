# milanapmu.uae — strona wizytówkowa

Statyczna, dwujęzyczna (EN / RU) strona dla **Milana PMU Dubai** — permanentny makijaż
i kamuflaż blizn, z dojazdem do klientki w Dubaju i Szardży.

Bez build stepu i bez zależności: otwierasz `index.html` i strona działa.
Fonty są hostowane lokalnie, więc działa też offline.

---

## Uruchomienie

```bash
# najprościej
open index.html

# albo lokalny serwer (potrzebny, jeśli chcesz testować ścieżki jak na produkcji)
python3 -m http.server 8000
```

## Struktura

```
index.html  services.html  results.html  pricing.html
about.html  faq.html       contact.html          ← wersja angielska (root)
ru/…                                             ← wersja rosyjska, te same strony
assets/
  css/tokens.css      ← cała warstwa wizualna: kolory, typografia, odstępy, ruch
  css/fonts.css       ← @font-face dla lokalnych fontów
  css/site.css        ← style komponentów
  js/site.js          ← nawigacja, reveal, suwaki przed/po, dobór pigmentu, formularz
  fonts/              ← Manrope + JetBrains Mono (latin + cyrylica), OFL
  img/                ← placeholdery do podmiany na prawdziwe zdjęcia
tools/
  build.py            ← generator: jeden szablon → EN w root + RU w /ru/
  content_en.py       ← cała treść angielska
  content_ru.py       ← cała treść rosyjska
  make_placeholders.py← generator placeholderów graficznych
robots.txt  sitemap.xml
```

## Jak edytować

Dwie drogi — wybierz jedną i trzymaj się jej:

1. **Przez generator (zalecane przy większych zmianach).** Edytujesz `tools/content_en.py`
   i `tools/content_ru.py`, potem `python3 tools/build.py`. Obie wersje językowe
   pozostają zsynchronizowane strukturalnie.
2. **Bezpośrednio w HTML.** Wtedy usuń katalog `tools/` — ponowne uruchomienie
   generatora nadpisze ręczne zmiany.

Numery telefonu, adres e-mail, linki i domena siedzą w jednym miejscu:
`SITE` na górze `tools/build.py`.

## Design system

Wszystkie kolory, rozmiary i czasy animacji są w `assets/css/tokens.css`.
Zmiana palety = zmiana kilku wartości w tym jednym pliku.

| Rola | Token | Wartość |
|---|---|---|
| Akcent (przyciski, linia pod headerem) | `--gold` | `#DFA615` |
| Złoty tekst/ikony na jasnym tle | `--gold-text` | `#8A6108` |
| Złoty tekst na ciemnym tle | `--gold-light` | `#F0C960` |
| Ciemne pasma sekcji | `--graphite` / `--graphite-deep` | `#5C5450` / `#322D2A` |
| Tło strony | `--silk` | `#F4F2EF` |
| Tekst | `--ink` / `--ink-body` | `#141210` / `#45403B` |
| Skala odcieni skóry (kafle pigmentu) | `--tone-01` … `--tone-08` | — |

**Typografia:** Manrope (nagłówki i tekst) + JetBrains Mono (etykiety, kody, ceny, dni gojenia).
Wersaliki występują tylko w dwóch miejscach: w nagłówkach display i w foncie mono.
Wszystko, co się klika, jest pisane normalnie — Manrope ma zbyt luźne światła
przy wersalikach w parach typu „TS" (ROZDZIELA słowa RESULTS i WHATSAPP).

**Element sygnaturowy:** pasek odcieni skóry i interaktywny dobór pigmentu na stronie
głównej. To nie ozdobnik — dobór pigmentu pod podton to faktyczne rzemiosło w kamuflażu blizn
i to jedyna rzecz, której konkurencja nie ma.

## Interakcje

| Zachowanie | Jak działa | Gdy się nie uda |
|---|---|---|
| Ciężki smooth scroll | [Lenis](https://lenis.darkroom.engineering/) z CDN, `lerp: 0.085`, pętla `requestAnimationFrame` | brak Lenisa (`typeof Lenis === "undefined"`) → natywne przewijanie, strona działa normalnie |
| Linki kotwiczne | `lenis.scrollTo(el, { offset })`, offset liczony z realnej wysokości headera | `window.scrollTo({ behavior: "smooth" })` |
| Przejścia między stronami | treść `<main>` gaśnie i unosi się, `#veil` zakrywa całość (320 ms), po wczytaniu treść wraca z dołu (460 ms). Header i stopka nie ruszają się — przejście czyta się jak jedna strona, która się zmienia | link nawiguje natychmiast |
| Zmiana języka | to samo, ale `#veil` w trybie `--loading`: rozmycie tła, znak firmowy i pasek postępu, ~680 ms | jak wyżej |
| Popup „Book" | natywny `<dialog>` — pułapka focusa, Esc i `::backdrop` z pudełka | przycisk to prawdziwy link do WhatsApp i tak działa |
| FAQ | animacja wysokości przez Web Animations API, `<details>` zostaje źródłem prawdy | natywne rozwijanie bez animacji |

Jeśli nowa strona wczytuje się dłużej niż 500 ms, zwykła zasłona sama zamienia się
w tryb `--loading` — zamiast pustego ekranu widać znak firmowy i pasek.

Przy otwartym menu mobilnym i przy otwartym popupie leci `lenis.stop()`, przy zamknięciu
`lenis.start()`; bez Lenisa blokadę przejmuje klasa `is-locked` na `<html>`.

**`prefers-reduced-motion`**: Lenis w ogóle się nie inicjalizuje, przejścia i animacja FAQ
są pomijane, nawigacja jest natychmiastowa.

**Uwaga o CDN:** Lenis to jedyny zewnętrzny zasób na stronie (fonty są lokalne).
Bez internetu strona nadal działa — po prostu przewija się natywnie. Jeśli wolisz zero
zależności zewnętrznych, wgraj `lenis.min.js` do `assets/js/` i podmień `src` w `tools/build.py`.

## Zdjęcia

W `assets/img/` są placeholdery (miękkie gradienty w palecie marki, z dyskretną
etykietą co ma być na danym kadrze). **Podmieniasz plik pod tą samą nazwą** —
nic w kodzie nie wymaga zmiany. Zalecane: WebP, szerokość 1600 px dla kadrów
sekcyjnych, 2400 px dla hero.

| Plik | Kadr |
|---|---|
| `hero.svg` | zabieg w trakcie, kadr poziomy, dużo miejsca po prawej na tekst |
| `service-brows/lips/camo.svg` | po jednym kadrze na usługę, 4:3 |
| `ba-*-before/after.svg` | pary przed/po, ten sam kadr i to samo światło |
| `portrait.svg` | Milana przy pracy, pion |
| `home-service.svg` | rozłożone stanowisko u klientki |
| `studio.svg` | sterylne, jednorazowe akcesoria |
| `detail-pigments.svg` | próbki pigmentów przy skórze |

## Do potwierdzenia z klientką (placeholdery)

- [ ] **Numer telefonu / WhatsApp** — teraz `+971 50 000 0000` (`SITE` w `tools/build.py`)
- [ ] **Adres e-mail** — teraz `hello@milanapmu.ae`
- [ ] **Domena** — teraz `https://milanapmu.ae` (wpływa na `canonical`, `hreflang`, `sitemap.xml`)
- [ ] **Godziny pracy** — teraz „By appointment" / „По записи"
- [ ] **Ceny poza 350 AED** — korekta, kamuflaż, kamuflaż na głowie i przekrycie
      starego PMU mają „On request"; trzeba wpisać realne widełki albo zostawić
- [ ] **Kwota depozytu** — treść mówi, że depozyt potwierdza termin, ale nie podaje kwoty
- [ ] **Czasy trwania i trwałość** — wpisane wartości branżowe (2,5–3 h, 1–2 lata itd.),
      Milana powinna je potwierdzić
- [ ] **Doświadczenie / szkolenia / certyfikaty** — świadomie nie wymyślone; strona
      „O mnie" jest napisana bez tych danych i zyska na ich dodaniu
- [ ] **Opinie klientek** — trzy miejsca na stronie głównej mają widoczne
      placeholdery. Wstawiamy tylko prawdziwe cytaty, za zgodą klientek.
- [ ] **Zdjęcia** — wszystkie (lista wyżej)

## Wdrożenie

Dowolny statyczny hosting: Netlify, Vercel, Cloudflare Pages, GitHub Pages albo zwykły FTP.
Wgrywasz całą zawartość repozytorium poza `tools/`.

Po ustawieniu domeny podmień `SITE["domain"]` i przebuduj — inaczej `canonical`,
`hreflang` i `sitemap.xml` będą wskazywać na placeholder.

## Dostępność i jakość

- Kontrast tekstu ≥ 4,5:1 w każdej kombinacji, elementy UI ≥ 3:1
- Cele dotykowe ≥ 24×24 px (WCAG 2.2), przyciski i pola ≥ 48 px
- Pełna obsługa klawiatury, widoczny focus, `skip link`
- `prefers-reduced-motion` respektowane
- Poprawna hierarchia nagłówków, `alt` na każdej grafice, `lang` i `hreflang`
- Bez poziomego scrolla od 320 px w górę
- Strona działa bez JS: animacje są warunkowane klasą `.js`, „Book" pozostaje linkiem do
  WhatsApp, FAQ rozwija się natywnie, a nakładka przejścia nigdy się nie pokazuje

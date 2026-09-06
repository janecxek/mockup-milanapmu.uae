#!/usr/bin/env python3
"""Build the static site.

One set of templates, two languages: English at the root, Russian under /ru/.
Both are real HTML files with hreflang links, so each language is indexable on
its own URL — no client-side translation.

    python3 tools/build.py

Content lives in CONTENT below. Edit it here and rebuild, or edit the emitted
HTML directly and stop using this script — both are valid ways to work.
"""
import html
import pathlib
import re
from urllib.parse import quote

ROOT = pathlib.Path(__file__).resolve().parents[1]

# --- Things the client must confirm before launch ---------------------------
# Placeholders are marked TODO in README.md. Change them here once.
SITE = {
    "brand": "Milana",
    "brand_sub": "PMU · DUBAI",
    "phone_display": "+971 50 000 0000",     # TODO real number
    "phone_e164": "+971500000000",           # TODO real number
    "whatsapp": "971500000000",              # TODO real number
    "email": "hello@milanapmu.ae",           # TODO real address
    "instagram": "https://www.instagram.com/milanapmu.uae/",
    "instagram_handle": "@milanapmu.uae",
    "founder": "https://www.instagram.com/milanulanbekova/",
    "founder_handle": "@milanulanbekova",
    "domain": "https://milanapmu.ae",        # TODO real domain
}

PAGES = ["index", "services", "results", "pricing", "about", "faq", "contact"]

# Intrinsic sizes of the shipped artwork. Emitted as width/height on every
# <img> so the browser reserves the right box before the file arrives.
DIMS = {
    "hero.webp": (1672, 941),
    "portrait.webp": (1024, 1536),
    "studio.webp": (1400, 933),
    "home-service.webp": (1400, 933),
    "detail-pigments.webp": (1400, 933),
    "service-brows.webp": (1400, 788),
    "service-lips.webp": (1400, 788),
    "service-camo.webp": (1400, 788),
    "gallery-brows-01.webp": (900, 1125),
    "gallery-lips-01.webp": (900, 1350),
    "gallery-lips-02.webp": (900, 1200),
    "gallery-face-01.webp": (900, 1190),
    "gallery-face-02.webp": (900, 1195),
    "gallery-face-03.webp": (900, 1592),
}


def dims(name):
    wh = DIMS.get(name)
    return f' width="{wh[0]}" height="{wh[1]}"' if wh else ""

ICONS = {
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "whatsapp": '<svg viewBox="0 0 32 32" fill="currentColor" aria-hidden="true"><path d="M16.02 3.2c-7.06 0-12.8 5.74-12.8 12.8 0 2.26.6 4.47 1.73 6.42L3.2 28.8l6.55-1.71a12.75 12.75 0 0 0 6.27 1.6h.01c7.06 0 12.8-5.74 12.8-12.8s-5.75-12.69-12.81-12.69zm0 23.04h-.01a10.6 10.6 0 0 1-5.4-1.48l-.39-.23-4.02 1.05 1.07-3.92-.25-.4a10.57 10.57 0 0 1-1.62-5.65c0-5.86 4.77-10.63 10.63-10.63 2.84 0 5.5 1.11 7.51 3.12a10.56 10.56 0 0 1 3.11 7.52c0 5.86-4.77 10.62-10.63 10.62z"/><path d="M21.86 18.7c-.32-.16-1.89-.93-2.18-1.04-.29-.11-.5-.16-.71.16s-.82 1.03-1 1.25c-.19.21-.37.24-.68.08-.32-.16-1.34-.49-2.55-1.57-.94-.84-1.58-1.87-1.77-2.19-.18-.32-.02-.49.14-.65.15-.14.32-.37.48-.56.16-.19.21-.32.32-.53.11-.21.05-.4-.03-.56-.08-.16-.71-1.72-.98-2.35-.26-.62-.52-.53-.71-.54h-.61c-.21 0-.56.08-.85.4-.29.32-1.11 1.09-1.11 2.64s1.14 3.06 1.29 3.27c.16.21 2.24 3.42 5.43 4.8.76.33 1.35.52 1.81.67.76.24 1.45.21 2 .13.61-.09 1.89-.77 2.15-1.52.27-.75.27-1.38.19-1.52-.08-.13-.29-.21-.61-.37z"/></svg>',
    "instagram": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="3.6"/><circle cx="17.2" cy="6.8" r="1.1" fill="currentColor" stroke="none"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="4.5" width="19" height="15" rx="2.5"/><path d="m3 7 9 6 9-6"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.2 2"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2.6 4.5 5.7v5.6c0 4.7 3.2 8.4 7.5 10.1 4.3-1.7 7.5-5.4 7.5-10.1V5.7z"/><path d="m9 12 2.2 2.2L15.5 10"/></svg>',
    "home": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3.5 10.5 12 3.5l8.5 7"/><path d="M5.5 9.6V20h13V9.6"/><path d="M10 20v-5.5h4V20"/></svg>',
    "drop": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3s5.5 6.1 5.5 9.8A5.5 5.5 0 0 1 12 18.3a5.5 5.5 0 0 1-5.5-5.5C6.5 9.1 12 3 12 3z"/></svg>',
    "close": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>',
    "form": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="3" width="16" height="18" rx="2.5"/><path d="M8.5 8.5h7M8.5 12.5h7M8.5 16.5h4"/></svg>',
    "quote": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M9.4 5.6C6.3 7 4.4 9.7 4.4 13v5.4h6.4V13H7.6c0-2.3 1-3.9 3-4.9zM20.4 5.6C17.3 7 15.4 9.7 15.4 13v5.4h6.4V13h-3.2c0-2.3 1-3.9 3-4.9z"/></svg>',
    "mark": '<svg viewBox="0 0 40 40" fill="none" aria-hidden="true"><circle cx="20" cy="20" r="17" stroke="var(--gold)" stroke-width="3.4" stroke-linecap="round" stroke-dasharray="80 27" transform="rotate(-28 20 20)"/><path d="M20 12.5v15M12.5 20h15" stroke="var(--gold)" stroke-width="3.4" stroke-linecap="round"/></svg>',
}

def e(s):
    return html.escape(str(s), quote=True)

def slug_href(page, lang, from_lang):
    """Link to `page` in `lang`, written relative to a document in `from_lang`."""
    name = "index.html" if page == "index" else page + ".html"
    if lang == "en":
        return name if from_lang == "en" else "../" + name
    return "ru/" + name if from_lang == "en" else name


# --- Shell ------------------------------------------------------------------

def head(lang, page, C):
    meta = C["meta"][page]
    asset = "assets/" if lang == "en" else "../assets/"
    canon = SITE["domain"] + ("/" if lang == "en" else "/ru/") + ("" if page == "index" else page + ".html")
    alt_en = SITE["domain"] + "/" + ("" if page == "index" else page + ".html")
    alt_ru = SITE["domain"] + "/ru/" + ("" if page == "index" else page + ".html")
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(meta['title'])}</title>
<meta name="description" content="{e(meta['desc'])}">
<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="en" href="{alt_en}">
<link rel="alternate" hreflang="ru" href="{alt_ru}">
<link rel="alternate" hreflang="x-default" href="{alt_en}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(meta['title'])}">
<meta property="og:description" content="{e(meta['desc'])}">
<meta property="og:locale" content="{'en_AE' if lang == 'en' else 'ru_RU'}">
<script>(function(d){{var h=d.documentElement;h.classList.add('js');try{{var m=sessionStorage.getItem('pmu-enter');if(m){{sessionStorage.removeItem('pmu-enter');h.classList.add('is-entering');if(m==='lang')h.classList.add('is-entering-lang');}}}}catch(e){{}}}})(document)</script>
<link rel="stylesheet" href="{asset}css/fonts.css">
<link rel="stylesheet" href="{asset}css/tokens.css">
<link rel="stylesheet" href="{asset}css/site.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'><circle cx='20' cy='20' r='17' fill='none' stroke='%23DFA615' stroke-width='4'/><path d='M20 12v16M12 20h16' stroke='%23DFA615' stroke-width='4'/></svg>">
</head>
<body>
<a class="skip-link" href="#main">{e(C['ui']['skip'])}</a>
<div class="veil" id="veil" aria-hidden="true">
  <div class="veil__inner">
    <span class="veil__mark">{ICONS['mark']}</span>
    <span class="veil__brand">
      <span class="brand__name" style="font-size:1.5rem">{e(SITE['brand'])}</span>
      <span class="brand__sub">{e(SITE['brand_sub'])}</span>
    </span>
    <span class="veil__bar"><i></i></span>
  </div>
</div>
"""


def header(lang, page, C):
    nav = C["nav"]
    left = ["services", "results", "pricing"]
    right = ["about", "faq", "contact"]

    def link(p):
        cur = ' aria-current="page"' if p == page else ""
        return f'<a class="nav__link" href="{slug_href(p, lang, lang)}"{cur}>{e(nav[p])}</a>'

    lang_switch = (
        f'<div class="lang" role="group" aria-label="{e(C["ui"]["language"])}">'
        f'<a href="{slug_href(page, "en", lang)}" data-lang aria-current="{"true" if lang == "en" else "false"}" lang="en">EN</a>'
        f'<a href="{slug_href(page, "ru", lang)}" data-lang aria-current="{"true" if lang == "ru" else "false"}" lang="ru">RU</a>'
        f"</div>"
    )
    return f"""<header class="header">
  <div class="header__inner">
    <nav class="nav nav--start" aria-label="{e(C['ui']['nav_primary'])}">
      <a class="nav__tel" href="tel:{SITE['phone_e164']}">{ICONS['phone']}<span>{e(SITE['phone_display'])}</span></a>
      {''.join(link(p) for p in left)}
    </nav>
    <a class="brand" href="{slug_href('index', lang, lang)}">
      <span class="brand__name"><span class="brand__mark">{ICONS['mark']}</span>{e(SITE['brand'])}</span>
      <span class="brand__sub">{e(SITE['brand_sub'])}</span>
    </a>
    <nav class="nav nav--end" aria-label="{e(C['ui']['nav_secondary'])}">
      {''.join(link(p) for p in right)}
      {lang_switch}
      <a class="btn btn--gold" href="{wa_link(C)}" data-book aria-haspopup="dialog" aria-controls="book-dialog" target="_blank" rel="noopener">{e(C['ui']['book'])}</a>
    </nav>
    <button class="burger" type="button" aria-expanded="false" aria-label="{e(C['ui']['menu'])}"><span></span></button>
  </div>
  <div class="header__rule"><span></span></div>
</header>
"""


def wa_link(C):
    return "https://wa.me/%s?text=%s" % (SITE["whatsapp"], quote(C["ui"]["wa_text"]))


def dock(C):
    return f"""<div class="dock">
  <a href="{wa_link(C)}" target="_blank" rel="noopener" aria-label="{e(C['ui']['wa_aria'])}">{ICONS['whatsapp']}</a>
  <a href="{SITE['instagram']}" target="_blank" rel="noopener" aria-label="Instagram">{ICONS['instagram']}</a>
  <a href="tel:{SITE['phone_e164']}" aria-label="{e(C['ui']['call'])}">{ICONS['phone']}</a>
</div>
<nav class="mobile-bar" aria-label="{e(C['ui']['quick_contact'])}">
  <a class="is-primary" href="{wa_link(C)}" target="_blank" rel="noopener">{ICONS['whatsapp']}WhatsApp</a>
  <a href="{SITE['instagram']}" target="_blank" rel="noopener">{ICONS['instagram']}Instagram</a>
</nav>
"""


def book_dialog(lang, C):
    """Booking options, one dialog per page.

    The trigger stays a real WhatsApp link, so with no JS or no <dialog>
    support the button still does the thing it promises.
    """
    B = C["book"]
    hrefs = {
        "whatsapp": (wa_link(C), True),
        "instagram": (SITE["instagram"], True),
        "phone": ("tel:" + SITE["phone_e164"], False),
        "form": (slug_href("contact", lang, lang), False),
    }
    rows = []
    for i, opt in enumerate(B["options"]):
        href, external = hrefs[opt["icon"]]
        ext = ' target="_blank" rel="noopener"' if external else ""
        primary = " book-option--primary" if i == 0 else ""
        rows.append(
            f'<a class="book-option{primary}" href="{href}"{ext}>'
            f'<span class="book-option__ico" data-ico="{opt["icon"]}">{ICONS[opt["icon"]]}</span>'
            f'<span class="book-option__text"><b>{e(opt["title"])}</b>'
            f'<span class="book-option__desc">{e(opt["desc"])}</span></span>'
            f'<span class="book-option__go">{ICONS["arrow"]}</span></a>'
        )
    return f"""<dialog class="book-dialog" id="book-dialog" aria-labelledby="book-dialog-title">
  <div class="book-dialog__head">
    <h2 id="book-dialog-title">{e(B['h2'])}</h2>
    <p>{e(B['lead'])}</p>
    <button class="book-dialog__close" type="button" data-close aria-label="{e(B['close'])}">{ICONS['close']}</button>
  </div>
  <div class="book-options">{''.join(rows)}</div>
  <p class="book-dialog__note">{e(B['note'])}</p>
</dialog>
"""


def footer(lang, C):
    nav = C["nav"]
    cols = "".join(
        f'<li><a href="{slug_href(p, lang, lang)}">{e(nav[p])}</a></li>'
        for p in PAGES
    )
    asset_js = "assets/js/site.js" if lang == "en" else "../assets/js/site.js"
    f = C["footer"]
    return f"""<footer class="footer">
  <div class="wrap footer__inner">
    <div>
      <a class="brand" href="{slug_href('index', lang, lang)}" style="align-items:flex-start">
        <span class="brand__name"><span class="brand__mark">{ICONS['mark']}</span>{e(SITE['brand'])}</span>
        <span class="brand__sub">{e(SITE['brand_sub'])}</span>
      </a>
      <p class="mt-4" style="font-size:.875rem">{e(f['blurb'])}</p>
      <div class="pigment-strip mt-4" aria-hidden="true" style="border-radius:4px;overflow:hidden;max-width:280px">
        <div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>
      </div>
    </div>
    <div>
      <h2 class="footer__title">{e(f['sitemap'])}</h2>
      <ul>{cols}</ul>
    </div>
    <div>
      <h2 class="footer__title">{e(f['contact'])}</h2>
      <ul class="footer__contact">
        <li>{ICONS['whatsapp']}<a href="{wa_link(C)}" target="_blank" rel="noopener">{e(SITE['phone_display'])}</a></li>
        <li>{ICONS['mail']}<a href="mailto:{SITE['email']}">{e(SITE['email'])}</a></li>
        <li>{ICONS['instagram']}<a href="{SITE['instagram']}" target="_blank" rel="noopener">{e(SITE['instagram_handle'])}</a></li>
        <li>{ICONS['pin']}<span>{e(f['areas'])}</span></li>
        <li>{ICONS['clock']}<span>{e(f['hours'])}</span></li>
      </ul>
    </div>
  </div>
  <div class="wrap">
    <div class="footer__legal">
      <span>&copy; <span data-year>2026</span> {e(SITE['brand'])} {e(SITE['brand_sub'])}. {e(f['rights'])}</span>
      <span>{e(f['founder_label'])} <a href="{SITE['founder']}" target="_blank" rel="noopener">{e(SITE['founder_handle'])}</a></span>
    </div>
  </div>
</footer>
<script src="https://cdn.jsdelivr.net/npm/lenis@1/dist/lenis.min.js" defer></script>
<script src="{asset_js}" defer></script>
</body>
</html>
"""


# --- Shared blocks ----------------------------------------------------------

def pigment_strip():
    return ('<div class="pigment-strip" aria-hidden="true">'
            + "<div></div>" * 8 + "</div>")


def ba_block(asset, item, C):
    """Before/after comparison slider.

    Currently unused: no genuine before/after pairs exist yet. Kept wired up
    (with its CSS and its keyboard-accessible range input) so the moment real
    pairs arrive it is a content change, not a rebuild.
    """
    return f"""<figure class="ba">
  <div class="ba__frame">
    <img src="{asset}img/{item['before']}" alt="{e(item['alt_before'])}" loading="lazy" decoding="async">
    <img class="ba__after" src="{asset}img/{item['after']}" alt="{e(item['alt_after'])}" loading="lazy" decoding="async">
    <span class="ba__tag ba__tag--before">{e(C['ui']['before'])}</span>
    <span class="ba__tag ba__tag--after">{e(C['ui']['after'])}</span>
    <input class="ba__range" type="range" min="0" max="100" value="50" step="1"
           aria-label="{e(C['ui']['ba_aria'])}">
    <span class="ba__handle" aria-hidden="true"></span>
  </div>
  <figcaption class="ba__caption"><span>{e(item['caption'])}</span><span>{e(item['meta'])}</span></figcaption>
</figure>"""


def tone_buttons(C):
    codes = ["MS-01", "MS-02", "MS-03", "MS-04", "MS-05", "MS-06", "MS-07", "MS-08"]
    hexes = ["#F3DCCB", "#EBCBB2", "#DFB694", "#CE9E78", "#B5825E", "#986748", "#7A4F36", "#5C3A28"]
    out = []
    for i, (code, hx) in enumerate(zip(codes, hexes)):
        pressed = "true" if i == 3 else "false"
        out.append(
            f'<button class="tone" type="button" data-tone="{code}" aria-pressed="{pressed}" '
            f'style="background:{hx}"><span class="sr-only">{e(C["ui"]["tone_aria"])} {code}</span></button>'
        )
    return "".join(out)


def matcher_block(C):
    m = C["home"]["camo"]
    return f"""<div class="matcher" data-matcher>
  <div>
    <h3 style="letter-spacing:-.01em">{e(m['matcher_title'])}</h3>
    <p class="mt-4">{e(m['matcher_lead'])}</p>
    <div class="tones" role="group" aria-label="{e(m['matcher_title'])}">{tone_buttons(C)}</div>
  </div>
  <div class="match-card">
    <p class="eyebrow" style="margin-bottom:1rem"><span class="mono" data-out="code">MS-04</span></p>
    <div class="match-card__swatches">
      <div class="match-swatch"><i data-out="skin"></i><b>{e(m['labels']['skin'])}</b></div>
      <div class="match-swatch"><i data-out="base"></i><b>{e(m['labels']['base'])}</b></div>
      <div class="match-swatch"><i data-out="corr"></i><b>{e(m['labels']['corr'])}</b></div>
    </div>
    <p class="match-card__note" data-out="note"></p>
    <p class="match-card__note" style="opacity:.6;font-size:.78rem">{e(m['disclaimer'])}</p>
  </div>
</div>"""


def faq_list(items, open_first=False):
    out = ['<div class="faq">']
    for i, it in enumerate(items):
        op = " open" if (open_first and i == 0) else ""
        paras = "".join(f"<p>{p}</p>" for p in it["a"])
        out.append(f"<details{op}><summary>{e(it['q'])}</summary><div>{paras}</div></details>")
    out.append("</div>")
    return "".join(out)


def cta_band(lang, C, block):
    return f"""<section class="section section--dark">
  <div class="wrap">
    <div class="head head--center">
      <p class="eyebrow eyebrow--center">{e(block['eyebrow'])}</p>
      <h2 class="h2-caps">{e(block['h2'])}</h2>
      <p class="lead">{e(block['lead'])}</p>
      <div class="btn-row mt-5" style="justify-content:center">
        <a class="btn btn--gold btn--lg" href="{wa_link(C)}" target="_blank" rel="noopener">{e(block['primary'])}</a>
        <a class="btn btn--ghost btn--lg" href="{slug_href('contact', lang, lang)}">{e(block['secondary'])}</a>
      </div>
    </div>
  </div>
</section>"""


# --- Pages ------------------------------------------------------------------

def page_index(lang, C):
    a = "assets/" if lang == "en" else "../assets/"
    H = C["home"]

    facts = "".join(
        f'<li class="hero__fact">{ICONS[k]}<span>{e(t)}</span></li>' for k, t in H["facts"]
    )
    services = "".join(
        f"""<article class="card reveal" data-delay="{i}">
      <div class="card__media"><img src="{a}img/{s['img']}" alt="{e(s['alt'])}"{dims(s['img'])} loading="lazy" decoding="async"></div>
      <div class="card__body">
        <h3 class="card__title">{e(s['title'])}</h3>
        <p style="font-size:.925rem">{e(s['text'])}</p>
        <div class="card__meta">
          <span class="card__price">{e(s['price'])} <small>{e(s['price_note'])}</small></span>
          <a class="card__link" href="{slug_href('services', lang, lang)}{s['anchor']}">{e(C['ui']['more'])}{ICONS['arrow']}</a>
        </div>
      </div>
    </article>""" for i, s in enumerate(H["services"]["items"])
    )
    bullets = "".join(f'<li class="tick">{e(b)}</li>' for b in H["camo"]["bullets"])
    results = "".join(
        f"""<figure class="card reveal" data-delay="{i}" style="margin:0">
      <div class="card__media card__media--portrait"><img src="{a}img/{it['img']}" alt="{e(it['alt'])}"{dims(it['img'])} loading="lazy" decoding="async"></div>
      <figcaption class="card__body"><span class="chip">{e(it['tag'])}</span><p style="font-size:.9rem">{e(it['caption'])}</p></figcaption>
    </figure>""" for i, it in enumerate(H["results"]["items"])
    )
    timeline = "".join(
        f'<div class="timeline__step"><p class="timeline__day">{e(s["day"])}</p>'
        f'<h3>{e(s["title"])}</h3><p>{e(s["text"])}</p></div>'
        for s in H["healing"]["steps"]
    )
    steps = "".join(
        f'<li class="step"><span class="step__num" aria-hidden="true"></span>'
        f'<div><h3>{e(s["title"])}</h3><p>{e(s["text"])}</p></div></li>'
        for s in H["home_service"]["steps"]
    )
    founder_facts = "".join(
        f'<div><dt class="eyebrow" style="display:block">{e(k)}</dt>'
        f'<dd class="mono">{e(v)}</dd></div>'
        for k, v in H["founder"]["facts"]
    )
    reviews = "".join(
        # SAMPLE copy for the mockup — see README. The marker below travels with
        # the built HTML so this cannot quietly ship as if it were real.
        f'<!-- SAMPLE REVIEW - replace with a real, permissioned client quote before launch -->'
        f'<blockquote class="quote reveal" data-delay="{i}">'
        f'<span class="quote__mark">{ICONS["quote"]}</span><p>{e(q["text"])}</p>'
        f'<footer>{e(q["who"])}</footer></blockquote>'
        for i, q in enumerate(H["reviews"]["slots"])
    )

    return f"""<main id="main" class="page">

<section class="hero">
  <div class="hero__media">
    <img src="{a}img/hero.webp" alt="{e(H['hero_alt'])}"{dims("hero.webp")} fetchpriority="high" decoding="async">
  </div>
  <div class="wrap hero__inner">
    <div class="hero__copy">
      <p class="eyebrow">{e(H['eyebrow'])}</p>
      <h1 class="display hero__title">{H['title_html']}</h1>
      <p class="hero__lead">{e(H['lead'])}</p>
      <div class="btn-row">
        <a class="btn btn--gold btn--lg" href="{wa_link(C)}" target="_blank" rel="noopener">{e(H['cta_primary'])}</a>
        <a class="btn btn--ghost btn--lg" href="{slug_href('results', lang, lang)}">{e(H['cta_secondary'])}</a>
      </div>
      <ul class="hero__facts">{facts}</ul>
    </div>
  </div>
</section>
{pigment_strip()}

<section class="section section--white">
  <div class="wrap">
    <div class="head head--split reveal">
      <div>
        <p class="eyebrow">{e(H['services']['eyebrow'])}</p>
        <h2 class="h2-caps">{e(H['services']['h2'])}</h2>
      </div>
      <p class="lead">{e(H['services']['lead'])}</p>
    </div>
    <div class="grid grid--3 mt-6">{services}</div>
  </div>
</section>

<section class="section section--dark">
  <div class="wrap">
    <div class="head head--split reveal">
      <div>
        <p class="eyebrow">{e(H['camo']['eyebrow'])}</p>
        <h2 class="h2-caps">{e(H['camo']['h2'])}</h2>
      </div>
      <p class="lead">{e(H['camo']['lead'])}</p>
    </div>
    <ul class="grid grid--4 mt-5 reveal" style="list-style:none;padding:0">{bullets}</ul>
    <div class="mt-6 reveal">{matcher_block(C)}</div>
    <div class="btn-row mt-6">
      <a class="btn btn--gold" href="{slug_href('services', lang, lang)}#camouflage">{e(H['camo']['cta'])}</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="head head--split reveal">
      <div>
        <p class="eyebrow">{e(H['results']['eyebrow'])}</p>
        <h2 class="h2-caps">{e(H['results']['h2'])}</h2>
      </div>
      <p class="lead">{e(H['results']['lead'])}</p>
    </div>
    <div class="grid grid--3 mt-6">{results}</div>
    <div class="btn-row mt-5"><a class="btn btn--ghost" href="{slug_href('results', lang, lang)}">{e(H['results']['cta'])}</a></div>
  </div>
</section>

<section class="section section--warm">
  <div class="wrap">
    <div class="head reveal">
      <p class="eyebrow">{e(H['healing']['eyebrow'])}</p>
      <h2 class="h2-caps">{e(H['healing']['h2'])}</h2>
      <p class="lead">{e(H['healing']['lead'])}</p>
    </div>
    <div class="timeline reveal">{timeline}</div>
    <p class="price-note mt-5">{e(H['healing']['note'])}</p>
  </div>
</section>

<section class="section section--white">
  <div class="wrap split">
    <div class="reveal">
      <p class="eyebrow">{e(H['home_service']['eyebrow'])}</p>
      <h2 class="h2-caps">{e(H['home_service']['h2'])}</h2>
      <p class="lead mt-4">{e(H['home_service']['lead'])}</p>
      <ol class="steps mt-6" style="list-style:none;padding:0">{steps}</ol>
    </div>
    <div class="media-frame reveal" data-delay="1">
      <img src="{a}img/home-service.webp" alt="{e(H['home_service']['img_alt'])}"{dims("home-service.webp")} loading="lazy" decoding="async">
    </div>
  </div>
</section>

<section class="section section--warm">
  <div class="wrap split">
    <div class="media-frame reveal">
      <img src="{a}img/portrait.webp" alt="{e(H['founder']['img_alt'])}"{dims("portrait.webp")} loading="lazy" decoding="async">
    </div>
    <div class="reveal" data-delay="1">
      <p class="eyebrow">{e(H['founder']['eyebrow'])}</p>
      <h2 class="h2-caps">{e(H['founder']['h2'])}</h2>
      {''.join(f'<p class="mt-4">{e(p)}</p>' for p in H['founder']['paras'])}
      <dl class="spec-list mt-6">{founder_facts}</dl>
      <div class="btn-row mt-6">
        <a class="btn btn--ghost" href="{slug_href('about', lang, lang)}">{e(H['founder']['cta'])}</a>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="head head--center reveal">
      <p class="eyebrow eyebrow--center">{e(H['reviews']['eyebrow'])}</p>
      <h2 class="h2-caps">{e(H['reviews']['h2'])}</h2>
      <p class="lead">{e(H['reviews']['lead'])}</p>
    </div>
    <div class="grid grid--3 mt-6">{reviews}</div>
    <div class="btn-row mt-5" style="justify-content:center">
      <a class="btn btn--ghost" href="{SITE['instagram']}" target="_blank" rel="noopener">{e(H['reviews']['ig_cta'])}</a>
    </div>
  </div>
</section>

<section class="section section--warm">
  <div class="wrap wrap--narrow">
    <div class="head reveal">
      <p class="eyebrow">{e(H['faq']['eyebrow'])}</p>
      <h2 class="h2-caps">{e(H['faq']['h2'])}</h2>
    </div>
    {faq_list(H['faq']['items'], open_first=True)}
    <div class="btn-row mt-5"><a class="btn btn--ghost" href="{slug_href('faq', lang, lang)}">{e(H['faq']['cta'])}</a></div>
  </div>
</section>

{cta_band(lang, C, H['cta'])}
</main>
"""


def page_services(lang, C):
    a = "assets/" if lang == "en" else "../assets/"
    S = C["services"]
    blocks = []
    for i, it in enumerate(S["items"]):
        rev = " split--reverse" if i % 2 else ""
        good = "".join(f"<li class='tick'>{e(g)}</li>" for g in it["good_for"])
        specs = "".join(
            f'<div><dt class="eyebrow" style="display:block">{e(k)}</dt>'
            f'<dd class="mono">{e(v)}</dd></div>'
            for k, v in it["specs"]
        )
        blocks.append(f"""<section class="section svc section--dark" id="{it['id']}">
  <img class="svc__bg" src="{a}img/{it['img']}" alt="{e(it['alt'])}"{dims(it['img'])} loading="lazy" decoding="async">
  <div class="wrap">
    <div class="svc__head reveal">
      <p class="eyebrow">{e(it['eyebrow'])}</p>
      <h2 class="h2-caps">{e(it['title'])}</h2>
    </div>
    <div class="svc__cols">
      <div class="reveal">
        <p class="lead">{e(it['lead'])}</p>
        {''.join(f'<p class="mt-4">{e(p)}</p>' for p in it['paras'])}
      </div>
      <div class="reveal" data-delay="1">
        <h3 style="font-size:1rem;letter-spacing:-.01em">{e(S['good_for_label'])}</h3>
        <ul class="mt-4" style="list-style:none;padding:0;display:grid;gap:.6rem">{good}</ul>
        <dl class="spec-list mt-6">{specs}</dl>
        <div class="btn-row mt-6">
          <a class="btn btn--gold" href="{wa_link(C)}" target="_blank" rel="noopener">{e(it['cta'])}</a>
          <a class="btn btn--ghost" href="{slug_href('pricing', lang, lang)}">{e(S['see_pricing'])}</a>
        </div>
      </div>
    </div>
  </div>
</section>""")

    return f"""<main id="main" class="page">
<section class="section section--tight">
  <div class="wrap">
    <div class="head">
      <p class="eyebrow">{e(S['eyebrow'])}</p>
      <h1 class="display" style="font-size:var(--fs-h1)">{e(S['h1'])}</h1>
      <p class="lead">{e(S['lead'])}</p>
    </div>
  </div>
</section>
{pigment_strip()}
{''.join(blocks)}
{cta_band(lang, C, S['cta'])}
</main>
"""


def page_pricing(lang, C):
    P = C["pricing"]
    rows = "".join(
        f'<tr><th scope="row">{e(r["name"])}<small>{e(r["note"])}</small></th>'
        f'<td>{e(r["duration"])}</td><td>{e(r["price"])}</td></tr>'
        for r in P["rows"]
    )
    included = "".join(
        f'<div class="card card--flat"><div class="card__body" style="padding:0">'
        f'<span class="ico ico--lg">{ICONS[k]}</span>'
        f'<h3 class="card__title" style="font-size:1rem">{e(t)}</h3>'
        f'<p style="font-size:.9rem">{e(x)}</p></div></div>'
        for k, t, x in P["included"]["items"]
    )
    notes = "".join(f"<li class='tick'>{e(n)}</li>" for n in P["notes"])
    return f"""<main id="main" class="page">
<section class="section section--tight">
  <div class="wrap">
    <div class="head">
      <p class="eyebrow">{e(P['eyebrow'])}</p>
      <h1 class="display" style="font-size:var(--fs-h1)">{e(P['h1'])}</h1>
      <p class="lead">{e(P['lead'])}</p>
    </div>
  </div>
</section>
{pigment_strip()}
<section class="section section--white">
  <div class="wrap">
    <table class="price-table reveal">
      <caption>{e(P['caption'])}</caption>
      <thead><tr><th scope="col">{e(P['th_service'])}</th><th scope="col">{e(P['th_time'])}</th><th scope="col">{e(P['th_price'])}</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    <ul class="mt-6" style="list-style:none;padding:0;display:grid;gap:.6rem;max-width:62ch">{notes}</ul>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="head reveal">
      <p class="eyebrow">{e(P['included']['eyebrow'])}</p>
      <h2 class="h2-caps">{e(P['included']['h2'])}</h2>
    </div>
    <div class="grid grid--4 mt-6 reveal">{included}</div>
  </div>
</section>
{cta_band(lang, C, P['cta'])}
</main>
"""


def page_results(lang, C):
    a = "assets/" if lang == "en" else "../assets/"
    R = C["results"]
    tiles = "".join(
        f"""<figure class="card reveal" data-delay="{i % 3}" style="margin:0">
      <div class="card__media card__media--portrait"><img src="{a}img/{g['img']}" alt="{e(g['alt'])}"{dims(g['img'])} loading="lazy" decoding="async"></div>
      <figcaption class="card__body"><span class="chip">{e(g['tag'])}</span><p style="font-size:.9rem">{e(g['caption'])}</p></figcaption>
    </figure>""" for i, g in enumerate(R["gallery"])
    )
    return f"""<main id="main" class="page">
<section class="section section--tight">
  <div class="wrap">
    <div class="head">
      <p class="eyebrow">{e(R['eyebrow'])}</p>
      <h1 class="display" style="font-size:var(--fs-h1)">{e(R['h1'])}</h1>
      <p class="lead">{e(R['lead'])}</p>
    </div>
  </div>
</section>
{pigment_strip()}
<section class="section section--white">
  <div class="wrap">
    <div class="grid grid--3">{tiles}</div>
    <p class="price-note mt-6">{e(R['note'])}</p>
  </div>
</section>
{cta_band(lang, C, R['cta'])}
</main>
"""


def page_about(lang, C):
    a = "assets/" if lang == "en" else "../assets/"
    A = C["about"]
    principles = "".join(
        f'<div class="reveal" data-delay="{i}"><h3 style="letter-spacing:-.01em;font-size:1rem">{e(p["title"])}</h3>'
        f'<p class="mt-4" style="font-size:.925rem">{e(p["text"])}</p></div>'
        for i, p in enumerate(A["principles"])
    )
    standards = "".join(f"<li class='tick'>{e(s)}</li>" for s in A["standards"])
    return f"""<main id="main" class="page">
<section class="section section--tight">
  <div class="wrap">
    <div class="head">
      <p class="eyebrow">{e(A['eyebrow'])}</p>
      <h1 class="display" style="font-size:var(--fs-h1)">{e(A['h1'])}</h1>
      <p class="lead">{e(A['lead'])}</p>
    </div>
  </div>
</section>
{pigment_strip()}
<section class="section section--white">
  <div class="wrap split">
    <div class="media-frame reveal">
      <img src="{a}img/portrait.webp" alt="{e(A['img_alt'])}"{dims("portrait.webp")} loading="lazy" decoding="async">
    </div>
    <div class="reveal" data-delay="1">
      {''.join(f'<p class="mt-4">{e(p)}</p>' for p in A['paras'])}
      <p class="mt-6" style="font-size:.9rem;color:var(--ink-mute)">{e(A['founder_label'])}
        <a href="{SITE['founder']}" target="_blank" rel="noopener" class="channel-link" style="font-weight:700;color:var(--ink)">{e(SITE['founder_handle'])}</a></p>
    </div>
  </div>
</section>
<section class="section section--dark">
  <div class="wrap">
    <div class="head reveal">
      <p class="eyebrow">{e(A['principles_eyebrow'])}</p>
      <h2 class="h2-caps">{e(A['principles_h2'])}</h2>
    </div>
    <div class="grid grid--3 mt-6">{principles}</div>
  </div>
</section>
<section class="section">
  <div class="wrap split">
    <div class="reveal">
      <p class="eyebrow">{e(A['standards_eyebrow'])}</p>
      <h2 class="h2-caps">{e(A['standards_h2'])}</h2>
      <p class="lead mt-4">{e(A['standards_lead'])}</p>
      <ul class="mt-6" style="list-style:none;padding:0;display:grid;gap:.7rem">{standards}</ul>
    </div>
    <div class="media-frame reveal" data-delay="1">
      <img src="{a}img/studio.webp" alt="{e(A['standards_img_alt'])}"{dims("studio.webp")} loading="lazy" decoding="async">
    </div>
  </div>
</section>
{cta_band(lang, C, A['cta'])}
</main>
"""


def page_faq(lang, C):
    F = C["faq"]
    groups = "".join(
        f'<section class="mt-6 reveal"><h2 class="h2-caps" style="font-size:var(--fs-h3)">{e(g["title"])}</h2>{faq_list(g["items"])}</section>'
        for g in F["groups"]
    )
    return f"""<main id="main" class="page">
<section class="section section--tight">
  <div class="wrap">
    <div class="head">
      <p class="eyebrow">{e(F['eyebrow'])}</p>
      <h1 class="display" style="font-size:var(--fs-h1)">{e(F['h1'])}</h1>
      <p class="lead">{e(F['lead'])}</p>
    </div>
  </div>
</section>
{pigment_strip()}
<section class="section section--white">
  <div class="wrap wrap--narrow">{groups}
    <p class="price-note mt-6">{e(F['medical_note'])}</p>
  </div>
</section>
{cta_band(lang, C, F['cta'])}
</main>
"""


def page_contact(lang, C):
    K = C["contact"]
    channels = "".join(
        f'<li style="display:flex;gap:.8rem;align-items:flex-start">'
        f'<span class="ico" style="margin-top:.2rem">{ICONS[c["icon"]]}</span>'
        f'<span><b style="display:block;color:var(--ink)">{e(c["label"])}</b>'
        f'<a href="{c["href"]}"{" target=_blank rel=noopener" if c["href"].startswith("http") else ""} class="channel-link">{e(c["value"])}</a></span></li>'
        for c in K["channels"]
    )
    options = "".join(f'<option value="{e(o)}">{e(o)}</option>' for o in K["form"]["services"])
    return f"""<main id="main" class="page">
<section class="section section--tight">
  <div class="wrap">
    <div class="head">
      <p class="eyebrow">{e(K['eyebrow'])}</p>
      <h1 class="display" style="font-size:var(--fs-h1)">{e(K['h1'])}</h1>
      <p class="lead">{e(K['lead'])}</p>
    </div>
  </div>
</section>
{pigment_strip()}
<section class="section section--white">
  <div class="wrap split split--top">
    <div class="reveal">
      <h2 class="h2-caps" style="font-size:var(--fs-h3)">{e(K['direct_h2'])}</h2>
      <p class="mt-4">{e(K['direct_lead'])}</p>
      <div class="btn-row mt-5">
        <a class="btn btn--gold btn--lg" href="{wa_link(C)}" target="_blank" rel="noopener">{e(K['wa_cta'])}</a>
      </div>
      <ul class="mt-6" style="list-style:none;padding:0;display:grid;gap:1.1rem">{channels}</ul>
    </div>
    <div class="reveal" data-delay="1">
      <form class="form-grid" data-wa-form action="{wa_link(C)}" method="get" target="_blank">
        <h2 class="h2-caps" style="font-size:var(--fs-h3)">{e(K['form']['h2'])}</h2>
        <p style="font-size:.9rem;color:var(--ink-mute)">{e(K['form']['lead'])}</p>
        <div class="form-grid form-grid--2">
          <div class="field">
            <label for="f-name">{e(K['form']['name'])}</label>
            <input id="f-name" name="name" type="text" autocomplete="name" required>
          </div>
          <div class="field">
            <label for="f-phone">{e(K['form']['phone'])}</label>
            <input id="f-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" placeholder="+971 5X XXX XXXX" required>
          </div>
        </div>
        <div class="field">
          <label for="f-service">{e(K['form']['service'])}</label>
          <select id="f-service" name="service">{options}</select>
        </div>
        <div class="field">
          <label for="f-area">{e(K['form']['area'])}</label>
          <input id="f-area" name="area" type="text" placeholder="{e(K['form']['area_ph'])}">
        </div>
        <div class="field">
          <label for="f-msg">{e(K['form']['message'])}</label>
          <textarea id="f-msg" name="message" placeholder="{e(K['form']['message_ph'])}"></textarea>
          <span class="hint">{e(K['form']['message_hint'])}</span>
        </div>
        <button class="btn btn--gold btn--lg" type="submit">{e(K['form']['submit'])}</button>
        <p class="form-note">{e(K['form']['note'])}</p>
      </form>
    </div>
  </div>
</section>
<section class="section section--warm" id="areas">
  <div class="wrap">
    <div class="head reveal">
      <p class="eyebrow">{e(K['areas_eyebrow'])}</p>
      <h2 class="h2-caps">{e(K['areas_h2'])}</h2>
      <p class="lead">{e(K['areas_lead'])}</p>
    </div>
    <div class="grid grid--3 mt-6 reveal">
      {''.join(f'<div><h3 style="font-size:1rem;letter-spacing:-.01em">{e(t)}</h3><p class="mt-4" style="font-size:.9rem">{e(x)}</p></div>' for t, x in K['areas_items'])}
    </div>
  </div>
</section>
{cta_band(lang, C, K['cta'])}
</main>
"""


RENDERERS = {
    "index": page_index,
    "services": page_services,
    "pricing": page_pricing,
    "results": page_results,
    "about": page_about,
    "faq": page_faq,
    "contact": page_contact,
}


# --- Build ------------------------------------------------------------------

def resolve_channels(C):
    """Fill contact placeholders from SITE so numbers live in one place."""
    repl = {
        "__PHONE__": SITE["phone_display"],
        "__EMAIL__": SITE["email"],
        "__IG_HANDLE__": SITE["instagram_handle"],
        "__WA__": wa_link(C),
        "__TEL__": "tel:" + SITE["phone_e164"],
        "__MAILTO__": "mailto:" + SITE["email"],
        "__IG__": SITE["instagram"],
    }
    for ch in C["contact"]["channels"]:
        for key in ("value", "href"):
            ch[key] = repl.get(ch[key], ch[key])
    for opt in C["book"]["options"]:
        for token, value in repl.items():
            opt["desc"] = opt["desc"].replace(token, value)


def main():
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from content_en import EN
    from content_ru import RU

    written = []
    for lang, C in (("en", EN), ("ru", RU)):
        resolve_channels(C)
        outdir = ROOT if lang == "en" else ROOT / "ru"
        outdir.mkdir(parents=True, exist_ok=True)
        for page in PAGES:
            doc = head(lang, page, C) + header(lang, page, C) \
                + RENDERERS[page](lang, C) + dock(C) + book_dialog(lang, C) + footer(lang, C)
            doc = re.sub(r"\n{3,}", "\n\n", doc)
            path = outdir / ("index.html" if page == "index" else page + ".html")
            path.write_text(doc, encoding="utf-8")
            written.append(str(path.relative_to(ROOT)))

    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE["domain"], encoding="utf-8")

    urls = []
    for lang in ("en", "ru"):
        for page in PAGES:
            loc = SITE["domain"] + ("/" if lang == "en" else "/ru/") + ("" if page == "index" else page + ".html")
            alts = "".join(
                '\n    <xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (
                    l, SITE["domain"] + ("/" if l == "en" else "/ru/") + ("" if page == "index" else page + ".html"))
                for l in ("en", "ru"))
            urls.append("  <url>\n    <loc>%s</loc>%s\n  </url>" % (loc, alts))
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(urls) + "\n</urlset>\n",
        encoding="utf-8")

    print("built %d pages:" % len(written))
    for w in written:
        print("  " + w)


if __name__ == "__main__":
    main()

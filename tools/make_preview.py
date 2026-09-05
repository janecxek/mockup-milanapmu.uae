#!/usr/bin/env python3
"""Bundle the whole site into one self-contained HTML file.

For review only: all 14 pages, both languages, CSS, JS, fonts and images
inlined, with hash routing standing in for real URLs. The shipped site is the
plain multi-page build — this exists so the mockup can be opened or emailed
as a single file with no server.

    python3 tools/make_preview.py   ->  preview/milana-pmu-preview.html
"""
import base64, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "preview"; OUT.mkdir(exist_ok=True)
PAGES = ["index", "services", "results", "pricing", "about", "faq", "contact"]

def read(p): return (ROOT / p).read_text(encoding="utf-8")

# --- fonts: latin + cyrillic only, embedded as data URIs --------------------
fonts_css = read("assets/css/fonts.css")
def embed_font(m):
    name = m.group(1)
    data = base64.b64encode((ROOT / "assets/fonts" / name).read_bytes()).decode()
    return "url(data:font/woff2;base64,%s)" % data
fonts_css = "\n\n".join(
    b for b in fonts_css.split("\n\n")
    if "-ext" not in b or "@font-face" not in b)          # drop extended subsets
fonts_css = re.sub(r"url\(\.\./fonts/([^)]+)\)", embed_font, fonts_css)

css = "\n".join([read("assets/css/tokens.css"), fonts_css, read("assets/css/site.css")])

# --- images: SVG placeholders as data URIs ----------------------------------
images = {}
for f in sorted((ROOT / "assets/img").glob("*.svg")):
    images[f.name] = "data:image/svg+xml;base64," + base64.b64encode(f.read_bytes()).decode()

# --- behaviour: make the IIFE re-runnable after each route change -----------
js = read("assets/js/site.js")
js = js.replace("(function () {\n  'use strict';", "window.__initSite = function () {\n  'use strict';", 1)
js = re.sub(r"\}\)\(\);\s*$", "};\n", js)

# --- page bodies ------------------------------------------------------------
def route(lang, page, anchor=""):
    key = "%s/%s" % (lang, "home" if page == "index" else page)
    return "#/" + key + ("~" + anchor if anchor else "")

bodies = {}
for lang in ("en", "ru"):
    for page in PAGES:
        src = read(("" if lang == "en" else "ru/") + ("index.html" if page == "index" else page + ".html"))
        body = re.search(r"<body>(.*)</body>", src, re.S).group(1)
        body = re.sub(r'<script src="[^"]*site\.js"[^>]*></script>', "", body)
        other = "ru" if lang == "en" else "en"

        def href(m):
            target, anchor = m.group(1), m.group(2) or ""
            up = target.startswith("../")
            t = target.replace("../", "").replace("ru/", "")
            page_name = "index" if t == "index.html" else t[:-5]
            to = other if (up or target.startswith("ru/")) else lang
            return 'href="%s"' % route(to, page_name, anchor.lstrip("#"))

        body = re.sub(r'href="((?:\.\./|ru/)?[a-z-]+\.html)(#[a-z-]+)?"', href, body)
        body = re.sub(r'href="#([a-z-]+)"(?! )', lambda m: 'href="%s"' % route(lang, page, m.group(1)), body)
        body = re.sub(r'src="(?:\.\./)?assets/img/([^"]+)"', lambda m: 'src="%s"' % images[m.group(1)], body)
        bodies[route(lang, page).lstrip("#/")] = body

import json
router = """
const PAGES = %s;
const app = document.getElementById('app');
function render() {
  const raw = (location.hash || '#/en/home').slice(2);
  const [key, anchor] = raw.split('~');
  const body = PAGES[key] || PAGES['en/home'];
  document.documentElement.lang = key.startsWith('ru') ? 'ru' : 'en';
  app.innerHTML = body;
  window.__initSite();
  if (anchor) {
    const el = document.getElementById(anchor);
    if (el) { el.scrollIntoView(); return; }
  }
  window.scrollTo(0, 0);
}
addEventListener('hashchange', render);
render();
""" % json.dumps(bodies, ensure_ascii=False)

html = """<title>Milana PMU Dubai</title>
<style>%s
.preview-note{position:fixed;left:50%%;bottom:12px;transform:translateX(-50%%);z-index:200;
 background:rgba(20,18,16,.88);color:#fff;padding:.45rem 1rem;border-radius:999px;
 font:500 11px/1 ui-monospace,Menlo,monospace;letter-spacing:.1em;text-transform:uppercase;
 pointer-events:none}
@media (max-width:720px){.preview-note{bottom:64px}}
</style>
<div id="app"></div>
<div class="preview-note">Podgląd — jeden plik, obie wersje językowe</div>
<script>document.documentElement.classList.add('js')</script>
<script>%s</script>
<script>%s</script>
""" % (css, js, router)

path = OUT / "milana-pmu-preview.html"
path.write_text(html, encoding="utf-8")
print("wrote %s  (%.1f MB)" % (path.relative_to(ROOT), path.stat().st_size / 1e6))

#!/usr/bin/env python3
"""Convert a delivered photograph into the WebP the site actually loads.

    python3 tools/png_to_webp.py <source> <name-in-DIMS> [focus]

`name-in-DIMS` is the key in build.py's DIMS table, which supplies the exact
output size — so the file on disk can never disagree with the width/height
attributes the build writes onto the <img>. The source is cover-cropped to that
aspect ratio (never squashed) around `focus`, a 0-1 vertical anchor: 0 keeps the
top edge, 1 the bottom, the default 0.5 crops evenly. Use it to keep the subject
in frame when the source is a different shape from the target.

There is no PIL, cwebp or ffmpeg in this environment, so the resize and the WebP
encode both go through a headless Chromium canvas.
"""
import asyncio
import base64
import mimetypes
import pathlib
import sys

from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from build import DIMS  # noqa: E402  (path set above)

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
QUALITY = 0.82

CONVERT_JS = """
async ([src, outW, outH, focus, q]) => {
  const img = new Image();
  img.src = src;
  await img.decode();
  // Cover crop: take the largest box of the target ratio that fits the source,
  // so nothing is ever stretched.
  const target = outW / outH;
  let sw = img.width, sh = Math.round(img.width / target);
  if (sh > img.height) { sh = img.height; sw = Math.round(img.height * target); }
  const sx = Math.round((img.width - sw) / 2);
  const sy = Math.round((img.height - sh) * focus);
  const c = document.createElement('canvas');
  c.width = outW; c.height = outH;
  const ctx = c.getContext('2d');
  ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(img, sx, sy, sw, sh, 0, 0, outW, outH);
  return c.toDataURL('image/webp', q);
}
"""


async def main(src, name, focus):
    if name not in DIMS:
        sys.exit(f"{name} is not in DIMS in tools/build.py — add it first")
    out_w, out_h = DIMS[name]
    mime = mimetypes.guess_type(src.name)[0] or "image/png"
    data = f"data:{mime};base64," + base64.b64encode(src.read_bytes()).decode()

    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=CHROME)
        page = await browser.new_page()
        await page.goto("about:blank")
        url = await page.evaluate(CONVERT_JS, [data, out_w, out_h, focus, QUALITY])
        await browser.close()

    out = ROOT / "assets/img" / name
    out.write_bytes(base64.b64decode(url.split(",", 1)[1]))
    print(f"wrote {out.relative_to(ROOT)}  {out_w}x{out_h}  {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    asyncio.run(main(pathlib.Path(sys.argv[1]), sys.argv[2],
                     float(sys.argv[3]) if len(sys.argv) > 3 else 0.5))

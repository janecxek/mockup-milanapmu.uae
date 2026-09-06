#!/usr/bin/env python3
"""Derive assets/img/service-lashline.webp from an existing client photograph.

There is no photograph shot for the lashline section yet, so the section
background is a 16:9 band cropped from `gallery-face-02.webp` — a real client
result already used on the site — centred on the eyes and scaled to the size
every other service photo uses (1400x788). It sits behind a scrim measured at
6.1:1 for white body text, so the upscale is not visible in use.

Replace the file with a purpose-shot photograph when one exists and delete this
script. There is no PIL, cwebp or ffmpeg in this environment, so the resize and
the WebP encode both go through a headless Chromium canvas.
"""
import asyncio
import base64
import pathlib

from playwright.async_api import async_playwright

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/img/gallery-face-02.webp"
OUT = ROOT / "assets/img/service-lashline.webp"
SRC_W, BAND_TOP = 900, 200          # source is 900x1195; the eyes sit near y=420
OUT_W, OUT_H, QUALITY = 1400, 788, 0.82

CROP_JS = """
async ([src, srcW, bandTop, outW, outH, q]) => {
  const img = new Image();
  img.src = src;
  await img.decode();
  const bandH = Math.round(srcW * outH / outW);
  const c = document.createElement('canvas');
  c.width = outW; c.height = outH;
  const ctx = c.getContext('2d');
  ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(img, 0, bandTop, srcW, bandH, 0, 0, outW, outH);
  return c.toDataURL('image/webp', q);
}
"""


async def main():
    data = "data:image/webp;base64," + base64.b64encode(SRC.read_bytes()).decode()
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=CHROME)
        page = await browser.new_page()
        await page.goto("about:blank")
        url = await page.evaluate(
            CROP_JS, [data, SRC_W, BAND_TOP, OUT_W, OUT_H, QUALITY]
        )
        await browser.close()
    OUT.write_bytes(base64.b64decode(url.split(",", 1)[1]))
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    asyncio.run(main())

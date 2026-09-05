#!/usr/bin/env python3
"""Generate placeholder artwork for the mockup.

Soft warm gradient fields in the brand's photographic palette (beige, taupe,
skin, gold) with film grain, so an unfinished page still reads as art-directed.
Each file carries a discreet label naming the shot that belongs there.
Delete a file and drop in the real photo under the same name.
"""
import os, pathlib

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets" / "img"
OUT.mkdir(parents=True, exist_ok=True)

TPL = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{alt}">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{c1}"/>
      <stop offset="0.52" stop-color="{c2}"/>
      <stop offset="1" stop-color="{c3}"/>
    </linearGradient>
    <radialGradient id="glow" cx="{gx}" cy="{gy}" r="0.72">
      <stop offset="0" stop-color="{c4}" stop-opacity="0.85"/>
      <stop offset="1" stop-color="{c4}" stop-opacity="0"/>
    </radialGradient>
    <filter id="grain">
      <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="3" stitchTiles="stitch"/>
      <feColorMatrix type="saturate" values="0"/>
    </filter>
    <filter id="soft"><feGaussianBlur stdDeviation="{blur}"/></filter>
  </defs>
  <rect width="{w}" height="{h}" fill="url(#g)"/>
  <g filter="url(#soft)" opacity="0.75">
    <ellipse cx="{ex1}" cy="{ey1}" rx="{er1}" ry="{er1b}" fill="{c4}" opacity="0.5"/>
    <ellipse cx="{ex2}" cy="{ey2}" rx="{er2}" ry="{er2b}" fill="{c5}" opacity="0.45"/>
  </g>
  <rect width="{w}" height="{h}" fill="url(#glow)"/>
  <rect width="{w}" height="{h}" filter="url(#grain)" opacity="0.07"/>
  <g opacity="0.5" transform="translate({lx} {ly})">
    <rect x="0" y="-20" width="{lw}" height="28" rx="14" fill="#1E1A18" opacity="0.42"/>
    <text x="14" y="0" font-family="ui-monospace, Menlo, monospace" font-size="13"
          letter-spacing="2.4" fill="#FFFFFF" opacity="0.9">{label}</text>
  </g>
</svg>
"""

def make(name, w, h, c, label, alt, gx="0.3", gy="0.25"):
    c1, c2, c3, c4, c5 = c
    lw = 14 * 2 + int(len(label) * 9.6)
    svg = TPL.format(
        w=w, h=h, c1=c1, c2=c2, c3=c3, c4=c4, c5=c5, gx=gx, gy=gy,
        blur=int(min(w, h) * 0.12),
        ex1=int(w * 0.28), ey1=int(h * 0.34), er1=int(w * 0.30), er1b=int(h * 0.36),
        ex2=int(w * 0.74), ey2=int(h * 0.68), er2=int(w * 0.26), er2b=int(h * 0.30),
        lx=int(w * 0.04), ly=int(h - h * 0.055), lw=lw, label=label, alt=alt,
    )
    (OUT / name).write_text(svg, encoding="utf-8")
    return name

# palette families ------------------------------------------------------------
WARM   = ("#C9AE93", "#A98C74", "#6E5F55", "#E7D3BC", "#8C7461")  # studio / editorial
SKIN   = ("#E8CDB4", "#D8B294", "#B08D70", "#F5E4D2", "#C69A78")  # close-up skin
GRAPH  = ("#6E645F", "#4A423E", "#2A2522", "#9A8B80", "#3B3431")  # dark, moody
BLUSH  = ("#E7C4BA", "#D3A196", "#A87A6E", "#F6DDD5", "#C08D80")  # lips
GOLD   = ("#D8BE8B", "#B99A62", "#7A6238", "#F2E0B8", "#9C8047")  # gold-lit

FILES = [
    ("hero.svg",            1920, 1080, ("#B6A08C", "#8E7563", "#57493F", "#E3CDB4", "#7A6455"), "HERO — TREATMENT IN PROGRESS",  "Placeholder for the hero photograph"),
    ("service-brows.svg",   1200,  900, SKIN,  "PHOTO — POWDER BROWS",          "Placeholder for a powder brows photograph"),
    ("service-lips.svg",    1200,  900, BLUSH, "PHOTO — LIP BLUSH",             "Placeholder for a lip blush photograph"),
    ("service-camo.svg",    1200,  900, WARM,  "PHOTO — SCAR CAMOUFLAGE",       "Placeholder for a scar camouflage photograph"),
    ("portrait.svg",        1000, 1250, WARM,  "PHOTO — MILANA AT WORK",        "Placeholder for a portrait of Milana"),
    ("home-service.svg",    1200,  900, GOLD,  "PHOTO — HOME SETUP",            "Placeholder for a home service setup photograph"),
    ("studio.svg",          1200,  900, WARM,  "PHOTO — STERILE SETUP",         "Placeholder for a sterile equipment photograph"),
    ("detail-pigments.svg", 1200,  900, SKIN,  "PHOTO — PIGMENT SWATCHES",      "Placeholder for a pigment swatch photograph"),
    ("ba-brows-before.svg", 1200,  900, ("#D6B69B","#B99578","#8A6E59","#E8D0B9","#A88568"), "BEFORE — BROWS", "Placeholder: brows before"),
    ("ba-brows-after.svg",  1200,  900, ("#EBD2BB","#D6B597","#A98A70","#F7E6D6","#C4A184"), "AFTER — BROWS",  "Placeholder: brows after"),
    ("ba-lips-before.svg",  1200,  900, ("#D9B3AA","#BE8E85","#8E6961","#EDCFC7","#AC8078"), "BEFORE — LIPS",  "Placeholder: lips before"),
    ("ba-lips-after.svg",   1200,  900, ("#EFC6BB","#DBA294","#B27E70","#FBE1D8","#C89283"), "AFTER — LIPS",   "Placeholder: lips after"),
    ("ba-camo-before.svg",  1200,  900, ("#D7BDA6","#BC9C82","#8E735E","#EAD5BF","#A9866B"), "BEFORE — SCAR",  "Placeholder: scar before"),
    ("ba-camo-after.svg",   1200,  900, ("#E9D2BB","#D2B295","#A48771","#F6E5D3","#C09C7F"), "AFTER — SCAR",   "Placeholder: scar after"),
]

for name, w, h, c, label, alt in FILES:
    make(name, w, h, c, label, alt)

print("wrote", len(FILES), "placeholders to", OUT)

#!/usr/bin/env python3
"""
Generates the composite hero image showing both SunSprout Hub and SunSprout Satellite
side-by-side at their true relative physical scales.

Physical Dimensions:
  - SunSprout Hub: 56.00 mm x 85.00 mm
  - SunSprout Satellite: 27.25 mm x 51.10 mm
"""

import argparse
from pathlib import Path
from PIL import Image, ImageFilter


def crop_to_content(img: Image.Image) -> Image.Image:
    """Crops transparent borders around the board."""
    bbox = img.split()[-1].getbbox()
    if bbox:
        return img.crop(bbox)
    return img


def make_shadow(img: Image.Image, offset_y: int = 16, blur: int = 22, opacity: float = 0.5):
    """Creates a soft Gaussian drop shadow for transparent PNG images."""
    alpha = img.split()[-1]
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh_pix = sh.load()
    a_pix = alpha.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            a = a_pix[x, y]
            if a > 0:
                sh_pix[x, y] = (0, 0, 0, int(a * opacity))
    padded = Image.new("RGBA", (img.size[0] + blur * 4, img.size[1] + blur * 4), (0, 0, 0, 0))
    padded.paste(sh, (blur * 2, blur * 2), sh)
    blurred = padded.filter(ImageFilter.GaussianBlur(blur))
    return blurred, blur * 2, blur * 2 - offset_y


def main():
    parser = argparse.ArgumentParser(description="Create combined Hub + Satellite hero image")
    parser.add_argument("--hub", default="website/static/img/board-top.png", help="Path to Hub top render")
    parser.add_argument("--satellite", default="website/static/img/satellite-board-top.png", help="Path to Satellite top render")
    parser.add_argument("--output", default="website/static/img/hub-and-satellite.png", help="Output PNG path")
    args = parser.parse_args()

    hub_raw = Image.open(args.hub).convert("RGBA")
    sat_raw = Image.open(args.satellite).convert("RGBA")

    hub_cropped = crop_to_content(hub_raw)
    sat_cropped = crop_to_content(sat_raw)

    # Hub: 56.00 mm x 85.00 mm
    # Satellite: 27.25 mm x 51.10 mm
    hub_h = 1200
    hub_w = int(hub_h * (56.00 / 85.00))
    hub_resized = hub_cropped.resize((hub_w, hub_h), Image.Resampling.LANCZOS)

    sat_h = int(hub_h * (51.10 / 85.00))
    sat_w = int(sat_h * (27.25 / 51.10))
    sat_resized = sat_cropped.resize((sat_w, sat_h), Image.Resampling.LANCZOS)

    gap = 100
    pad_x = 80
    pad_top = 80
    pad_bot = 80

    canvas_w = pad_x * 2 + hub_w + sat_w + gap
    canvas_h = pad_top + pad_bot + hub_h

    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))

    hub_x = pad_x
    hub_y = pad_top

    sat_x = hub_x + hub_w + gap
    # Bottom-align Satellite to Hub baseline (RJ45 connectors align at bottom)
    sat_y = pad_top + hub_h - sat_h

    hub_shadow, hs_ox, hs_oy = make_shadow(hub_resized, offset_y=18, blur=20, opacity=0.5)
    sat_shadow, ss_ox, ss_oy = make_shadow(sat_resized, offset_y=18, blur=20, opacity=0.5)

    canvas.paste(hub_shadow, (hub_x - hs_ox, hub_y - hs_oy), hub_shadow)
    canvas.paste(sat_shadow, (sat_x - ss_ox, sat_y - ss_oy), sat_shadow)

    canvas.paste(hub_resized, (hub_x, hub_y), hub_resized)
    canvas.paste(sat_resized, (sat_x, sat_y), sat_resized)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)
    print(f"Generated {out_path} ({canvas.size[0]}x{canvas.size[1]})")


if __name__ == "__main__":
    main()

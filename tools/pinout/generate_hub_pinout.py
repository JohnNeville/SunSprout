#!/usr/bin/env python3
"""
SunSproutHub Graphical Pinout Diagram Generator

Generates a modern, publication-grade vector SVG pinout diagram (Adafruit / SparkFun style)
for SunSproutHub. Embeds the high-resolution board render with color-coded callouts,
pin numbers, functional badges, strapping caveats, and interactive data attributes.

Usage:
    python tools/pinout/generate_hub_pinout.py \
        --board-image website/static/img/board-top.png \
        --output website/static/img/pinout-top.svg
"""

import argparse
import base64
import os
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Pin definitions for SunSproutHub
# ---------------------------------------------------------------------------

J7_PINS = [
    {"pin": 1, "board_y": 13.07, "tags": [("3V3_USER", "pwr"), ("Switched 3.3V", "pwr")]},
    {"pin": 2, "board_y": 15.61, "tags": [("GND", "gnd")]},
    {"pin": 3, "board_y": 18.15, "tags": [("GPIO0", "lp-gpio"), ("LP_GPIO0 / Wake", "lp-gpio")]},
    {"pin": 4, "board_y": 20.69, "tags": [("GPIO1", "gpio"), ("Free IO", "gpio")]},
    {"pin": 5, "board_y": 23.23, "tags": [("GPIO7", "gpio"), ("Free IO", "gpio"), ("SDIO Strap", "strap")]},
    {"pin": 6, "board_y": 25.77, "tags": [("GPIO9", "i2c-user"), ("SDA_USER", "i2c-user")]},
    {"pin": 7, "board_y": 28.31, "tags": [("GPIO10", "i2c-user"), ("SCL_USER", "i2c-user")]},
    {"pin": 8, "board_y": 30.85, "tags": [("GND", "gnd")]},
    {"pin": 9, "board_y": 33.39, "tags": [("3V3_USER", "pwr"), ("Switched 3.3V", "pwr")]},
]

J8_PINS = [
    {"pin": 1, "board_y": 13.82, "tags": [("3V3_USER", "pwr"), ("Switched 3.3V", "pwr")]},
    {"pin": 2, "board_y": 16.36, "tags": [("GND", "gnd")]},
    {"pin": 3, "board_y": 18.90, "tags": [("GPIO26", "gpio"), ("Free IO", "gpio"), ("Boot Strap", "strap")]},
    {"pin": 4, "board_y": 21.44, "tags": [("GPIO25", "gpio"), ("Free IO", "gpio"), ("Boot Strap", "strap")]},
    {"pin": 5, "board_y": 23.98, "tags": [("GPIO11", "uart"), ("U0TXD (Console)", "uart")]},
    {"pin": 6, "board_y": 26.52, "tags": [("GPIO12", "uart"), ("U0RXD (Console)", "uart")]},
    {"pin": 7, "board_y": 29.06, "tags": [("GPIO24", "gpio"), ("Free IO", "gpio")]},
    {"pin": 8, "board_y": 31.60, "tags": [("GPIO27", "gpio"), ("Free IO", "gpio"), ("Boot Strap", "strap")]},
    {"pin": 9, "board_y": 34.14, "tags": [("GPIO5", "gpio"), ("Free IO", "gpio")]},
]

LEGEND_ITEMS = [
    ("Power & Solar (3V3 / VIN)", "pwr"),
    ("Ground (GND)", "gnd"),
    ("Free GPIO", "gpio"),
    ("LP Core GPIO / Wake", "lp-gpio"),
    ("User I2C (HP_I2C)", "i2c-user"),
    ("Internal I2C (LP_I2C)", "i2c-int"),
    ("UART Console (U0TXD/RXD)", "uart"),
    ("Strapping Pins", "strap"),
    ("Buttons / Reset / Wake", "btn"),
    ("Differential I2C", "diff"),
    ("USB-C Native", "usb"),
]


# ---------------------------------------------------------------------------
# SVG Generator Implementation
# ---------------------------------------------------------------------------

def generate_pinout_svg(board_image_path: str, output_svg_path: str, css_path: str = None):
    """Renders the standalone vector SVG pinout diagram with rich typography and interactivity."""
    
    # Board physical dimensions
    BOARD_MM_W = 56.0
    BOARD_MM_H = 85.0
    
    # Canvas dimensions
    CANVAS_W = 1520
    CANVAS_H = 1040
    
    # Board placement on canvas
    BOARD_PIX_H = 650
    BOARD_PIX_W = int(BOARD_PIX_H * (BOARD_MM_W / BOARD_MM_H))  # ~428px
    BOARD_X = (CANVAS_W - BOARD_PIX_W) // 2
    BOARD_Y = 105
    
    def mm_to_canvas(bx_mm, by_mm):
        cx = BOARD_X + (bx_mm / BOARD_MM_W) * BOARD_PIX_W
        cy = BOARD_Y + (by_mm / BOARD_MM_H) * BOARD_PIX_H
        return cx, cy

    # Read CSS
    css_content = ""
    if css_path and os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

    # Image source (embed as base64 data URI if found)
    image_href = ""
    if os.path.exists(board_image_path):
        try:
            from PIL import Image
            import io
            im = Image.open(board_image_path)
            if im.mode in ('RGBA', 'LA'):
                pix = im.load()
                w, h = im.size
                min_x, max_x = w, 0
                min_y, max_y = h, 0
                has_solid = False
                for y in range(h):
                    for x in range(w):
                        if pix[x, y][3] > 128:
                            has_solid = True
                            if x < min_x: min_x = x
                            if x > max_x: max_x = x
                            if y < min_y: min_y = y
                            if y > max_y: max_y = y
                if has_solid and (min_x > 0 or min_y > 0 or max_x < w - 1 or max_y < h - 1):
                    im = im.crop((min_x, min_y, max_x + 1, max_y + 1))
                    cpix = im.load()
                    for cy in range(im.size[1]):
                        for cx in range(im.size[0]):
                            if cpix[cx, cy][3] < 128:
                                cpix[cx, cy] = (0, 0, 0, 0)
            buf = io.BytesIO()
            im.save(buf, format="PNG")
            encoded = base64.b64encode(buf.getvalue()).decode("ascii")
            image_href = f"data:image/png;base64,{encoded}"
        except Exception:
            with open(board_image_path, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode("ascii")
                ext = Path(board_image_path).suffix.lower().lstrip(".")
                mime = "image/png" if ext == "png" else "image/jpeg"
                image_href = f"data:{mime};base64,{encoded}"
    else:
        image_href = os.path.basename(board_image_path)

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS_W} {CANVAS_H}" width="100%" height="100%" class="diagram" id="hub-pinout-svg">',
        '  <defs>',
        f'    <style type="text/css"><![CDATA[\n{css_content}\n]]></style>',
        '    <filter id="shadow" x="-5%" y="-5%" width="115%" height="115%">',
        '      <feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="#000000" flood-opacity="0.6"/>',
        '    </filter>',
        '  </defs>',
        '',
        '  <!-- Background Canvas -->',
        f'  <rect width="{CANVAS_W}" height="{CANVAS_H}" fill="#0b1320"/>',
        f'  <rect x="20" y="20" width="{CANVAS_W - 40}" height="{CANVAS_H - 40}" class="panel"/>',
        '',
        '  <!-- Header Title -->',
        '  <g transform="translate(50, 68)">',
        '    <text class="title">SunSproutHub Pinout &amp; Signal Diagram</text>',
        '    <text y="26" class="subtitle">ESP32-C5-WROOM-1U • Dual Independent I2C Buses • BQ25798 Charger • BQ34Z100 Fuel Gauge</text>',
        f'    <rect x="{CANVAS_W - 250}" y="-20" width="150" height="30" rx="6" fill="#0f2b48" stroke="#0284c7" stroke-width="1.2"/>',
        f'    <text x="{CANVAS_W - 175}" y="-1" class="header-tag" text-anchor="middle">PCB REV 1.0</text>',
        '  </g>',
        '',
        '  <!-- Board Image Layer -->',
        '  <g filter="url(#shadow)">',
        f'    <image href="{image_href}" x="{BOARD_X}" y="{BOARD_Y}" width="{BOARD_PIX_W}" height="{BOARD_PIX_H}" preserveAspectRatio="none"/>',
        '  </g>',
        '',
    ]

    # Helper function to render a badge tag
    def render_badge(x, y, text, tag_type, is_right_aligned=False, width=None):
        char_len = len(text)
        w = width if width else (char_len * 8.6 + 22)
        h = 28
        rx = x - w if is_right_aligned else x
        rect_svg = f'<rect x="{rx:.1f}" y="{y - h/2:.1f}" width="{w:.1f}" height="{h:.1f}" class="badge-bg"/>'
        text_x = rx + w / 2
        text_svg = f'<text x="{text_x:.1f}" y="{y:.1f}" class="badge-text" text-anchor="middle">{text}</text>'
        return f'<g class="tag-{tag_type}">{rect_svg}{text_svg}</g>', w

    # Helper function to render pin number pill
    def render_pin_pill(x, y, pnum, is_right_side=False):
        w, h = 32, 28
        rx = x if is_right_side else (x - w)
        rect = f'<rect x="{rx:.1f}" y="{y - h/2:.1f}" width="{w:.1f}" height="{h:.1f}" class="pin-num-bg"/>'
        text_x = rx + w / 2
        text = f'<text x="{text_x:.1f}" y="{y:.1f}" class="pin-num-text">{pnum}</text>'
        return f'<g>{rect}{text}</g>'

    # -----------------------------------------------------------------------
    # Left Header: J7 (9 pins)
    # -----------------------------------------------------------------------
    svg_lines.append('  <!-- J7 Expansion Header (Left Side) -->')
    j7_start_y = 175
    j7_spacing = 48
    end_x = 460
    
    svg_lines.append(f'  <text x="{end_x}" y="{j7_start_y - 25}" class="header-tag" text-anchor="end">J7 EXPANSION (2.54MM)</text>')

    for i, p in enumerate(J7_PINS):
        label_y = j7_start_y + i * j7_spacing
        pin_cx, pin_cy = mm_to_canvas(3.10, p["board_y"])
        elbow_x = BOARD_X - 35
        
        tags_csv = ",".join(t[1] for t in p["tags"])
        primary_name = p["tags"][0][0]
        
        svg_lines.append(f'  <g class="callout-group" data-pin="J7.{p["pin"]}" data-tags="{tags_csv}" data-name="{primary_name}">')
        svg_lines.append(f'    <path d="M {pin_cx:.1f} {pin_cy:.1f} L {elbow_x} {label_y} L {end_x} {label_y}" class="leader-line"/>')
        svg_lines.append(f'    <circle cx="{pin_cx:.1f}" cy="{pin_cy:.1f}" r="4.5" class="pin-dot pin-dot-{p["tags"][0][1]}"/>')
        svg_lines.append(f'    {render_pin_pill(end_x, label_y, p["pin"], is_right_side=False)}')
        
        curr_x = end_x - 38
        for text, tag_type in p["tags"]:
            badge_svg, badge_w = render_badge(curr_x, label_y, text, tag_type, is_right_aligned=True)
            svg_lines.append(f'    {badge_svg}')
            curr_x -= (badge_w + 6)
        svg_lines.append('  </g>')

    # -----------------------------------------------------------------------
    # Right Header: J8 (9 pins)
    # -----------------------------------------------------------------------
    svg_lines.append('  <!-- J8 Expansion Header (Right Side) -->')
    j8_start_y = 175
    j8_spacing = 48
    start_x = BOARD_X + BOARD_PIX_W + 55
    
    svg_lines.append(f'  <text x="{start_x}" y="{j8_start_y - 25}" class="header-tag" text-anchor="start">J8 EXPANSION (2.54MM)</text>')

    for i, p in enumerate(J8_PINS):
        label_y = j8_start_y + i * j8_spacing
        pin_cx, pin_cy = mm_to_canvas(53.00, p["board_y"])
        elbow_x = BOARD_X + BOARD_PIX_W + 35
        
        tags_csv = ",".join(t[1] for t in p["tags"])
        primary_name = p["tags"][0][0]
        
        svg_lines.append(f'  <g class="callout-group" data-pin="J8.{p["pin"]}" data-tags="{tags_csv}" data-name="{primary_name}">')
        svg_lines.append(f'    <path d="M {pin_cx:.1f} {pin_cy:.1f} L {elbow_x} {label_y} L {start_x} {label_y}" class="leader-line"/>')
        svg_lines.append(f'    <circle cx="{pin_cx:.1f}" cy="{pin_cy:.1f}" r="4.5" class="pin-dot pin-dot-{p["tags"][0][1]}"/>')
        svg_lines.append(f'    {render_pin_pill(start_x, label_y, p["pin"], is_right_side=True)}')
        
        curr_x = start_x + 38
        for text, tag_type in p["tags"]:
            badge_svg, badge_w = render_badge(curr_x, label_y, text, tag_type, is_right_aligned=False)
            svg_lines.append(f'    {badge_svg}')
            curr_x += (badge_w + 6)
        svg_lines.append('  </g>')

    # -----------------------------------------------------------------------
    # Top Callouts: SW1 & SW2 Buttons
    # -----------------------------------------------------------------------
    svg_lines.append('  <!-- Tactile Buttons (Top Area) -->')
    # SW1 (Reset)
    sw1_cx, sw1_cy = mm_to_canvas(42.40, 4.03)
    sw1_label_y = 82
    sw1_label_x = BOARD_X + BOARD_PIX_W + 120
    svg_lines.append('  <g class="callout-group" data-pin="SW1" data-tags="btn,pwr" data-name="SW1: Reset">')
    svg_lines.append(f'    <path d="M {sw1_cx:.1f} {sw1_cy:.1f} L {sw1_cx} {sw1_label_y} L {sw1_label_x} {sw1_label_y}" class="leader-line"/>')
    svg_lines.append(f'    <circle cx="{sw1_cx:.1f}" cy="{sw1_cy:.1f}" r="4.5" class="pin-dot pin-dot-pwr"/>')
    curr_x = sw1_label_x + 6
    for text, tag_type in [("SW1", "btn"), ("RESET / EN", "btn"), ("CHIP_PU", "pwr")]:
        badge_svg, badge_w = render_badge(curr_x, sw1_label_y, text, tag_type, is_right_aligned=False)
        svg_lines.append(f'    {badge_svg}')
        curr_x += (badge_w + 6)
    svg_lines.append('  </g>')

    # SW2 (Bootloader GPIO28)
    sw2_cx, sw2_cy = mm_to_canvas(42.40, 10.65)
    sw2_label_y = 118
    sw2_label_x = BOARD_X + BOARD_PIX_W + 120
    svg_lines.append('  <g class="callout-group" data-pin="SW2" data-tags="btn,strap" data-name="SW2: Bootloader">')
    svg_lines.append(f'    <path d="M {sw2_cx:.1f} {sw2_cy:.1f} L {sw2_cx + 40} {sw2_label_y} L {sw2_label_x} {sw2_label_y}" class="leader-line"/>')
    svg_lines.append(f'    <circle cx="{sw2_cx:.1f}" cy="{sw2_cy:.1f}" r="4.5" class="pin-dot pin-dot-strap"/>')
    curr_x = sw2_label_x + 6
    for text, tag_type in [("SW2", "btn"), ("GPIO28", "strap"), ("Download Boot Strap", "strap")]:
        badge_svg, badge_w = render_badge(curr_x, sw2_label_y, text, tag_type, is_right_aligned=False)
        svg_lines.append(f'    {badge_svg}')
        curr_x += (badge_w + 6)
    svg_lines.append('  </g>')

    # -----------------------------------------------------------------------
    # Center / Bottom Peripherals: Stemma QT, USB-C, Solar, Buttons, Differential
    # -----------------------------------------------------------------------
    svg_lines.append('  <!-- Peripherals & Ports -->')
    # J6 (Stemma QT Int)
    j6_cx, j6_cy = mm_to_canvas(39.81, 28.32)
    j6_label_y = 615
    j6_label_x = BOARD_X + BOARD_PIX_W + 55
    svg_lines.append('  <g class="callout-group" data-pin="J6" data-tags="i2c-int" data-name="J6: STEMMA QT (Internal)">')
    svg_lines.append(f'    <path d="M {j6_cx:.1f} {j6_cy:.1f} L {j6_cx + 25} {j6_label_y} L {j6_label_x} {j6_label_y}" class="leader-line"/>')
    svg_lines.append(f'    <circle cx="{j6_cx:.1f}" cy="{j6_cy:.1f}" r="4.5" class="pin-dot pin-dot-i2c-int"/>')
    curr_x = j6_label_x + 6
    for text, tag_type in [("J6", "i2c-int"), ("STEMMA QT Internal", "i2c-int"), ("LP_I2C (GPIO2/3)", "i2c-int")]:
        badge_svg, badge_w = render_badge(curr_x, j6_label_y, text, tag_type, is_right_aligned=False)
        svg_lines.append(f'    {badge_svg}')
        curr_x += (badge_w + 6)
    svg_lines.append('  </g>')

    # J203 (Stemma QT User)
    j203_cx, j203_cy = mm_to_canvas(39.81, 36.61)
    j203_label_y = 665
    j203_label_x = BOARD_X + BOARD_PIX_W + 55
    svg_lines.append('  <g class="callout-group" data-pin="J203" data-tags="i2c-user" data-name="J203: STEMMA QT (User)">')
    svg_lines.append(f'    <path d="M {j203_cx:.1f} {j203_cy:.1f} L {j203_cx + 35} {j203_label_y} L {j203_label_x} {j203_label_y}" class="leader-line"/>')
    svg_lines.append(f'    <circle cx="{j203_cx:.1f}" cy="{j203_cy:.1f}" r="4.5" class="pin-dot pin-dot-i2c-user"/>')
    curr_x = j203_label_x + 6
    for text, tag_type in [("J203", "i2c-user"), ("STEMMA QT User", "i2c-user"), ("HP_I2C (GPIO9/10)", "i2c-user")]:
        badge_svg, badge_w = render_badge(curr_x, j203_label_y, text, tag_type, is_right_aligned=False)
        svg_lines.append(f'    {badge_svg}')
        curr_x += (badge_w + 6)
    svg_lines.append('  </g>')

    # SW3 (Wake Button)
    sw3_cx, sw3_cy = mm_to_canvas(35.79, 55.83)
    sw3_label_y = 715
    sw3_label_x = BOARD_X + BOARD_PIX_W + 55
    svg_lines.append('  <g class="callout-group" data-pin="SW3" data-tags="btn,pwr" data-name="SW3: Wake Button">')
    svg_lines.append(f'    <path d="M {sw3_cx:.1f} {sw3_cy:.1f} L {sw3_cx + 45} {sw3_label_y} L {sw3_label_x} {sw3_label_y}" class="leader-line"/>')
    svg_lines.append(f'    <circle cx="{sw3_cx:.1f}" cy="{sw3_cy:.1f}" r="4.5" class="pin-dot pin-dot-btn"/>')
    curr_x = sw3_label_x + 6
    for text, tag_type in [("SW3", "btn"), ("WAKE", "btn"), ("Ship-Mode Wake (QON)", "pwr")]:
        badge_svg, badge_w = render_badge(curr_x, sw3_label_y, text, tag_type, is_right_aligned=False)
        svg_lines.append(f'    {badge_svg}')
        curr_x += (badge_w + 6)
    svg_lines.append('  </g>')

    # USBC1 (USB-C Native Receptacle)
    usbc_cx, usbc_cy = mm_to_canvas(2.67, 47.71)
    usbc_label_y = 615
    usbc_label_x = BOARD_X - 55
    svg_lines.append('  <g class="callout-group" data-pin="USBC1" data-tags="usb" data-name="USBC1: USB-C Native">')
    svg_lines.append(f'    <path d="M {usbc_cx:.1f} {usbc_cy:.1f} L {usbc_cx - 25} {usbc_label_y} L {usbc_label_x} {usbc_label_y}" class="leader-line"/>')
    svg_lines.append(f'    <circle cx="{usbc_cx:.1f}" cy="{usbc_cy:.1f}" r="4.5" class="pin-dot pin-dot-usb"/>')
    curr_x = usbc_label_x - 6
    for text, tag_type in [("USBC1", "usb"), ("USB-C Native", "usb"), ("D+/D- • BC1.2", "usb")]:
        badge_svg, badge_w = render_badge(curr_x, usbc_label_y, text, tag_type, is_right_aligned=True)
        svg_lines.append(f'    {badge_svg}')
        curr_x -= (badge_w + 6)
    svg_lines.append('  </g>')

    # CN5 (Solar Input Terminal Block)
    cn5_cx, cn5_cy = mm_to_canvas(4.06, 65.58)
    cn5_label_y = 665
    cn5_label_x = BOARD_X - 55
    svg_lines.append('  <g class="callout-group" data-pin="CN5" data-tags="pwr" data-name="CN5: Solar Input Terminal">')
    svg_lines.append(f'    <path d="M {cn5_cx:.1f} {cn5_cy:.1f} L {cn5_cx - 30} {cn5_label_y} L {cn5_label_x} {cn5_label_y}" class="leader-line"/>')
    svg_lines.append(f'    <circle cx="{cn5_cx:.1f}" cy="{cn5_cy:.1f}" r="4.5" class="pin-dot pin-dot-pwr"/>')
    curr_x = cn5_label_x - 6
    for text, tag_type in [("CN5", "pwr"), ("Solar Input", "pwr"), ("VIN_SOLAR / GND", "pwr")]:
        badge_svg, badge_w = render_badge(curr_x, cn5_label_y, text, tag_type, is_right_aligned=True)
        svg_lines.append(f'    {badge_svg}')
        curr_x -= (badge_w + 6)
    svg_lines.append('  </g>')

    # J201 / J202 (Differential I2C)
    diff_cx, diff_cy = mm_to_canvas(28.00, 80.00)
    diff_label_y = 715
    diff_label_x = BOARD_X - 55
    svg_lines.append('  <g class="callout-group" data-pin="J201/J202" data-tags="diff" data-name="J201/J202: Differential I2C">')
    svg_lines.append(f'    <path d="M {diff_cx:.1f} {diff_cy:.1f} L {diff_cx - 80} {diff_label_y} L {diff_label_x} {diff_label_y}" class="leader-line"/>')
    svg_lines.append(f'    <circle cx="{diff_cx:.1f}" cy="{diff_cy:.1f}" r="4.5" class="pin-dot pin-dot-diff"/>')
    curr_x = diff_label_x - 6
    for text, tag_type in [("J201 / J202", "diff"), ("Diff I2C (PCA9615)", "diff"), ("Dual 8P8C / RJ45", "diff")]:
        badge_svg, badge_w = render_badge(curr_x, diff_label_y, text, tag_type, is_right_aligned=True)
        svg_lines.append(f'    {badge_svg}')
        curr_x -= (badge_w + 6)
    svg_lines.append('  </g>')

    # -----------------------------------------------------------------------
    # Legend Bar (Footer)
    # -----------------------------------------------------------------------
    legend_y = CANVAS_H - 125
    legend_h = 100
    svg_lines.append('  <!-- Legend Panel -->')
    svg_lines.append(f'  <rect x="50" y="{legend_y}" width="{CANVAS_W - 100}" height="{legend_h}" rx="10" fill="#09101d" stroke="#1e293b" stroke-width="1.2"/>')
    svg_lines.append(f'  <text x="70" y="{legend_y + 22}" class="legend-title">Signal Classification Legend (Click to Filter)</text>')

    leg_x = 70
    leg_item_y = legend_y + 52
    line_h = 34
    for name, tag_type in LEGEND_ITEMS:
        badge_svg, w = render_badge(leg_x, leg_item_y, name, tag_type, is_right_aligned=False)
        if leg_x + w > CANVAS_W - 70:
            leg_x = 70
            leg_item_y += line_h
            badge_svg, w = render_badge(leg_x, leg_item_y, name, tag_type, is_right_aligned=False)
        svg_lines.append(f'  <g class="legend-badge" data-tag="{tag_type}" style="cursor: pointer;">{badge_svg}</g>')
        leg_x += (w + 14)

    svg_lines.append('</svg>')
    
    # Write output
    os.makedirs(os.path.dirname(os.path.abspath(output_svg_path)), exist_ok=True)
    with open(output_svg_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))
    print(f"Generated pinout diagram: {output_svg_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate SunSproutHub SVG Pinout Diagram")
    parser.add_argument("--board-image", default="website/static/img/board-top.png", help="Path to rendered board top image")
    parser.add_argument("--output", default="website/static/img/pinout-top.svg", help="Output path for SVG diagram")
    parser.add_argument("--css", default="tools/pinout/styles.css", help="Path to CSS stylesheet")
    args = parser.parse_args()

    generate_pinout_svg(args.board_image, args.output, args.css)


if __name__ == "__main__":
    main()

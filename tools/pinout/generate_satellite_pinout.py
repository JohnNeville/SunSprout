#!/usr/bin/env python3
"""
SunSprout Satellite Graphical Pinout & Jumper Diagram Generator

Generates publication-grade vector SVG diagrams for SunSprout Satellite:
1. Top View (satellite-pinout-top.svg): Sensor ports (J2-J6), RJ45 (J1), Aux header (J7), Local power (J9), ICs.
2. Bottom View (satellite-pinout-bottom.svg): Configuration jumpers (JP1, JP16, JP11, JP13, JP17, JP18)
   and address selection truth tables.

Includes enlarged typography, interactive data attributes, and category tagging.

Usage:
    python tools/pinout/generate_satellite_pinout.py
"""

import argparse
import base64
import io
import os
from pathlib import Path
from PIL import Image


# ---------------------------------------------------------------------------
# Board physical dimensions
# ---------------------------------------------------------------------------
BOARD_MM_W = 27.25
BOARD_MM_H = 51.10

CANVAS_W = 1520
CANVAS_H = 1040

BOARD_PIX_H = 650
BOARD_PIX_W = int(BOARD_PIX_H * (BOARD_MM_W / BOARD_MM_H))  # ~346px
BOARD_X = (CANVAS_W - BOARD_PIX_W) // 2
BOARD_Y = 105


def mm_to_canvas_top(bx_mm, by_mm):
    cx = BOARD_X + (bx_mm / BOARD_MM_W) * BOARD_PIX_W
    cy = BOARD_Y + (by_mm / BOARD_MM_H) * BOARD_PIX_H
    return cx, cy


def mm_to_canvas_bottom(bx_mm, by_mm):
    # Mirrored horizontally for bottom view
    cx = BOARD_X + ((BOARD_MM_W - bx_mm) / BOARD_MM_W) * BOARD_PIX_W
    cy = BOARD_Y + (by_mm / BOARD_MM_H) * BOARD_PIX_H
    return cx, cy


def load_and_crop_image(image_path: str):
    if not os.path.exists(image_path):
        return ""
    try:
        im = Image.open(image_path)
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
        return f"data:image/png;base64,{encoded}"
    except Exception:
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("ascii")
            return f"data:image/png;base64,{encoded}"


import html


def render_badge(x, y, text, tag_type, is_right_aligned=False, width=None):
    char_len = len(text)
    w = width if width else (char_len * 8.6 + 22)
    h = 28
    rx = x - w if is_right_aligned else x
    rect_svg = f'<rect x="{rx:.1f}" y="{y - h/2:.1f}" width="{w:.1f}" height="{h:.1f}" class="badge-bg"/>'
    text_x = rx + w / 2
    escaped_text = html.escape(text)
    text_svg = f'<text x="{text_x:.1f}" y="{y:.1f}" class="badge-text" text-anchor="middle">{escaped_text}</text>'
    return f'<g class="tag-{tag_type}">{rect_svg}{text_svg}</g>', w


def render_pin_pill(x, y, pnum, is_right_side=False):
    w, h = 32, 28
    rx = x if is_right_side else (x - w)
    rect = f'<rect x="{rx:.1f}" y="{y - h/2:.1f}" width="{w:.1f}" height="{h:.1f}" class="pin-num-bg"/>'
    text_x = rx + w / 2
    text = f'<text x="{text_x:.1f}" y="{y:.1f}" class="pin-num-text">{pnum}</text>'
    return f'<g>{rect}{text}</g>'


# ---------------------------------------------------------------------------
# 1. TOP VIEW DIAGRAM GENERATOR
# ---------------------------------------------------------------------------

def generate_satellite_top_svg(board_image_path: str, output_svg_path: str, css_path: str):
    css_content = ""
    if css_path and os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

    extra_css = """
.tag-analog .badge-bg { fill: #172554; stroke: #2563eb; }
.tag-analog .badge-text { fill: #bfdbfe; }
.tag-onewire .badge-bg { fill: #052e16; stroke: #16a34a; }
.tag-onewire .badge-text { fill: #bbf7d0; }
.tag-jumper .badge-bg { fill: #4a044e; stroke: #c026d3; }
.tag-jumper .badge-text { fill: #f5d0fe; }
.pin-dot-analog { fill: #3b82f6; }
.pin-dot-onewire { fill: #22c55e; }
.pin-dot-jumper { fill: #c026d3; }
"""
    css_content += extra_css
    image_href = load_and_crop_image(board_image_path)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS_W} {CANVAS_H}" width="100%" height="100%" class="diagram" id="satellite-top-svg">',
        '  <defs>',
        f'    <style type="text/css"><![CDATA[\n{css_content}\n]]></style>',
        '    <filter id="shadow" x="-5%" y="-5%" width="115%" height="115%">',
        '      <feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="#000000" flood-opacity="0.6"/>',
        '    </filter>',
        '  </defs>',
        f'  <rect width="{CANVAS_W}" height="{CANVAS_H}" fill="#0b1320"/>',
        f'  <rect x="20" y="20" width="{CANVAS_W - 40}" height="{CANVAS_H - 40}" class="panel"/>',
        '',
        '  <!-- Header Title -->',
        '  <g transform="translate(50, 68)">',
        '    <text class="title">SunSprout Satellite Pinout &amp; Port Diagram</text>',
        '    <text y="26" class="subtitle">Differential I2C Leaf Node • 4× Soil Moisture Probes • 1-Wire DS18B20 Temperature • RJ45 Bus</text>',
        f'    <rect x="{CANVAS_W - 250}" y="-20" width="150" height="30" rx="6" fill="#0f2b48" stroke="#0284c7" stroke-width="1.2"/>',
        f'    <text x="{CANVAS_W - 175}" y="-1" class="header-tag" text-anchor="middle">PCB REV 1.0</text>',
        '  </g>',
        '',
        '  <!-- Board Image -->',
        '  <g filter="url(#shadow)">',
        f'    <image href="{image_href}" x="{BOARD_X}" y="{BOARD_Y}" width="{BOARD_PIX_W}" height="{BOARD_PIX_H}" preserveAspectRatio="none"/>',
        '  </g>',
        '',
    ]

    # --- LEFT SIDE CALLOUTS (JST PH Sensor Ports) ---
    left_ports = [
        ("J6", 8.30, "1-Wire Temp", [("ONEWIRE_DQ", "onewire"), ("SAT_3V3", "pwr"), ("GND", "gnd")]),
        ("J2", 17.40, "Moisture 1", [("MOIST1 (AIN0)", "analog"), ("SAT_3V3", "pwr"), ("GND", "gnd")]),
        ("J3", 26.50, "Moisture 2", [("MOIST2 (AIN1)", "analog"), ("SAT_3V3", "pwr"), ("GND", "gnd")]),
        ("J4", 35.50, "Moisture 3", [("MOIST3 (AIN2)", "analog"), ("SAT_3V3", "pwr"), ("GND", "gnd")]),
        ("J5", 44.50, "Moisture 4", [("MOIST4 (AIN3)", "analog"), ("SAT_3V3", "pwr"), ("GND", "gnd")]),
    ]

    start_y = 160
    gap_y = 108
    end_x = 480
    svg.append(f'  <text x="{end_x}" y="{start_y - 30}" class="header-tag" text-anchor="end">SENSOR INPUT PORTS (JST PH 2.0MM)</text>')

    for i, (pname, by_mm, ptitle, tags) in enumerate(left_ports):
        label_y = start_y + i * gap_y
        pcx, pcy = mm_to_canvas_top(3.65, by_mm)
        elbow_x = BOARD_X - 45

        tags_csv = ",".join(t[1] for t in tags)
        svg.append(f'  <g class="callout-group" data-pin="{pname}" data-tags="{tags_csv}" data-name="{pname}: {ptitle}">')
        svg.append(f'    <path d="M {pcx:.1f} {pcy:.1f} L {elbow_x} {label_y} L {end_x} {label_y}" class="leader-line"/>')
        svg.append(f'    <circle cx="{pcx:.1f}" cy="{pcy:.1f}" r="4.5" class="pin-dot pin-dot-analog"/>')

        # Port badge
        b_svg, bw = render_badge(end_x, label_y, f"{pname}: {ptitle}", "i2c-user", is_right_aligned=True)
        svg.append(f'    {b_svg}')

        curr_x = end_x - bw - 8
        for ttext, ttype in tags:
            tag_svg, tw = render_badge(curr_x, label_y, ttext, ttype, is_right_aligned=True)
            svg.append(f'    {tag_svg}')
            curr_x -= (tw + 6)
        svg.append('  </g>')

    # --- RIGHT SIDE CALLOUTS (Power, Buffer, Headers, RJ45, TVS, Term, Qwiic, 1-Wire Master) ---
    right_items = [
        ("JP19", 13.55, 2.10, "Power LED Cut Jumper", [("JP19", "jumper"), ("NC Trace Jumper", "strap"), ("Cut to Disable LED", "strap")], "jumper,strap", "jumper"),
        ("LED1", 17.50, 3.30, "Power Status LED", [("LED1", "pwr"), ("SAT_3V3 Active", "pwr"), ("PWR (Green)", "pwr")], "pwr", "pwr"),
        ("U3", 13.05, 7.06, "DS2482 1-Wire Master", [("U3", "onewire"), ("DS2482S-100+", "onewire"), ("1-Wire Master", "onewire")], "onewire,i2c-user,sensor", "onewire"),
        ("JP11", 20.30, 8.90, "I2C Pull-Ups", [("JP11", "jumper"), ("4.7kΩ SDA/SCL", "jumper"), ("Single-Cut Trace", "strap")], "jumper,strap", "jumper"),
        ("J9", 24.20, 14.50, "Satellite Power Input", [("J9", "pwr"), ("SAT_3V3", "pwr"), ("GND", "gnd")], "pwr,gnd", "pwr"),
        ("J8", 10.40, 14.70, "Qwiic I2C Port", [("J8", "i2c-user"), ("Qwiic / STEMMA QT", "i2c-user"), ("Local I2C Bus", "i2c-user")], "i2c-user,diff,sensor", "i2c-user"),
        ("U1", 16.20, 16.50, "PCA9615 Transceiver", [("U1", "diff"), ("PCA9615DPZ", "diff"), ("Diff I2C Transceiver", "diff")], "diff", "diff"),
        ("J7", 24.20, 25.10, "Cable Power Tap", [("J7", "pwr"), ("VCC_1", "pwr"), ("GND_1", "gnd"), ("GND_2", "gnd"), ("VCC_2", "pwr")], "pwr,gnd", "pwr"),
        ("U2", 8.05, 26.45, "ADS1115 16-Bit ADC", [("U2", "analog"), ("ADS1115IDGS", "analog"), ("16-Bit 4-Ch ADC", "analog")], "analog,sensor", "analog"),
        ("R3-R8", 16.00, 26.50, "Bus Termination Array", [("R3-R8", "diff"), ("100Ω Bus Termination", "diff"), ("390Ω Bias", "diff")], "diff", "diff"),
        ("U4", 17.92, 32.54, "USBLC6-4SC6 TVS", [("U4", "diff"), ("USBLC6-4SC6", "diff"), ("TVS ESD Protection", "diff")], "diff", "diff"),
        ("J1", 15.95, 45.20, "RJ45 Bus", [("J1", "diff"), ("RJHSE5380 (8P8C)", "diff"), ("Diff I2C + Dual Power", "diff")], "diff,pwr", "diff"),
    ]

    r_start_y = 135
    r_gap_y = 64
    start_x = BOARD_X + BOARD_PIX_W + 55
    svg.append(f'  <text x="{start_x}" y="{r_start_y - 25}" class="header-tag" text-anchor="start">COMMUNICATION &amp; POWER INTERFACES</text>')

    for i, (ref, bx_mm, by_mm, title, tags, tags_csv, dot_type) in enumerate(right_items):
        label_y = r_start_y + i * r_gap_y
        pcx, pcy = mm_to_canvas_top(bx_mm, by_mm)
        elbow_x = BOARD_X + BOARD_PIX_W + 35

        svg.append(f'  <g class="callout-group" data-pin="{ref}" data-tags="{tags_csv}" data-name="{ref}: {title}">')
        svg.append(f'    <path d="M {pcx:.1f} {pcy:.1f} L {elbow_x} {label_y} L {start_x} {label_y}" class="leader-line"/>')
        svg.append(f'    <circle cx="{pcx:.1f}" cy="{pcy:.1f}" r="4.5" class="pin-dot pin-dot-{dot_type}"/>')

        curr_x = start_x
        for ttext, ttype in tags:
            tag_svg, tw = render_badge(curr_x, label_y, ttext, ttype, is_right_aligned=False)
            svg.append(f'    {tag_svg}')
            curr_x += (tw + 6)
        svg.append('  </g>')

    # --- FOOTER LEGEND ---
    legend_y = CANVAS_H - 125
    svg.append('  <!-- Legend Panel -->')
    svg.append(f'  <rect x="50" y="{legend_y}" width="{CANVAS_W - 100}" height="100" rx="10" fill="#09101d" stroke="#1e293b" stroke-width="1.2"/>')
    svg.append(f'  <text x="70" y="{legend_y + 22}" class="legend-title">Signal Classification Legend (Top View)</text>')

    TOP_LEGEND = [
        ("Power Rails (SAT_3V3 / RJ45_VCC_1 / RJ45_VCC_2)", "pwr"),
        ("Ground (GND / RJ45_GND_1 / RJ45_GND_2)", "gnd"),
        ("Differential I2C (DSCL / DSDA)", "diff"),
        ("Single-Ended I2C (Qwiic / Local)", "i2c-user"),
        ("Analog Moisture Probes (MOIST1..4)", "analog"),
        ("1-Wire Bus (DS18B20 / DS2482)", "onewire"),
        ("Configuration Jumpers", "jumper"),
        ("Strapping / Trace Cuts", "strap"),
    ]

    leg_x = 70
    leg_item_y = legend_y + 52
    for name, tag_type in TOP_LEGEND:
        b_svg, w = render_badge(leg_x, leg_item_y, name, tag_type, is_right_aligned=False)
        if leg_x + w > CANVAS_W - 70:
            leg_x = 70
            leg_item_y += 34
            b_svg, w = render_badge(leg_x, leg_item_y, name, tag_type, is_right_aligned=False)
        svg.append(f'  <g class="legend-badge" data-tag="{tag_type}" style="cursor: pointer;">{b_svg}</g>')
        leg_x += (w + 14)

    svg.append('</svg>')

    os.makedirs(os.path.dirname(os.path.abspath(output_svg_path)), exist_ok=True)
    with open(output_svg_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated Satellite Top pinout diagram: {output_svg_path}")


# ---------------------------------------------------------------------------
# 2. BOTTOM VIEW (JUMPERS & ADDRESSING) DIAGRAM GENERATOR
# ---------------------------------------------------------------------------

def generate_satellite_bottom_svg(board_image_path: str, output_svg_path: str, css_path: str):
    css_content = ""
    if css_path and os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

    extra_css = """
.tag-jumper .badge-bg, .tag-addr .badge-bg { fill: #4a044e; stroke: #c026d3; }
.tag-jumper .badge-text, .tag-addr .badge-text { fill: #f5d0fe; }
.table-card { fill: #0b1320; stroke: #1e293b; stroke-width: 1.5; rx: 8; transition: stroke 0.2s ease; }
.table-hdr { fill: #f8fafc; font-size: 14.5px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.table-txt { fill: #94a3b8; font-size: 13px; font-family: 'JetBrains Mono', monospace; }
.table-hl { fill: #38bdf8; font-size: 13.5px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.table-default { fill: #4ade80; font-size: 12px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
"""
    css_content += extra_css
    image_href = load_and_crop_image(board_image_path)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS_W} {CANVAS_H}" width="100%" height="100%" class="diagram" id="satellite-bottom-svg">',
        '  <defs>',
        f'    <style type="text/css"><![CDATA[\n{css_content}\n]]></style>',
        '    <filter id="shadow" x="-5%" y="-5%" width="115%" height="115%">',
        '      <feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="#000000" flood-opacity="0.6"/>',
        '    </filter>',
        '  </defs>',
        f'  <rect width="{CANVAS_W}" height="{CANVAS_H}" fill="#0b1320"/>',
        f'  <rect x="20" y="20" width="{CANVAS_W - 40}" height="{CANVAS_H - 40}" class="panel"/>',
        '',
        '  <!-- Header Title -->',
        '  <g transform="translate(50, 68)">',
        '    <text class="title">SunSprout Satellite Configuration &amp; Jumper Diagram (Bottom)</text>',
        '    <text y="26" class="subtitle">Hardware Solder Jumpers • ADS1115 / DS2482 Address Selection • Power &amp; Shield Routing</text>',
        f'    <rect x="{CANVAS_W - 250}" y="-20" width="150" height="30" rx="6" fill="#0f2b48" stroke="#0284c7" stroke-width="1.2"/>',
        f'    <text x="{CANVAS_W - 175}" y="-1" class="header-tag" text-anchor="middle">BOTTOM VIEW</text>',
        '  </g>',
        '',
        '  <!-- Board Image (Bottom View) -->',
        '  <g filter="url(#shadow)">',
        f'    <image href="{image_href}" x="{BOARD_X}" y="{BOARD_Y}" width="{BOARD_PIX_W}" height="{BOARD_PIX_H}" preserveAspectRatio="none"/>',
        '  </g>',
        '',
    ]

    # --- LEFT SIDE: POWER & GROUND ROUTING JUMPERS (JP18 / JP17) & SHIELD (JP13) ---
    # JP18 & JP17: Power Route & Ground Isolation (Placed on Left where JP17/JP18 physically sit on B.Cu)
    jp18_cx, jp18_cy = mm_to_canvas_bottom(22.75, 17.30)
    jp18_label_y = 230
    card18_w = 420
    card18_h = 180
    card18_x = 65
    card18_y = 150

    svg.append('  <g class="callout-group" data-pin="JP17/JP18" data-tags="jumper,pwr,gnd" data-name="JP17/JP18: Power &amp; Ground Route">')
    svg.append(f'    <path d="M {jp18_cx:.1f} {jp18_cy:.1f} L {BOARD_X - 40} {jp18_label_y} L {card18_x + card18_w} {jp18_label_y}" class="leader-line"/>')
    svg.append(f'    <circle cx="{jp18_cx:.1f}" cy="{jp18_cy:.1f}" r="5" class="pin-dot pin-dot-jumper"/>')
    svg.append(f'    <g transform="translate({card18_x}, {card18_y})">')
    svg.append(f'      <rect width="{card18_w}" height="{card18_h}" class="table-card"/>')
    svg.append('      <text x="18" y="28" class="table-hdr">JP17 / JP18: POWER &amp; GROUND ROUTING</text>')
    svg.append('      <text x="18" y="50" class="table-txt">JP18 (Power Source Bridge):</text>')
    svg.append('      <text x="28" y="74" class="table-txt">• Default: RJ45_VCC_1 -> SAT_3V3</text><text x="315" y="74" class="table-default">[DEFAULT]</text>')
    svg.append('      <text x="28" y="96" class="table-txt">• Cut trace for local buck regulation via J7 -> J9</text>')
    svg.append(f'      <line x1="18" y1="110" x2="{card18_w - 18}" y2="110" stroke="#334155" stroke-width="1.2"/>')
    svg.append('      <text x="18" y="132" class="table-txt">JP17 (Ground Isolation Bridge):</text>')
    svg.append('      <text x="28" y="152" class="table-txt">• Default: RJ45_GND_1 -> local GND</text><text x="315" y="152" class="table-default">[DEFAULT]</text>')
    svg.append('      <text x="28" y="170" class="table-txt">• Cut trace to isolate cable ground from sensors</text>')
    svg.append('    </g>')
    svg.append('  </g>')

    # JP13 (Shield Cut)
    jp13_cx, jp13_cy = mm_to_canvas_bottom(24.10, 38.30)
    jp13_label_y = 440
    card13_w = 420
    card13_h = 120
    card13_x = 65
    card13_y = 380

    svg.append('  <g class="callout-group" data-pin="JP13" data-tags="jumper,gnd" data-name="JP13: Shield Ground Isolation">')
    svg.append(f'    <path d="M {jp13_cx:.1f} {jp13_cy:.1f} L {BOARD_X - 40} {jp13_label_y} L {card13_x + card13_w} {jp13_label_y}" class="leader-line"/>')
    svg.append(f'    <circle cx="{jp13_cx:.1f}" cy="{jp13_cy:.1f}" r="5" class="pin-dot pin-dot-jumper"/>')
    svg.append(f'    <g transform="translate({card13_x}, {card13_y})">')
    svg.append(f'      <rect width="{card13_w}" height="{card13_h}" class="table-card"/>')
    svg.append('      <text x="18" y="28" class="table-hdr">JP13: RJ45 CABLE SHIELD GROUND</text>')
    svg.append('      <text x="18" y="52" class="table-txt">Default: Metal shield bridged to RJ45_GND_1.</text>')
    svg.append('      <text x="18" y="76" class="table-txt">Action: Slice center trace to break ground loop</text>')
    svg.append('      <text x="18" y="96" class="table-txt">for single-point earth grounding at Hub.</text>')
    svg.append('    </g>')
    svg.append('  </g>')

    # --- RIGHT SIDE: DS2482 (JP16) & ADS1115 (JP1) ADDRESS SELECTION JUMPERS ---
    # JP16 (DS2482 Address Jumper - at Top Center)
    jp16_cx, jp16_cy = mm_to_canvas_bottom(13.50, 12.40)
    jp16_label_y = 230
    card16_w = 430
    card16_h = 180
    card16_x = BOARD_X + BOARD_PIX_W + 55
    card16_y = 150

    svg.append('  <g class="callout-group" data-pin="JP16" data-tags="addr,jumper,onewire" data-name="JP16: DS2482 Address Select">')
    svg.append(f'    <path d="M {jp16_cx:.1f} {jp16_cy:.1f} L {BOARD_X + BOARD_PIX_W + 35} {jp16_label_y} L {card16_x} {jp16_label_y}" class="leader-line"/>')
    svg.append(f'    <circle cx="{jp16_cx:.1f}" cy="{jp16_cy:.1f}" r="5" class="pin-dot pin-dot-jumper"/>')
    svg.append(f'    <g transform="translate({card16_x}, {card16_y})">')
    svg.append(f'      <rect width="{card16_w}" height="{card16_h}" class="table-card"/>')
    svg.append('      <text x="18" y="28" class="table-hdr">JP16: DS2482 1-WIRE MASTER ADDRESS</text>')
    svg.append('      <text x="18" y="50" class="table-txt">Bit-weighted jumpers [AD1 (+2) / AD0 (+1)]:</text>')
    svg.append(f'      <line x1="18" y1="60" x2="{card16_w - 18}" y2="60" stroke="#334155" stroke-width="1.2"/>')
    svg.append('      <text x="24" y="86" class="table-txt">AD1=GND(0), AD0=GND(0):</text><text x="245" y="86" class="table-hl">0x18</text><text x="305" y="86" class="table-default">[DEF (0x18)]</text>')
    svg.append('      <text x="24" y="110" class="table-txt">AD1=GND(0), AD0=VCC(+1):</text><text x="245" y="110" class="table-hl">0x19</text>')
    svg.append('      <text x="24" y="134" class="table-txt">AD1=VCC(+2), AD0=GND(0):</text><text x="245" y="134" class="table-hl">0x1A</text>')
    svg.append('      <text x="24" y="158" class="table-txt">AD1=VCC(+2), AD0=VCC(+1):</text><text x="245" y="158" class="table-hl">0x1B</text>')
    svg.append('    </g>')
    svg.append('  </g>')

    # JP1 (ADS1115 Address Jumper - Placed on Right where 0x48-0x4B pads physically sit)
    jp1_cx, jp1_cy = mm_to_canvas_bottom(12.00, 19.30)
    jp1_label_y = 440
    card1_w = 430
    card1_h = 180
    card1_x = BOARD_X + BOARD_PIX_W + 55
    card1_y = 380

    svg.append('  <g class="callout-group" data-pin="JP1" data-tags="addr,jumper,analog" data-name="JP1: ADS1115 Address Select">')
    svg.append(f'    <path d="M {jp1_cx:.1f} {jp1_cy:.1f} L {BOARD_X + BOARD_PIX_W + 35} {jp1_label_y} L {card1_x} {jp1_label_y}" class="leader-line"/>')
    svg.append(f'    <circle cx="{jp1_cx:.1f}" cy="{jp1_cy:.1f}" r="5" class="pin-dot pin-dot-jumper"/>')
    svg.append(f'    <g transform="translate({card1_x}, {card1_y})">')
    svg.append(f'      <rect width="{card1_w}" height="{card1_h}" class="table-card"/>')
    svg.append('      <text x="18" y="28" class="table-hdr">JP1: ADS1115 I2C ADDRESS SELECT (4-WAY)</text>')
    svg.append('      <text x="18" y="50" class="table-txt">Pad 1 (ADDR) connects to selectable rail:</text>')
    svg.append(f'      <line x1="18" y1="60" x2="{card1_w - 18}" y2="60" stroke="#334155" stroke-width="1.2"/>')
    svg.append('      <text x="24" y="86" class="table-txt">Pads 1-2 (to GND):</text><text x="220" y="86" class="table-hl">0x48</text><text x="290" y="86" class="table-default">[DEFAULT BRIDGED]</text>')
    svg.append('      <text x="24" y="110" class="table-txt">Pads 1-3 (to SAT_3V3):</text><text x="220" y="110" class="table-hl">0x49</text>')
    svg.append('      <text x="24" y="134" class="table-txt">Pads 1-4 (to SDA_LOCAL):</text><text x="220" y="134" class="table-hl">0x4A</text>')
    svg.append('      <text x="24" y="158" class="table-txt">Pads 1-5 (to SCL_LOCAL):</text><text x="220" y="158" class="table-hl">0x4B</text>')
    svg.append('    </g>')
    svg.append('  </g>')

    # --- FOOTER LEGEND ---
    legend_y = CANVAS_H - 125
    svg.append('  <!-- Legend Panel -->')
    svg.append(f'  <rect x="50" y="{legend_y}" width="{CANVAS_W - 100}" height="100" rx="10" fill="#09101d" stroke="#1e293b" stroke-width="1.2"/>')
    svg.append(f'  <text x="70" y="{legend_y + 22}" class="legend-title">Jumper Function &amp; Addressing Legend (Bottom View)</text>')

    BOT_LEGEND = [
        ("I2C Address Selection Jumpers (JP1, JP16)", "addr"),
        ("Power & Ground Routing Jumpers (JP17, JP18)", "pwr"),
        ("Cable Shield Ground Isolation (JP13)", "gnd"),
        ("Factory Default Configuration [Bridged]", "gpio"),
        ("Custom Address / Isolated [User Configurable]", "strap"),
    ]

    leg_x = 70
    leg_item_y = legend_y + 52
    for name, tag_type in BOT_LEGEND:
        b_svg, w = render_badge(leg_x, leg_item_y, name, tag_type, is_right_aligned=False)
        if leg_x + w > CANVAS_W - 70:
            leg_x = 70
            leg_item_y += 34
            b_svg, w = render_badge(leg_x, leg_item_y, name, tag_type, is_right_aligned=False)
        svg.append(f'  <g class="legend-badge" data-tag="{tag_type}" style="cursor: pointer;">{b_svg}</g>')
        leg_x += (w + 14)

    svg.append('</svg>')

    os.makedirs(os.path.dirname(os.path.abspath(output_svg_path)), exist_ok=True)
    with open(output_svg_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated Satellite Bottom jumper diagram: {output_svg_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate SunSprout Satellite SVG Pinout & Jumper Diagrams")
    parser.add_argument("--top-image", default="website/static/img/satellite-board-top.png")
    parser.add_argument("--bottom-image", default="website/static/img/satellite-board-bottom.png")
    parser.add_argument("--top-output", default="website/static/img/satellite-pinout-top.svg")
    parser.add_argument("--bottom-output", default="website/static/img/satellite-pinout-bottom.svg")
    parser.add_argument("--css", default="tools/pinout/styles.css")
    args = parser.parse_args()

    generate_satellite_top_svg(args.top_image, args.top_output, args.css)
    generate_satellite_bottom_svg(args.bottom_image, args.bottom_output, args.css)


if __name__ == "__main__":
    main()

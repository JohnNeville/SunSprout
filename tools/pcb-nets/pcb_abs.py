"""Absolute pad positions (mm, KiCad board coordinates, y down) for chosen footprints."""
import math
import re
import sys

pcb = sys.argv[1]
want = {}
for a in sys.argv[2:]:
    ref, _, pads = a.partition(":")
    want[ref] = set(pads.split(",")) if pads else None
text = open(pcb, encoding="utf-8").read()
starts = [m.start() for m in re.finditer(r'\n\t\(footprint "', text)]
starts.append(len(text))
for a, b in zip(starts, starts[1:]):
    block = text[a:b]
    ref = re.search(r'\(property "Reference" "([^"]+)"', block)
    if not ref or ref.group(1) not in want:
        continue
    layer = re.search(r'\(layer "([^"]+)"\)', block).group(1)
    at = re.search(r'\n\t\t\(at ([\-\d.]+) ([\-\d.]+)(?: ([\-\d.]+))?\)', block)
    x, y, rot = float(at.group(1)), float(at.group(2)), float(at.group(3) or 0)
    th = math.radians(rot)
    print(f"{ref.group(1)} ({layer}) origin=({x:.2f}, {y:.2f}) rot={rot:g}")
    for pm in re.finditer(r'\(pad "([^"]+)" (\w+) (\w+)(.*?)\n\t\t\)', block, re.S):
        name = pm.group(1)
        if want[ref.group(1)] and name not in want[ref.group(1)]:
            continue
        pos = re.search(r'\(at ([\-\d.]+) ([\-\d.]+)', pm.group(4))
        net = re.search(r'\(net (?:\d+ )?"([^"]*)"\)', pm.group(4))
        px, py = float(pos.group(1)), float(pos.group(2))
        ax = x + px * math.cos(th) + py * math.sin(th)
        ay = y - px * math.sin(th) + py * math.cos(th)
        print(f"   pad {name:>3} -> ({ax:7.2f}, {ay:7.2f})  {net.group(1).split('/')[-1] if net else '-'}")

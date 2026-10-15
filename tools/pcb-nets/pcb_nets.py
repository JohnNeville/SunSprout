"""List the pad nets of chosen footprints from a KiCad .kicad_pcb (read-only text parse)."""
import re
import sys

pcb = sys.argv[1]
refs = sys.argv[2:]
text = open(pcb, encoding="utf-8").read()

# split into top-level footprints by tracking paren depth from each "(footprint "
starts = [m.start() for m in re.finditer(r'\n\t\(footprint "', text)]
starts.append(len(text))
for a, b in zip(starts, starts[1:]):
    block = text[a:b]
    m = re.search(r'\(property "Reference" "([^"]+)"', block)
    if not m or m.group(1) not in refs:
        continue
    lib = re.search(r'\(footprint "([^"]+)"', block).group(1)
    val = re.search(r'\(property "Value" "([^"]*)"', block)
    layer = re.search(r'\(layer "([^"]+)"\)', block).group(1)
    ang = re.search(r'\(at ([\-\d.]+) ([\-\d.]+)(?: ([\-\d.]+))?\)', block)
    print(f"{m.group(1)}: {lib} value={val.group(1) if val else '?'} layer={layer} at=({ang.group(1)}, {ang.group(2)}) rot={ang.group(3) or 0}")
    for pm in re.finditer(r'\(pad "([^"]+)"[^\n]*?\n(?:.*?\n)*?\t\t\t\(net (?:\d+ )?"([^"]*)"\)', block):
        pass
    for pm in re.finditer(r'\(pad "([^"]+)" (\w+) (\w+)(.*?)\n\t\t\)', block, re.S):
        net = re.search(r'\(net (?:\d+ )?"([^"]*)"\)', pm.group(4))
        pos = re.search(r'\(at ([\-\d.]+) ([\-\d.]+)', pm.group(4))
        print(f"   pad {pm.group(1):>3}  net={net.group(1) if net else '-':<28} at=({pos.group(1)}, {pos.group(2)})" if pos else f"   pad {pm.group(1)} net={net.group(1) if net else '-'}")

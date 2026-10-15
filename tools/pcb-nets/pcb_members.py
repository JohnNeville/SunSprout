"""For chosen net names, list every footprint pad on them (read-only parse of a .kicad_pcb)."""
import re
import sys

pcb = sys.argv[1]
wanted = sys.argv[2:]
text = open(pcb, encoding="utf-8").read()
starts = [m.start() for m in re.finditer(r'\n\t\(footprint "', text)]
starts.append(len(text))
members = {n: [] for n in wanted}
for a, b in zip(starts, starts[1:]):
    block = text[a:b]
    ref = re.search(r'\(property "Reference" "([^"]+)"', block)
    val = re.search(r'\(property "Value" "([^"]*)"', block)
    if not ref:
        continue
    for pm in re.finditer(r'\(pad "([^"]+)" (\w+) (\w+)(.*?)\n\t\t\)', block, re.S):
        net = re.search(r'\(net (?:\d+ )?"([^"]*)"\)', pm.group(4))
        if net:
            for n in wanted:
                if net.group(1).endswith(n):
                    members[n].append(f"{ref.group(1)}[{val.group(1) if val else ''}].{pm.group(1)}")
for n, m in members.items():
    print(f"{n}: {', '.join(m) if m else '(none)'}")

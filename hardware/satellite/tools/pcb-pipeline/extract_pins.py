"""Auto-extract pin geometry (dx, dy, angle, name) for a symbol from a raw .kicad_sym
file, across ALL of its unit sub-blocks (handles multi-unit symbols like USBLC6-4SC6
which spreads pins across _0_1/_1_1 etc.). Removes the need to hand-transcribe pin
tables the way the original battery-board kicad_sch_builder.py did.
"""
import re


def _find_balanced(text, start_idx):
    depth = 0
    i = start_idx
    while True:
        c = text[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[start_idx:i + 1]
        i += 1


def extract_top_symbol_block(filepath, symbol_name):
    """Return the full (symbol "Name" ...) block, including nested unit sub-symbols."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    needle = f'(symbol "{symbol_name}"'
    start = text.index(needle)
    return _find_balanced(text, start)


PIN_RE = re.compile(
    r'\(pin\s+\w+\s+\w+\s*'
    r'\(at\s+([\-0-9.]+)\s+([\-0-9.]+)\s+([\-0-9.]+)\)'
    r'.*?\(name\s+"([^"]*)"'
    r'.*?\(number\s+"([^"]*)"',
    re.S,
)


def extract_pins(filepath, symbol_name):
    """Returns {pin_number: (dx, dy, angle, pin_name)} for every pin across all
    unit sub-blocks of the named symbol (Y-up, as authored in the library)."""
    block = extract_top_symbol_block(filepath, symbol_name)
    pins = {}
    for m in PIN_RE.finditer(block):
        x, y, angle, name, number = m.groups()
        pins[number] = (float(x), float(y), int(float(angle)), name)
    return pins


if __name__ == "__main__":
    import sys
    fp, name = sys.argv[1], sys.argv[2]
    pins = extract_pins(fp, name)
    for num, (dx, dy, angle, pname) in sorted(pins.items(), key=lambda kv: kv[0]):
        print(f'"{num}": ({dx}, {dy}, {angle}, "{pname}"),')

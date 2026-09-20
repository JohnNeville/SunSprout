"""Extract a single (symbol "Name" ...) balanced s-expr block from a .kicad_sym file,
and rename it to "Lib:Name" for embedding in a schematic's (lib_symbols) cache."""

def extract(filepath, symbol_name):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    needle = f'(symbol "{symbol_name}"'
    start = text.index(needle)
    # find matching close paren by counting depth from the opening "(" just before "symbol"
    open_idx = start
    depth = 0
    i = open_idx
    while True:
        c = text[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
        i += 1
    return text[open_idx:end]

def extract_renamed(filepath, symbol_name, new_name):
    block = extract(filepath, symbol_name)
    old_header = f'(symbol "{symbol_name}"'
    new_header = f'(symbol "{new_name}"'
    assert block.startswith(old_header)
    return new_header + block[len(old_header):]

if __name__ == "__main__":
    import sys
    fp, name = sys.argv[1], sys.argv[2]
    b = extract(fp, name)
    print(len(b), "chars")
    print(b[:200])
    print("...")
    print(b[-200:])

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kicad_sch_builder as B

B.ROOT_UUID = "11111111-1111-1111-1111-111111111111"
SHEET_UUID = "22222222-2222-2222-2222-222222222222"
DOC_UUID = "33333333-3333-3333-3333-333333333333"

c1_block, C1 = B.symbol_instance("Device:C", "C1", "22uF", 20, 30, 0, SHEET_UUID, footprint="Capacitor_SMD:C_0805_2012Metric")

lib_symbols_block = B.build_lib_symbols_block(["Device:C"])
out = [B.sheet_header("MinTest", DOC_UUID, lib_symbols_block), c1_block, B.sheet_footer()]
with open("_mintest.kicad_sch", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("wrote _mintest.kicad_sch")

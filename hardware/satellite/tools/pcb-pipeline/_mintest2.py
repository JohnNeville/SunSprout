import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kicad_sch_builder as B

DOC_UUID = "44444444-4444-4444-4444-444444444444"
B.ROOT_UUID = DOC_UUID  # standalone: this file IS its own root

c1_block, C1 = B.symbol_instance("Device:C", "C1", "22uF", 20, 30, 0, "", footprint="Capacitor_SMD:C_0805_2012Metric")
# override the instances path to just "/{DOC_UUID}" (no sheet-symbol suffix) - matches
# how a real standalone-root file's own placed symbols are addressed
c1_block = c1_block.replace(
    f'(path "/{DOC_UUID}/"',
    f'(path "/{DOC_UUID}"',
)

lib_symbols_block = B.build_lib_symbols_block(["Device:C"])
out = [B.sheet_header("MinTest2", DOC_UUID, lib_symbols_block), c1_block,
       '\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)',
       B.sheet_footer()]
with open("_mintest2.kicad_sch", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("wrote _mintest2.kicad_sch")

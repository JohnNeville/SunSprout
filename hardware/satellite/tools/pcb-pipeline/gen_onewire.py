"""Generate Sheet 3: 1-Wire Temperature Interface (onewire_v1.kicad_sch)
I2C to 1-Wire master bridge (DS2482S-100+) with configurable address (0x18-0x1B)
and external DS18B20 connector.
Layout:
- Address jumpers JP16 & JP17 grouped together in an address configuration block on left.
- U3 (DS2482S-100+) placed centrally, with local decoupling C5 and pull-up R9 grouped directly with U3.
- J6 probe connector placed on the right.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kicad_sch_builder as B

B.ROOT_UUID = "b8ad246c-0963-44e9-b36f-20d138e559cc"
SHEET_UUID = "7d42e811-9a1b-4f5c-89b2-3e2c918a5411"
DOC_UUID = "f6699c23-35a9-4b08-98c4-5e4fde13fe18"

LIB_IDS_USED = [
    "project:DS2482S-100",
    "Connector_Generic:Conn_01x03",
    "Jumper:SolderJumper_3_Bridged12",
    "Device:C",
    "Device:R",
    "power:GND",
]

parts, wires, junctions, labels, pwr = [], [], [], [], []


def stub_label(pin_xy, net, dx=None, dy=None, shape="input"):
    x, y = pin_xy
    if dx is None and dy is None:
        dx = getattr(pin_xy, "dx", 10.16)
        dy = getattr(pin_xy, "dy", 0)
    elif dx is None:
        dx = 0
    elif dy is None:
        dy = 0
    dx = B.snap(dx)
    dy = B.snap(dy)
    ex, ey = B.snap(x + dx), B.snap(y + dy)
    wires.append(B.wire([(x, y), (ex, ey)]))
    if dx < 0:
        angle, justify = 180, "right"
    elif dx > 0:
        angle, justify = 0, "left"
    elif dy < 0:
        angle, justify = 90, "left"
    else:  # dy > 0
        angle, justify = 270, "right"
    labels.append(B.global_label(net, shape, ex, ey, angle, justify))


# ---------------------------------------------------------------------------
# Address Selection Jumper Group (grouped together at x=50.8)
# JP16 (AD0) and JP17 (AD1): 3-pad jumpers (Pin 1=GND, Pin 2=ADx, Pin 3=SAT_3V3; default 1-2 bridged -> 0x18)
jp16_block, JP16 = B.symbol_instance(
    "Jumper:SolderJumper_3_Bridged12", "JP16", "SolderJumper_3_Bridged12", 50.8, 63.5, 0, SHEET_UUID,
    footprint="Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm",
    usage="Solder jumper for DS2482S-100 AD0 address bit (1-2 bridged to GND for 0, cut & bridge 2-3 to SAT_3V3 for 1; default 0)",
    lcsc="", ft_pos="", ft_rot="", hide_value=True
)
jp17_block, JP17 = B.symbol_instance(
    "Jumper:SolderJumper_3_Bridged12", "JP17", "SolderJumper_3_Bridged12", 50.8, 95.25, 0, SHEET_UUID,
    footprint="Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm",
    usage="Solder jumper for DS2482S-100 AD1 address bit (1-2 bridged to GND for 0, cut & bridge 2-3 to SAT_3V3 for 1; default 0)",
    lcsc="", ft_pos="", ft_rot="", hide_value=True
)
parts += [jp16_block, jp17_block]

# ---------------------------------------------------------------------------
# U3: DS2482S-100+ 1-Wire Bridge & Local Passives Group (placed centrally at x=127.0)
u3_block, U3 = B.symbol_instance(
    "project:DS2482S-100", "U3", "DS2482S-100+", 127.0, 76.2, 0, SHEET_UUID,
    footprint="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
    usage="I2C to 1-Wire bridge with active pull-up and 4 selectable I2C addresses (0x18-0x1B) interfacing external DS18B20 temperature probes",
    lcsc="C143306", ft_pos="", ft_rot=""
)
parts.append(u3_block)

# C5: Decoupling capacitor grouped directly below U3
c5_block, C5 = B.symbol_instance(
    "Device:C", "C5", "100nF", 127.0, 120.65, 0, SHEET_UUID,
    footprint="Capacitor_SMD:C_0603_1608Metric",
    usage="High-frequency local bypass decoupling for DS2482S-100 VCC supply rail",
    lcsc="C14663", ft_pos="", ft_rot=""
)
parts.append(c5_block)

# R9: Optional 1-Wire passive pull-up resistor grouped adjacent to U3/J6
r9_block, R9 = B.symbol_instance(
    "Device:R", "R9", "4.7k", 165.1, 120.65, 0, SHEET_UUID,
    footprint="Resistor_SMD:R_0603_1608Metric",
    usage="Optional 1-Wire passive pull-up resistor to SAT_3V3 (DNP by default; populate 4.7k 0603 if external passive pull-up is needed for long cable runs)",
    lcsc="C23162", ft_pos="", ft_rot="", dnp=True
)
parts.append(r9_block)

# ---------------------------------------------------------------------------
# J6: 1-Wire Temp Probe Connector (JST PA 3-pin)
j6_block, J6 = B.symbol_instance(
    "Connector_Generic:Conn_01x03", "J6", "Conn_01x03", 203.2, 76.2, 0, SHEET_UUID,
    footprint="Connector_JST:JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical",
    usage="JST PA 3-pin connector for daisy-chained external DS18B20 1-Wire waterproof temperature probes",
    lcsc="C265095", ft_pos="", ft_rot=""
)
parts.append(j6_block)

# ---------------------------------------------------------------------------
# Wiring
# Power connections
for pin_xy in [U3["1"], C5["1"], R9["1"], J6["1"], JP16["3"], JP17["3"]]:
    stub_label(pin_xy, "SAT_3V3")

for pin_xy in [U3["3"], C5["2"], J6["2"], JP16["1"], JP17["1"]]:
    stub_label(pin_xy, "GND")

# I2C connections
stub_label(U3["5"], "SDA_LOCAL")
stub_label(U3["4"], "SCL_LOCAL")

# Address selection connections
stub_label(U3["7"], "AD0_SEL")
stub_label(JP16["2"], "AD0_SEL")

stub_label(U3["8"], "AD1_SEL")
stub_label(JP17["2"], "AD1_SEL")

# 1-Wire bus
stub_label(U3["2"], "ONEWIRE_DQ")
stub_label(J6["3"], "ONEWIRE_DQ")
stub_label(R9["2"], "ONEWIRE_DQ")

# U3.PCTLZ (pin 6) active-low strong pull-up control is not used with internal pull-up
ncs = [B.no_connect(*U3["6"])]

lib_symbols_block = B.build_lib_symbols_block(LIB_IDS_USED)
out = [B.sheet_header("1-Wire Temperature Interface", DOC_UUID, lib_symbols_block)]
out += parts + wires + junctions + labels + pwr + ncs
out.append(B.sheet_footer())

sch_text = "\n".join(out)
out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "onewire.kicad_sch")
with open(out_file, "w", encoding="utf-8") as f:
    f.write(sch_text)
print(f"wrote {out_file}")

sheet_file = os.path.join(B.PROJECT_ROOT, "sheets", "onewire_v1.kicad_sch")
if os.path.exists(os.path.dirname(sheet_file)):
    with open(sheet_file, "w", encoding="utf-8") as f:
        f.write(sch_text)
    print(f"wrote {sheet_file}")

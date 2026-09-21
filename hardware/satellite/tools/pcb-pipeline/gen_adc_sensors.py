"""Generate Sheet 2: ADC Soil Moisture Sensors (adc_sensors_v1.kicad_sch)
Precision analog acquisition for 4x capacitive soil moisture sensors via ADS1115.
Layout:
- Connectors J2-J5 in a clean input column on the left.
- U2 (ADS1115) placed centrally, with local decoupling C4 directly grouped with U2.
- JP1: Single unified 4-way address selector solder jumper block (project:SolderJumper_4_Bridged12).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kicad_sch_builder as B

B.ROOT_UUID = "b8ad246c-0963-44e9-b36f-20d138e559cc"
SHEET_UUID = "5c3db235-7c84-4784-89d3-95a10e8212da"
DOC_UUID = "e5588b12-2498-4e97-87b3-4d3fcd02ed07"

LIB_IDS_USED = [
    "Analog_ADC:ADS1115IDGS",
    "Connector_Generic:Conn_01x03",
    "project:SolderJumper_4_Bridged12",
    "Device:C",
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
# J2-J5: Moisture sensor connectors (JST PH 3-pin)
# Left column at x=38.1 with 25.4mm vertical pitch
j2_block, J2 = B.symbol_instance(
    "Connector_Generic:Conn_01x03", "J2", "Conn_01x03", 38.1, 38.1, 0, SHEET_UUID,
    footprint="Connector_JST:JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical",
    usage="DFRobot Gravity PH2.0-3P connector for analog capacitive soil moisture sensor 1 (Channel A0)",
    lcsc="C131339", ft_pos="", ft_rot=""
)
j3_block, J3 = B.symbol_instance(
    "Connector_Generic:Conn_01x03", "J3", "Conn_01x03", 38.1, 63.5, 0, SHEET_UUID,
    footprint="Connector_JST:JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical",
    usage="DFRobot Gravity PH2.0-3P connector for analog capacitive soil moisture sensor 2 (Channel A1)",
    lcsc="C131339", ft_pos="", ft_rot=""
)
j4_block, J4 = B.symbol_instance(
    "Connector_Generic:Conn_01x03", "J4", "Conn_01x03", 38.1, 88.9, 0, SHEET_UUID,
    footprint="Connector_JST:JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical",
    usage="DFRobot Gravity PH2.0-3P connector for analog capacitive soil moisture sensor 3 (Channel A2)",
    lcsc="C131339", ft_pos="", ft_rot=""
)
j5_block, J5 = B.symbol_instance(
    "Connector_Generic:Conn_01x03", "J5", "Conn_01x03", 38.1, 114.3, 0, SHEET_UUID,
    footprint="Connector_JST:JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical",
    usage="DFRobot Gravity PH2.0-3P connector for analog capacitive soil moisture sensor 4 (Channel A3)",
    lcsc="C131339", ft_pos="", ft_rot=""
)
parts += [j2_block, j3_block, j4_block, j5_block]

# ---------------------------------------------------------------------------
# U2: ADS1115 ADC & Local Passives Group (placed centrally at x=101.6)
u2_block, U2 = B.symbol_instance(
    "Analog_ADC:ADS1115IDGS", "U2", "ADS1115IDGS", 101.6, 76.2, 0, SHEET_UUID,
    footprint="Package_SO:TSSOP-10_3x3mm_P0.5mm",
    usage="16-bit 4-channel precision delta-sigma ADC measuring analog soil moisture sensor voltages over I2C",
    lcsc="C37593", ft_pos="", ft_rot=""
)
parts.append(u2_block)

# C4: Local bypass decoupling capacitor grouped directly below U2
c4_block, C4 = B.symbol_instance(
    "Device:C", "C4", "100nF", 101.6, 127.0, 0, SHEET_UUID,
    footprint="Capacitor_SMD:C_0603_1608Metric",
    usage="High-frequency local bypass decoupling for ADS1115 VDD supply rail",
    lcsc="C14663", ft_pos="", ft_rot=""
)
parts.append(c4_block)

# ---------------------------------------------------------------------------
# JP1: 4-Way Address Selection Solder Jumper Block (project:SolderJumper_4_Bridged12)
# Pin 1 = ADDR_SEL (left)
# Pin 2 = 0x48 / GND (bridged by default)
# Pin 3 = 0x49 / SAT_3V3 (open)
# Pin 4 = 0x4B / SCL_LOCAL (open)
# Pin 5 = 0x4A / SDA_LOCAL (open)
jp1_block, JP1 = B.symbol_instance(
    "project:SolderJumper_4_Bridged12", "JP1", "SolderJumper_4_Bridged12", 152.4, 76.2, 0, SHEET_UUID,
    footprint="project:SolderJumper-4_P1.3mm_Bridged12_RoundedPad1.0x1.5mm",
    usage="4-way address selector solder jumper block (Pin 1: ADDR; Pin 2: GND for 0x48 default bridged; Pin 3: SAT_3V3 for 0x49; Pin 4: SCL for 0x4B; Pin 5: SDA for 0x4A)",
    lcsc="", ft_pos="", ft_rot="", hide_value=True
)
parts.append(jp1_block)

# ---------------------------------------------------------------------------
# Wiring
# Power connections
for pin_xy in [U2["8"], C4["1"], J2["2"], J3["2"], J4["2"], J5["2"], JP1["3"]]:
    stub_label(pin_xy, "SAT_3V3")

for pin_xy in [U2["3"], C4["2"], J2["1"], J3["1"], J4["1"], J5["1"], JP1["2"]]:
    stub_label(pin_xy, "GND")

# I2C connections
stub_label(U2["10"], "SCL_LOCAL")
stub_label(JP1["4"], "SCL_LOCAL")

stub_label(U2["9"], "SDA_LOCAL")
stub_label(JP1["5"], "SDA_LOCAL")

# Address line connections
stub_label(U2["1"], "ADDR_SEL")
stub_label(JP1["1"], "ADDR_SEL")

# Analog inputs from connectors to ADC
stub_label(U2["4"], "MOIST1")
stub_label(J2["3"], "MOIST1")

stub_label(U2["5"], "MOIST2")
stub_label(J3["3"], "MOIST2")

stub_label(U2["6"], "MOIST3")
stub_label(J4["3"], "MOIST3")

stub_label(U2["7"], "MOIST4")
stub_label(J5["3"], "MOIST4")

# U2.ALERT (pin 2) intentionally left NC per design
ncs = [B.no_connect(*U2["2"])]

lib_symbols_block = B.build_lib_symbols_block(LIB_IDS_USED)
out = [B.sheet_header("ADC Soil Moisture Sensors", DOC_UUID, lib_symbols_block)]
out += parts + wires + junctions + labels + pwr + ncs
out.append(B.sheet_footer())

sch_text = "\n".join(out)
out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adc_sensors.kicad_sch")
with open(out_file, "w", encoding="utf-8") as f:
    f.write(sch_text)
print(f"wrote {out_file}")

sheet_file = os.path.join(B.PROJECT_ROOT, "sheets", "adc_sensors_v1.kicad_sch")
if os.path.exists(os.path.dirname(sheet_file)):
    with open(sheet_file, "w", encoding="utf-8") as f:
        f.write(sch_text)
    print(f"wrote {sheet_file}")

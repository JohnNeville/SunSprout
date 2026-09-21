import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kicad_sch_builder as B

B.ROOT_UUID = "b8ad246c-0963-44e9-b36f-20d138e559cc"
SHEET_UUID = "5c3db235-7c84-4784-89d3-95a10e8212da"
DOC_UUID = "e5588b12-2498-4e97-87b3-4d3fcd02ed07"

LIB_IDS_USED = [
    "Analog_ADC:ADS1115IDGS", "Interface_Expansion:DS2484R",
    "Connector_Generic:Conn_01x03", "Jumper:SolderJumper_2_Bridged",
    "Jumper:SolderJumper_2_Open", "Device:C", "Device:R", "power:GND",
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
# J2-J5: moisture sensor connectors (JST PH 3-pin)
# Placed on left at x=38.1 with generous 25.4mm vertical spacing
j2_block, J2 = B.symbol_instance(
    "Connector_Generic:Conn_01x03", "J2", "Conn_01x03", 38.1, 25.4, 0, SHEET_UUID,
    footprint="Connector_JST:JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical",
    usage="DFRobot Gravity PH2.0-3P connector for analog capacitive soil moisture sensor 1 (Channel A0)",
    lcsc="C131339", ft_pos="", ft_rot=""
)
j3_block, J3 = B.symbol_instance(
    "Connector_Generic:Conn_01x03", "J3", "Conn_01x03", 38.1, 50.8, 0, SHEET_UUID,
    footprint="Connector_JST:JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical",
    usage="DFRobot Gravity PH2.0-3P connector for analog capacitive soil moisture sensor 2 (Channel A1)",
    lcsc="C131339", ft_pos="", ft_rot=""
)
j4_block, J4 = B.symbol_instance(
    "Connector_Generic:Conn_01x03", "J4", "Conn_01x03", 38.1, 76.2, 0, SHEET_UUID,
    footprint="Connector_JST:JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical",
    usage="DFRobot Gravity PH2.0-3P connector for analog capacitive soil moisture sensor 3 (Channel A2)",
    lcsc="C131339", ft_pos="", ft_rot=""
)
j5_block, J5 = B.symbol_instance(
    "Connector_Generic:Conn_01x03", "J5", "Conn_01x03", 38.1, 101.6, 0, SHEET_UUID,
    footprint="Connector_JST:JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical",
    usage="DFRobot Gravity PH2.0-3P connector for analog capacitive soil moisture sensor 4 (Channel A3)",
    lcsc="C131339", ft_pos="", ft_rot=""
)
parts += [j2_block, j3_block, j4_block, j5_block]

# JP1-4: ADS1115 address-select solder jumpers (spaced generously along top at y=25.4, 50.8mm apart to avoid stub collisions)
jp1_block, JP1 = B.symbol_instance(
    "Jumper:SolderJumper_2_Bridged", "JP1", "SolderJumper_2_Bridged", 76.2, 25.4, 0, SHEET_UUID,
    footprint="Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm",
    usage="Solder jumper tying ADS1115 ADDR pin to GND (sets I2C address 0x48, default closed)",
    lcsc="", ft_pos="", ft_rot=""
)
jp2_block, JP2 = B.symbol_instance(
    "Jumper:SolderJumper_2_Open", "JP2", "SolderJumper_2_Open", 127.0, 25.4, 0, SHEET_UUID,
    footprint="Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm",
    usage="Solder jumper tying ADS1115 ADDR pin to SAT_3V3 (sets I2C address 0x49)",
    lcsc="", ft_pos="", ft_rot=""
)
jp3_block, JP3 = B.symbol_instance(
    "Jumper:SolderJumper_2_Open", "JP3", "SolderJumper_2_Open", 177.8, 25.4, 0, SHEET_UUID,
    footprint="Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm",
    usage="Solder jumper tying ADS1115 ADDR pin to SDA_LOCAL (sets I2C address 0x4A)",
    lcsc="", ft_pos="", ft_rot=""
)
jp4_block, JP4 = B.symbol_instance(
    "Jumper:SolderJumper_2_Open", "JP4", "SolderJumper_2_Open", 228.6, 25.4, 0, SHEET_UUID,
    footprint="Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm",
    usage="Solder jumper tying ADS1115 ADDR pin to SCL_LOCAL (sets I2C address 0x4B)",
    lcsc="", ft_pos="", ft_rot=""
)
parts += [jp1_block, jp2_block, jp3_block, jp4_block]

# U2: ADS1115 ADC (placed at x=88.9, y=88.9)
u2_block, U2 = B.symbol_instance(
    "Analog_ADC:ADS1115IDGS", "U2", "ADS1115IDGS", 88.9, 88.9, 0, SHEET_UUID,
    footprint="Package_SO:TSSOP-10_3x3mm_P0.5mm",
    usage="16-bit 4-channel precision delta-sigma ADC measuring analog soil moisture sensor voltages over I2C",
    lcsc="C37593", ft_pos="", ft_rot=""
)
parts.append(u2_block)

# U3: DS2484R 1-Wire bridge (placed at x=165.1, y=88.9, spaced 76.2mm from U2)
u3_block, U3 = B.symbol_instance(
    "Interface_Expansion:DS2484R", "U3", "DS2484R", 165.1, 88.9, 0, SHEET_UUID,
    footprint="Package_TO_SOT_SMD:SOT-23-6",
    usage="I2C to 1-Wire bridge with internal pull-up and slew rate control interfacing external DS18B20 temperature sensors",
    lcsc="C124886", ft_pos="", ft_rot=""
)
parts.append(u3_block)

# J6: 1-Wire temp probe connector (placed on far right at x=241.3, y=88.9)
j6_block, J6 = B.symbol_instance(
    "Connector_Generic:Conn_01x03", "J6", "Conn_01x03", 241.3, 88.9, 0, SHEET_UUID,
    footprint="Connector_JST:JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical",
    usage="JST PA 3-pin connector for daisy-chained external DS18B20 1-Wire waterproof temperature probes",
    lcsc="C131339", ft_pos="", ft_rot=""
)
parts.append(j6_block)

# Decoupling caps (placed cleanly below ICs at y=152.4)
c4_block, C4 = B.symbol_instance(
    "Device:C", "C4", "100nF", 88.9, 152.4, 0, SHEET_UUID,
    footprint="Capacitor_SMD:C_0603_1608Metric",
    usage="High-frequency local bypass decoupling for ADS1115 VDD supply rail",
    lcsc="C14663", ft_pos="", ft_rot=""
)
c5_block, C5 = B.symbol_instance(
    "Device:C", "C5", "100nF", 165.1, 152.4, 0, SHEET_UUID,
    footprint="Capacitor_SMD:C_0603_1608Metric",
    usage="High-frequency local bypass decoupling for DS2484R VDD/VCC supply rails",
    lcsc="C14663", ft_pos="", ft_rot=""
)

# R9: Optional 1-Wire passive pull-up resistor (DNP by default; solder 4.7k 0603 if needed)
r9_block, R9 = B.symbol_instance(
    "Device:R", "R9", "4.7k", 203.2, 152.4, 0, SHEET_UUID,
    footprint="Resistor_SMD:R_0603_1608Metric",
    usage="Optional 1-Wire passive pull-up resistor to SAT_3V3 (DNP by default; populate 4.7k 0603 if external passive pull-up is needed for long cable runs)",
    lcsc="C23162", ft_pos="", ft_rot="", dnp=True
)
parts += [c4_block, c5_block, r9_block]

# ---------------------------------------------------------------------------
# Wiring - net-connections.md, "Sheet 2 - Sensors"

for pin_xy in [U2["8"], U3["6"], U3["1"], C4["1"], C5["1"], R9["1"], J2["2"], J3["2"], J4["2"], J5["2"], J6["1"], JP2["2"]]:
    stub_label(pin_xy, "SAT_3V3")

for pin_xy in [U2["3"], U3["4"], C4["2"], C5["2"], J2["1"], J3["1"], J4["1"], J5["1"], J6["2"], JP1["2"]]:
    stub_label(pin_xy, "GND")

for pin_xy in [U2["9"], U3["2"], JP3["2"]]:
    stub_label(pin_xy, "SDA_LOCAL")
for pin_xy in [U2["10"], U3["3"], JP4["2"]]:
    stub_label(pin_xy, "SCL_LOCAL")

for pin_xy in [U2["1"], JP1["1"], JP2["1"], JP3["1"], JP4["1"]]:
    stub_label(pin_xy, "ADDR_SEL")

stub_label(U3["5"], "ONEWIRE_DQ")
stub_label(J6["3"], "ONEWIRE_DQ")
stub_label(R9["2"], "ONEWIRE_DQ")

stub_label(U2["4"], "MOIST1")
stub_label(J2["3"], "MOIST1")
stub_label(U2["5"], "MOIST2")
stub_label(J3["3"], "MOIST2")
stub_label(U2["6"], "MOIST3")
stub_label(J4["3"], "MOIST3")
stub_label(U2["7"], "MOIST4")
stub_label(J5["3"], "MOIST4")

# U2.ALERT (pin2) intentionally left NC per design
ncs = [B.no_connect(*U2["2"])]

lib_symbols_block = B.build_lib_symbols_block(LIB_IDS_USED)
out = [B.sheet_header("Sensors", DOC_UUID, lib_symbols_block)]
out += parts + wires + junctions + labels + pwr + ncs
out.append(B.sheet_footer())

sch_text = "\n".join(out)
out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sensors.kicad_sch")
with open(out_file, "w", encoding="utf-8") as f:
    f.write(sch_text)
print(f"wrote {out_file}")

sheet_file = os.path.join(B.PROJECT_ROOT, "sheets", "sensors_v1.kicad_sch")
if os.path.exists(os.path.dirname(sheet_file)):
    with open(sheet_file, "w", encoding="utf-8") as f:
        f.write(sch_text)
    print(f"wrote {sheet_file}")

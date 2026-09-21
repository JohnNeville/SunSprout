"""Generate Sheet 1: Differential I2C Endpoint (i2c_endpoint_v1.kicad_sch)
Differential transceiver (PCA9615), ESD protection (USBLC6-4SC6), RJ45 connector,
plain differential termination network (no jumpers), I2C pull-ups, and power/ground configuration.

Layout:
- Zone 1 (Left): U1 (PCA9615) + local decoupling C2 & C3 placed directly adjacent to U1;
  I2C pull-up group (JP11 single-cut dual pull-up jumper + R1/R2) placed directly above U1.
- Zone 2 (Center): Direct Differential Termination Ladders (R3-R5 for DSCL, R6-R8 for DSDA).
- Zone 3 (Center-Right): U4 (USBLC6-4SC6) ESD protection + local bypass C6 directly adjacent.
- Zone 4 (Right): J1 (RJ45 jack) + Power Distribution & Grounding Block:
  C1 (22uF bulk cap) + JP14 (power source select) + JP15 (GND_2 bridge) +
  JP13 (shield GND) + J7 (aux 2.54mm pin header).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kicad_sch_builder as B

B.ROOT_UUID = "b8ad246c-0963-44e9-b36f-20d138e559cc"
SHEET_UUID = "39f0f462-a3ef-4464-92a2-10c435d9a480"
DOC_UUID = "6fc92d06-5711-4053-8403-e6d0a28471f4"

LIB_IDS_USED = [
    "project:RJHSE5380_QwiicBusCompatible", "project:PCA9615DPZ",
    "project:SolderJumper_3_DualPullUp_Bridged",
    "Power_Protection:USBLC6-4SC6", "Device:R", "Device:C",
    "Jumper:SolderJumper_2_Bridged", "Jumper:SolderJumper_3_Bridged12",
    "Connector_Generic:Conn_01x04", "power:GND",
]

parts, wires, junctions, labels, ncs = [], [], [], [], []


def stub_label(pin_xy, net, dx=None, dy=None, shape="input"):
    """Short fixed-offset stub wire from a pin to a global_label carrying `net`."""
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


def direct_wire(pin_a, pin_b):
    wires.append(B.wire([pin_a, pin_b]))


# ===========================================================================
# ZONE 1: U1 (PCA9615) Differential I2C Transceiver & Local Passives Group
# ===========================================================================

# Dual I2C Pull-Up Cut Jumper JP11 (placed at x=50.8, y=30.48: Pin 1 top, Pins 2 & 3 bottom)
jp11_block, JP11 = B.symbol_instance(
    "project:SolderJumper_3_DualPullUp_Bridged", "JP11", "SolderJumper_3_DualPullUp_Bridged", 50.8, 30.48, 0, SHEET_UUID,
    footprint="project:SolderJumper-3_P1.3mm_DualPullUp_SingleCut_RoundedPad1.0x1.5mm",
    usage="Dual I2C pull-up single-cut solder jumper connecting SAT_3V3 to R1 (SCL) and R2 (SDA); single razor cut severs both pull-ups while isolating lines",
    lcsc="", ft_pos="", ft_rot="", hide_value=True
)
parts.append(jp11_block)

# I2C pull-ups R1, R2 (placed directly below JP11 pins 2 and 3 at y=50.8)
r1_block, R1 = B.symbol_instance(
    "Device:R", "R1", "4.7k", 48.26, 50.8, 0, SHEET_UUID,
    footprint="Resistor_SMD:R_0603_1608Metric",
    usage="Local I2C bus pull-up resistor for SCL_LOCAL line to SAT_3V3",
    lcsc="C23162", ft_pos="", ft_rot=""
)
r2_block, R2 = B.symbol_instance(
    "Device:R", "R2", "4.7k", 53.34, 50.8, 0, SHEET_UUID,
    footprint="Resistor_SMD:R_0603_1608Metric",
    usage="Local I2C bus pull-up resistor for SDA_LOCAL line to SAT_3V3",
    lcsc="C23162", ft_pos="", ft_rot=""
)
parts += [r1_block, r2_block]

# U1: PCA9615DPZ differential I2C buffer (placed at x=38.1, y=101.6)
u1_block, U1 = B.symbol_instance(
    "project:PCA9615DPZ", "U1", "PCA9615DPZ", 38.1, 101.6, 0, SHEET_UUID,
    footprint="Snapeda:TSSOP10_SOT552-1_NXP-L",
    usage="Differential I2C buffer/transceiver converting long-distance differential I2C (DSCL/DSDA) to local single-ended I2C (SCL_LOCAL/SDA_LOCAL)",
    lcsc="C3824272", ft_pos="", ft_rot=""
)
parts.append(u1_block)

# C2: Local decoupling for PCA9615 VDD(A) core/I2C supply (placed directly under U1 pin 1 at x=38.1, y=139.7)
c2_block, C2 = B.symbol_instance(
    "Device:C", "C2", "100nF", 38.1, 139.7, 0, SHEET_UUID,
    footprint="Capacitor_SMD:C_0603_1608Metric",
    usage="High-frequency local decoupling for PCA9615 VDD(A) core/I2C-side supply",
    lcsc="C14663", ft_pos="", ft_rot=""
)
# C3: Local decoupling for PCA9615 VDD(B) differential supply (placed directly under U1 pin 10 at x=88.9, y=139.7)
c3_block, C3 = B.symbol_instance(
    "Device:C", "C3", "100nF", 88.9, 139.7, 0, SHEET_UUID,
    footprint="Capacitor_SMD:C_0603_1608Metric",
    usage="High-frequency local decoupling for PCA9615 VDD(B) differential-side supply",
    lcsc="C14663", ft_pos="", ft_rot=""
)
parts += [c2_block, c3_block]


# ===========================================================================
# ZONE 2: Differential Termination Network (Direct Resistor Ladders)
# ===========================================================================

# DSCL termination ladder (vertical ladder at x=127.0)
r3_block, R3 = B.symbol_instance(
    "Device:R", "R3", "390", 127.0, 25.4, 0, SHEET_UUID,
    footprint="Resistor_SMD:R_0603_1608Metric",
    usage="Upper bias pull-up resistor for DSCL_P differential line to SAT_3V3",
    lcsc="C23151", ft_pos="", ft_rot=""
)
r4_block, R4 = B.symbol_instance(
    "Device:R", "R4", "100", 127.0, 50.8, 0, SHEET_UUID,
    footprint="Resistor_SMD:R_0603_1608Metric",
    usage="Differential termination resistor (100-ohm line matching) across DSCL_P and DSCL_N",
    lcsc="C22775", ft_pos="", ft_rot=""
)
r5_block, R5 = B.symbol_instance(
    "Device:R", "R5", "390", 127.0, 76.2, 0, SHEET_UUID,
    footprint="Resistor_SMD:R_0603_1608Metric",
    usage="Lower bias pull-down resistor for DSCL_N differential line to GND",
    lcsc="C23151", ft_pos="", ft_rot=""
)
parts += [r3_block, r4_block, r5_block]

# DSDA termination ladder (vertical ladder at x=177.8)
r6_block, R6 = B.symbol_instance(
    "Device:R", "R6", "390", 177.8, 25.4, 0, SHEET_UUID,
    footprint="Resistor_SMD:R_0603_1608Metric",
    usage="Upper bias pull-up resistor for DSDA_P differential line to SAT_3V3",
    lcsc="C23151", ft_pos="", ft_rot=""
)
r7_block, R7 = B.symbol_instance(
    "Device:R", "R7", "100", 177.8, 50.8, 0, SHEET_UUID,
    footprint="Resistor_SMD:R_0603_1608Metric",
    usage="Differential termination resistor (100-ohm line matching) across DSDA_P and DSDA_N",
    lcsc="C22775", ft_pos="", ft_rot=""
)
r8_block, R8 = B.symbol_instance(
    "Device:R", "R8", "390", 177.8, 76.2, 0, SHEET_UUID,
    footprint="Resistor_SMD:R_0603_1608Metric",
    usage="Lower bias pull-down resistor for DSDA_N differential line to GND",
    lcsc="C23151", ft_pos="", ft_rot=""
)
parts += [r6_block, r7_block, r8_block]


# ===========================================================================
# ZONE 3: U4 (USBLC6-4SC6) ESD Protection & Decoupling Group
# ===========================================================================

u4_block, U4 = B.symbol_instance(
    "Power_Protection:USBLC6-4SC6", "U4", "USBLC6-4SC6", 139.7, 114.3, 0, SHEET_UUID,
    footprint="Package_TO_SOT_SMD:SOT-23-6",
    usage="Low-capacitance ESD protection diode array clamping the 4 differential I2C lines to SAT_3V3 and GND at the RJ45 cable entry",
    lcsc="C5180279", ft_pos="", ft_rot=""
)
parts.append(u4_block)

# C6: High-frequency local decoupling for USBLC6-4SC6 VBUS clamp reference rail (grouped right beside U4 at x=165.1)
c6_block, C6 = B.symbol_instance(
    "Device:C", "C6", "100nF", 165.1, 114.3, 0, SHEET_UUID,
    footprint="Capacitor_SMD:C_0603_1608Metric",
    usage="High-frequency local decoupling for USBLC6-4SC6 VBUS clamp reference rail",
    lcsc="C14663", ft_pos="", ft_rot=""
)
parts.append(c6_block)


# ===========================================================================
# ZONE 4: J1 (RJ45), Power Entry Bulk Cap, & Ground Configuration Group
# ===========================================================================

# J1: RJHSE5380 8P8C jack
j1_block, J1 = B.symbol_instance(
    "project:RJHSE5380_QwiicBusCompatible", "J1", "RJHSE5380_QwiicBusCompatible", 254.0, 101.6, 0, SHEET_UUID,
    footprint="Snapeda:AMPHENOL_RJHSE5380",
    usage="8P8C / RJ45 differential I2C cable connector (QwiicBus pinout), bringing in power, ground, and DSCL/DSDA differential pairs from SunSproutHub",
    lcsc="C464586", ft_pos="", ft_rot=""
)
parts.append(j1_block)

# C1: Bulk reservoir capacitor at power-in point (grouped adjacent to JP14 at x=165.1, y=152.4)
c1_block, C1 = B.symbol_instance(
    "Device:C", "C1", "22uF", 165.1, 152.4, 0, SHEET_UUID,
    footprint="Capacitor_SMD:C_0805_2012Metric",
    usage="Bulk reservoir capacitor at power-in point (VCC_1/SAT_3V3), absorbing cable IR drop and transient load dips",
    lcsc="C45783", ft_pos="", ft_rot=""
)
parts.append(c1_block)

# Configuration Jumpers Block:
# JP14: Power Source Selection Jumper (VCC_1 vs VCC_2 to SAT_3V3)
jp14_block, JP14 = B.symbol_instance(
    "Jumper:SolderJumper_3_Bridged12", "JP14", "SolderJumper_3_Bridged12", 203.2, 152.4, 0, SHEET_UUID,
    footprint="Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm",
    usage="3-way solder jumper selecting power source for SAT_3V3 rail (1-2: VCC_1 default, 2-3: VCC_2 auxiliary power)",
    lcsc="", ft_pos="", ft_rot="", hide_value=True
)
parts.append(jp14_block)

# JP15: GND_2 to GND Bridged Jumper
jp15_block, JP15 = B.symbol_instance(
    "Jumper:SolderJumper_2_Bridged", "JP15", "SolderJumper_2_Bridged", 203.2, 172.72, 0, SHEET_UUID,
    footprint="Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm",
    usage="Cuttable trace jumper bridging cable GND_2 (GRN_N) to system GND (default bridged; cut if using isolated secondary supply)",
    lcsc="", ft_pos="", ft_rot="", hide_value=True
)
parts.append(jp15_block)

# JP13: Shield Ground Isolation Jumper (between J1.SHIELD and GND)
jp13_block, JP13 = B.symbol_instance(
    "Jumper:SolderJumper_2_Bridged", "JP13", "SolderJumper_2_Bridged", 203.2, 190.5, 0, SHEET_UUID,
    footprint="Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm",
    usage="Cuttable trace jumper connecting RJ45 cable shield to system ground; cut to break ground loops in outdoor field installations",
    lcsc="", ft_pos="", ft_rot="", hide_value=True
)
parts.append(jp13_block)

# J7: 1x04 2.54mm Pin Header for VCC_2 / GND_2 auxiliary expansion
# Pin 1: VCC_2, Pin 2: GND_2, Pin 3: GND_2, Pin 4: GND_2
j7_block, J7 = B.symbol_instance(
    "Connector_Generic:Conn_01x04", "J7", "Conn_01x04", 254.0, 165.1, 0, SHEET_UUID,
    footprint="Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
    usage="Auxiliary 2.54mm pin header exposing VCC_2 (Pin 1) and multiple GND_2 (Pins 2-4) for future expansion or power injection",
    lcsc="C22368214", ft_pos="", ft_rot=""
)
parts.append(j7_block)


# ===========================================================================
# WIRING
# ===========================================================================

# SAT_3V3
for pin_xy in [U1["1"], U1["3"], U1["10"], U4["5"], C1["1"], C2["1"], C3["1"], C6["1"], JP14["2"]]:
    stub_label(pin_xy, "SAT_3V3")

# JP11 wiring to R1, R2
direct_wire(JP11["2"], R1["1"])
direct_wire(JP11["3"], R2["1"])
stub_label(JP11["1"], "SAT_3V3")

# GND
for pin_xy in [U1["5"], U4["2"], C1["2"], C2["2"], C3["2"], C6["2"], R5["2"], R8["2"], J1["5"], JP13["2"], JP15["2"]]:
    stub_label(pin_xy, "GND")

# VCC_1
stub_label(J1["4"], "VCC_1")
stub_label(JP14["1"], "VCC_1")

# VCC_2
stub_label(J1["3"], "VCC_2")
stub_label(JP14["3"], "VCC_2")
stub_label(J7["1"], "VCC_2")

# GND_2
stub_label(J1["6"], "GND_2")
stub_label(JP15["1"], "GND_2")
for pin_xy in [J7["2"], J7["3"], J7["4"]]:
    stub_label(pin_xy, "GND_2")

# SHIELD
stub_label(J1["SH1"], "SHIELD")
stub_label(J1["SH2"], "SHIELD")
stub_label(JP13["1"], "SHIELD")

# SDA_LOCAL / SCL_LOCAL (shared bus - continues onto Sheets 2 & 3)
stub_label(U1["2"], "SDA_LOCAL")
stub_label(R2["2"], "SDA_LOCAL")
stub_label(U1["4"], "SCL_LOCAL")
stub_label(R1["2"], "SCL_LOCAL")

# DSCL_N / DSCL_P
for pin_xy in [J1["1"], U1["6"], U4["3"]]:
    stub_label(pin_xy, "DSCL_N")
for pin_xy in [J1["2"], U1["7"], U4["1"]]:
    stub_label(pin_xy, "DSCL_P")

# DSCL Termination Ladder: SAT_3V3 -> R3 -> DSCL_P -> R4 -> DSCL_N -> R5 -> GND
stub_label(R3["1"], "SAT_3V3")

# Node DSCL_P between R3 and R4
mid_dscl_p = (127.0, 38.1)
wires.append(B.wire([R3["2"], mid_dscl_p]))
wires.append(B.wire([mid_dscl_p, R4["1"]]))
wires.append(B.wire([mid_dscl_p, (137.16, 38.1)]))
junctions.append(B.junction(*mid_dscl_p))
labels.append(B.global_label("DSCL_P", "input", 137.16, 38.1, 0, "left"))

# Node DSCL_N between R4 and R5
mid_dscl_n = (127.0, 63.5)
wires.append(B.wire([R4["2"], mid_dscl_n]))
wires.append(B.wire([mid_dscl_n, R5["1"]]))
wires.append(B.wire([mid_dscl_n, (137.16, 63.5)]))
junctions.append(B.junction(*mid_dscl_n))
labels.append(B.global_label("DSCL_N", "input", 137.16, 63.5, 0, "left"))

# R5 pin 2 connects to GND (already included in GND list above)

# DSDA_N / DSDA_P
for pin_xy in [J1["7"], U1["9"], U4["6"]]:
    stub_label(pin_xy, "DSDA_N")
for pin_xy in [J1["8"], U1["8"], U4["4"]]:
    stub_label(pin_xy, "DSDA_P")

# DSDA Termination Ladder: SAT_3V3 -> R6 -> DSDA_P -> R7 -> DSDA_N -> R8 -> GND
stub_label(R6["1"], "SAT_3V3")

# Node DSDA_P between R6 and R7
mid_dsda_p = (177.8, 38.1)
wires.append(B.wire([R6["2"], mid_dsda_p]))
wires.append(B.wire([mid_dsda_p, R7["1"]]))
wires.append(B.wire([mid_dsda_p, (187.96, 38.1)]))
junctions.append(B.junction(*mid_dsda_p))
labels.append(B.global_label("DSDA_P", "input", 187.96, 38.1, 0, "left"))

# Node DSDA_N between R7 and R8
mid_dsda_n = (177.8, 63.5)
wires.append(B.wire([R7["2"], mid_dsda_n]))
wires.append(B.wire([mid_dsda_n, R8["1"]]))
wires.append(B.wire([mid_dsda_n, (187.96, 63.5)]))
junctions.append(B.junction(*mid_dsda_n))
labels.append(B.global_label("DSDA_N", "input", 187.96, 63.5, 0, "left"))

# R8 pin 2 connects to GND (already included in GND list above)

lib_symbols_block = B.build_lib_symbols_block(LIB_IDS_USED)
out = [B.sheet_header("Differential I2C Endpoint", DOC_UUID, lib_symbols_block)]
out += parts + wires + junctions + labels + ncs
out.append(B.sheet_footer())

sch_text = "\n".join(out)
out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "differential_i2c_endpoint.kicad_sch")
with open(out_file, "w", encoding="utf-8") as f:
    f.write(sch_text)
print(f"wrote {out_file}")

sheet_file = os.path.join(B.PROJECT_ROOT, "sheets", "i2c_endpoint_v1.kicad_sch")
if os.path.exists(os.path.dirname(sheet_file)):
    with open(sheet_file, "w", encoding="utf-8") as f:
        f.write(sch_text)
    print(f"wrote {sheet_file}")

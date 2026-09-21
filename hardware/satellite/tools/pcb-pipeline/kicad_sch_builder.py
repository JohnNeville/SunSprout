"""Minimal helper for hand-authoring KiCad 10 .kicad_sch files programmatically.
Adapted from the battery_poweredboard project's tool of the same name. Draws every
wire as an explicit, deterministic coordinate this script computed itself - no
third-party auto-router or layout engine involved, unlike the tscircuit/
circuit-json-to-kicad pipeline this replaces for the satellite board.
"""
import uuid
import os
from extract_symbol import extract_renamed
from extract_pins import extract_pins as _extract_pins_auto

def u():
    return str(uuid.uuid4())

KICAD_SYM_DIR = r"C:\Program Files\KiCad\10.0\share\kicad\symbols"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_SYM = PROJECT_ROOT + r"\libraries\symbols\project.kicad_sym"

# lib_id -> (source .kicad_sym file, symbol name within that file)
LIB_SOURCES = {
    "project:RJHSE5380_QwiicBusCompatible": (PROJECT_SYM, "RJHSE5380_QwiicBusCompatible"),
    "project:PCA9615DPZ": (PROJECT_SYM, "PCA9615DPZ"),
    "project:DS2482S-100": (PROJECT_SYM, "DS2482S-100"),
    "project:SolderJumper_4_Bridged12": (PROJECT_SYM, "SolderJumper_4_Bridged12"),
    "project:SolderJumper_3_DualPullUp_Bridged": (PROJECT_SYM, "SolderJumper_3_DualPullUp_Bridged"),
    "Analog_ADC:ADS1015IDGS": (KICAD_SYM_DIR + r"\Analog_ADC.kicad_sym", "ADS1015IDGS"),
    "Interface_Expansion:DS2484R": (KICAD_SYM_DIR + r"\Interface_Expansion.kicad_sym", "DS2484R"),
    "Power_Protection:USBLC6-4SC6": (KICAD_SYM_DIR + r"\Power_Protection.kicad_sym", "USBLC6-4SC6"),
    "Jumper:SolderJumper_2_Bridged": (KICAD_SYM_DIR + r"\Jumper.kicad_sym", "SolderJumper_2_Bridged"),
    "Jumper:SolderJumper_2_Open": (KICAD_SYM_DIR + r"\Jumper.kicad_sym", "SolderJumper_2_Open"),
    "Jumper:SolderJumper_3_Bridged12": (KICAD_SYM_DIR + r"\Jumper.kicad_sym", "SolderJumper_3_Bridged12"),
    "Connector_Generic:Conn_01x03": (KICAD_SYM_DIR + r"\Connector_Generic.kicad_sym", "Conn_01x03"),
    "Connector_Generic:Conn_01x04": (KICAD_SYM_DIR + r"\Connector_Generic.kicad_sym", "Conn_01x04"),
    "Device:R": (KICAD_SYM_DIR + r"\Device.kicad_sym", "R"),
    "Device:C": (KICAD_SYM_DIR + r"\Device.kicad_sym", "C"),
    "power:GND": (KICAD_SYM_DIR + r"\power.kicad_sym", "GND"),
}

# ADS1115IDGS is a KiCad `(extends "ADS1015IDGS")` derived symbol - no geometry of its
# own. We embed the base symbol's full block (real pins/graphics) and rename+relabel it,
# same as what KiCad's own GUI does internally when resolving `extends` for embedding.
ADS1115_RENAME = {"old": "ADS1015IDGS", "new_lib_id": "Analog_ADC:ADS1115IDGS", "new_name": "ADS1115IDGS"}


def build_lib_symbols_block(lib_ids_used):
    blocks = []
    seen = set()
    for lib_id in sorted(set(lib_ids_used)):
        if lib_id == "Analog_ADC:ADS1115IDGS":
            src_file, sym_name = LIB_SOURCES["Analog_ADC:ADS1015IDGS"]
            block = extract_renamed(src_file, sym_name, "Analog_ADC:ADS1115IDGS")
            block = block.replace("ADS1015IDGS", "ADS1115IDGS")
            blocks.append(block)
            continue
        src_file, sym_name = LIB_SOURCES[lib_id]
        blocks.append(extract_renamed(src_file, sym_name, lib_id))
    inner = "\n".join(blocks)
    return "\t(lib_symbols\n" + inner + "\n\t)\n"


def get_pins(lib_id):
    """Auto-extracted pin table: {pin_number: (dx, dy, angle, pin_name)}, Y-up local
    offsets as authored in the source library."""
    if lib_id == "Analog_ADC:ADS1115IDGS":
        src_file, sym_name = LIB_SOURCES["Analog_ADC:ADS1015IDGS"]
    else:
        src_file, sym_name = LIB_SOURCES[lib_id]
    return _extract_pins_auto(src_file, sym_name)


ROOT_UUID = "b8ad246c-0963-44e9-b36f-20d138e559cc"


GRID = 1.27


def snap(val, grid=GRID):
    """Snap coordinate to nearest grid increment (default 1.27 mm / 50 mil)."""
    v = round(round(val / grid) * grid, 4)
    return int(v) if v.is_integer() else v


class Pin(tuple):
    """A 2-tuple (x, y) with pin orientation metadata for stub/wire direction."""
    def __new__(cls, x, y, dx=10.16, dy=0, side="right"):
        return super().__new__(cls, (x, y))

    def __init__(self, x, y, dx=10.16, dy=0, side="right"):
        self.dx = dx
        self.dy = dy
        self.side = side


PROP_IDS = {
    "Reference": 0,
    "Value": 1,
    "Footprint": 2,
    "Datasheet": 3,
    "Usage": 4,
    "LCSC Part": 5,
    "FT Position Offset": 6,
    "FT Rotation Offset": 7,
}


def prop(name, value, x, y, angle=0, hide=False, justify=None, prop_id=None):
    x, y = snap(x), snap(y)
    j = f"\n\t\t\t\t(justify {justify})" if justify else ""
    h = "\n\t\t\t\t(hide yes)" if hide else ""
    pid = prop_id if prop_id is not None else PROP_IDS.get(name, 4)
    return f'''\t\t(property "{name}" "{value}"
\t\t\t(id {pid})
\t\t\t(at {x} {y} {angle})
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t){j}{h}
\t\t\t)
\t\t)'''


def symbol_instance(lib_id, ref, value, x, y, angle, sheet_symbol_uuid,
                     footprint="", datasheet="", extra_props="",
                     ref_pos=None, value_pos=None, dnp=False, project_name="SunSproutSatellite",
                     usage="", lcsc="", ft_pos="", ft_rot="", hide_value=None):
    import math
    x, y = snap(x), snap(y)
    pins = get_pins(lib_id)
    embedded_lib_id = "Analog_ADC:ADS1115IDGS" if lib_id == "Analog_ADC:ADS1115IDGS" else lib_id
    sym_uuid = u()
    pin_uuids = {num: u() for num in pins}
    pin_lines = [f'\t\t(pin "{num}"\n\t\t\t(uuid "{pin_uuids[num]}")\n\t\t)' for num in pins]
    pins_block = "\n".join(pin_lines)
    
    # Text orientation: KiCad rotates properties by symbol angle, so we counter-rotate by (360 - angle) % 360
    # to keep Reference and Value text horizontal and legible.
    prop_angle = (360 - angle) % 360
    if angle in (90, 270):
        rx, ry = (snap(ref_pos[0]), snap(ref_pos[1])) if ref_pos else (snap(x + 3.81), snap(y))
        vx, vy = (snap(value_pos[0]), snap(value_pos[1])) if value_pos else (snap(x + 3.81), snap(y + 2.54))
    else:
        rx, ry = (snap(ref_pos[0]), snap(ref_pos[1])) if ref_pos else (snap(x - 7.62), snap(y - 8.89))
        vx, vy = (snap(value_pos[0]), snap(value_pos[1])) if value_pos else (snap(x - 7.62), snap(y - 6.35))
    
    # Default hide_value=True for jumpers to keep schematics clean
    if hide_value is None:
        hide_value = lib_id.startswith("Jumper:")
        
    usage_str = f"\n{prop('Usage', usage, x, y, hide=True)}" if usage else ""
    lcsc_str = f"\n{prop('LCSC Part', lcsc, x, y, hide=True)}"
    ft_pos_str = f"\n{prop('FT Position Offset', ft_pos, x, y, hide=True)}"
    ft_rot_str = f"\n{prop('FT Rotation Offset', ft_rot, x, y, hide=True)}"
    body = f'''\t(symbol
\t\t(lib_id "{embedded_lib_id}")
\t\t(at {x} {y} {angle})
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp {"yes" if dnp else "no"})
\t\t(uuid "{sym_uuid}")
\t\t(fields_autoplaced no)
{prop("Reference", ref, rx, ry, angle=prop_angle)}
{prop("Value", value, vx, vy, angle=prop_angle, hide=hide_value)}
{prop("Footprint", footprint, x, y, hide=True)}
{prop("Datasheet", datasheet, x, y, hide=True)}{usage_str}{lcsc_str}{ft_pos_str}{ft_rot_str}
{extra_props}
{pins_block}
\t\t(instances
\t\t\t(project "{project_name}"
\t\t\t\t(path "/{ROOT_UUID}/{sheet_symbol_uuid}"
\t\t\t\t\t(reference "{ref}")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)'''
    # Transform pin positions and exit angles with symbol rotation
    rad = math.radians(angle)
    cos_a = round(math.cos(rad))
    sin_a = round(math.sin(rad))

    positions = {}
    for num in pins:
        pdx, pdy, pangle, pname = pins[num]
        # In KiCad library: pdx is X (right), pdy is Y (UP).
        # Counter-clockwise rotation by `angle` in library space (Y up):
        rot_x = pdx * cos_a - pdy * sin_a
        rot_y = pdx * sin_a + pdy * cos_a
        # In schematic canvas: X is right, Y is DOWN.
        pos_x = snap(x + rot_x)
        pos_y = snap(y - rot_y)
        # Rotated pin exit angle:
        rot_angle = (pangle + angle) % 360
        if rot_angle == 0:
            p_dx, p_dy, p_side = -10.16, 0, "left"
        elif rot_angle == 180:
            p_dx, p_dy, p_side = 10.16, 0, "right"
        elif rot_angle == 270:
            p_dx, p_dy, p_side = 0, -10.16, "top"
        elif rot_angle == 90:
            p_dx, p_dy, p_side = 0, 10.16, "bottom"
        else:
            p_dx, p_dy, p_side = 10.16, 0, "right"
        positions[num] = Pin(pos_x, pos_y, p_dx, p_dy, p_side)
    return body, positions


def wire(points):
    if len(points) < 2:
        return ""
    if len(points) == 2:
        pts = f"(xy {snap(points[0][0])} {snap(points[0][1])}) (xy {snap(points[1][0])} {snap(points[1][1])})"
        return f'''\t(wire
\t\t(pts {pts})
\t\t(stroke
\t\t\t(width 0)
\t\t\t(type default)
\t\t)
\t\t(uuid "{u()}")
\t)'''
    # KiCad schematic syntax requires exactly 2 endpoints per wire
    segments = [wire([points[i], points[i + 1]]) for i in range(len(points) - 1)]
    return "\n".join(segments)


def junction(x, y):
    return f'\t(junction\n\t\t(at {snap(x)} {snap(y)})\n\t\t(diameter 0)\n\t\t(color 0 0 0 0)\n\t\t(uuid "{u()}")\n\t)'


def global_label(name, shape, x, y, angle, justify="left"):
    return f'''\t(global_label "{name}"
\t\t(shape {shape})
\t\t(at {snap(x)} {snap(y)} {angle})
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.27 1.27)
\t\t\t)
\t\t\t(justify {justify})
\t\t)
\t\t(uuid "{u()}")
\t\t(fields_autoplaced no)
\t)'''


def no_connect(x, y):
    return f'\t(no_connect\n\t\t(at {snap(x)} {snap(y)})\n\t\t(uuid "{u()}")\n\t)'


def power_symbol(ref, value, x, y, sheet_symbol_uuid, pwr_num, project_name="SunSproutSatellite"):
    x, y = snap(x), snap(y)
    lib_id = f"power:{value}"
    sym_uuid = u()
    pin_uuid = u()
    return f'''\t(symbol
\t\t(lib_id "{lib_id}")
\t\t(at {x} {y} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "{sym_uuid}")
\t\t(fields_autoplaced no)
{prop("Reference", f"#PWR0{pwr_num:02d}", x, y-6.35, hide=True)}
{prop("Value", value, x, y-3.81)}
{prop("Footprint", "", x, y, hide=True)}
{prop("Datasheet", "", x, y, hide=True)}
\t\t(pin "1"
\t\t\t(uuid "{pin_uuid}")
\t\t)
\t\t(instances
\t\t\t(project "{project_name}"
\t\t\t\t(path "/{ROOT_UUID}/{sheet_symbol_uuid}"
\t\t\t\t\t(reference "#PWR0{pwr_num:02d}")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)'''


def sheet_header(title, doc_uuid, lib_symbols_block, paper="A4"):
    return f'''(kicad_sch
\t(version 20260306)
\t(generator "eeschema")
\t(generator_version "10.0")
\t(uuid "{doc_uuid}")
\t(paper "{paper}")
\t(title_block
\t\t(title "{title}")
\t\t(company "SunSproutSatellite")
\t)
{lib_symbols_block}'''


def sheet_footer():
    return "\t(embedded_fonts no)\n)\n"

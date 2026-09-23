# Differential I2C endpoint — PCA9615

| Item | Value |
|---|---|
| Reference | `U1` |
| Part | NXP PCA9615DPZ |
| Package | TSSOP-10 |
| Schematic sheet | `sheets/i2c_endpoint_v1.kicad_sch` |

## Function

The buffer converts the four-wire differential bus arriving over the cable back into a
standard two-wire I2C bus. It is the same part, in the same role, as the hub's own
[differential I2C buffer](../../hub/modules/pca9615-i2c-buffer.md) — but this board sits at
the far end of the cable, not in the middle of it.

## Connector

| Reference | Part | Function |
|---|---|---|
| `J1` | Amphenol RJHSE5380 | 8P8C jack |

One jack, not two. This board is always a dead-end leaf. It never passes a cable through to
another node. That is the central difference from the hub's own copy of this circuit, and it
drives every other decision on this page.

## Termination — Fixed Endpoint Resistor Ladders

The differential I2C standard (and PCA9615 datasheet) requires termination at both true ends of the transmission line. The hub is an intermediate node, so it carries none. This board is designed as a dedicated bus endpoint satellite, so it carries complete fixed termination networks directly populated on the board:

| Pair | Network | Values |
|---|---|---|
| `DSCL+`/`DSCL-` | `RJ45_VCC_1` → 390Ω (R3) → node `DSCL_P` → 100Ω (R4) → node `DSCL_N` → 390Ω (R5) → `RJ45_GND_1` | `R3`, `R4`, `R5` |
| `DSDA+`/`DSDA-` | `RJ45_VCC_1` → 390Ω (R6) → node `DSDA_P` → 100Ω (R7) → node `DSDA_N` → 390Ω (R8) → `RJ45_GND_1` | `R6`, `R7`, `R8` |

These standard termination ladders provide:
1. 100Ω AC line matching across `DSCL_P`/`DSCL_N` and `DSDA_P`/`DSDA_N`.
2. Upper bias pull-up (390Ω to `RJ45_VCC_1`) and lower bias pull-down (390Ω to `RJ45_GND_1`) guaranteeing an idle high differential state directly referenced to the incoming cable power domain.

For intermediate/midpoint daisy-chain applications where termination should be omitted, a dedicated Midpoint subsheet variant can be swapped in without needing trace-cutting jumpers.

## Decoupled Power Architecture & Auxiliary Expansion

The PCA9615 buffer provides true galvanic supply domain separation:
- **Cable Side (`VDDB`)**: Directly powered by incoming Pair 1 power (`RJ45_VCC_1` / `RJ45_GND_1`). This isolates cable IR drop, noise, and transients from the satellite's local sensor rail.
- **Local Side (`VDDA`) & Enable (`EN`)**: Powered by `SAT_3V3` and referenced to system `GND`.
- **Bulk Reservoir (`C1`)**: Placed directly across raw cable entry nets `RJ45_VCC_1` and `RJ45_GND_1` (22µF) to stabilize cable impedance and surge currents.

| Reference | Value / Type | Function |
|---|---|---|
| `C1` | 22µF | Bulk reservoir across raw cable entry (`RJ45_VCC_1` to `RJ45_GND_1`), absorbing cable IR drop |
| `C2` | 100nF | Local decoupling for `VDDA` (`SAT_3V3` to `GND`) |
| `C3` | 100nF | Cable-side decoupling for `VDDB` (`RJ45_VCC_1` to `RJ45_GND_1`) |
| `JP18` | SolderJumper_2_Bridged | Power source bridge: connects `RJ45_VCC_1` to `SAT_3V3` (bridged by default) |
| `JP17` | SolderJumper_2_Bridged | Ground isolation bridge: connects `RJ45_GND_1` to `GND` (bridged by default) |
| `J7` | Conn_01x04 (2.54mm) | Cable power breakout: Pin 1 = `RJ45_VCC_1`, Pin 2 = `RJ45_GND_1`, Pin 3 = `RJ45_GND_2`, Pin 4 = `RJ45_VCC_2` |
| `J9` | Conn_01x02 (2.54mm) | Local satellite power input: Pin 1 = `SAT_3V3`, Pin 2 = `GND` |

### Standard Mode vs. Long-Distance Buck Regulation

1. **Standard Direct Mode (Factory Default)**:
   - `JP18` and `JP17` remain bridged.
   - 3.3V power from Hub Pair 1 directly supplies the satellite (`SAT_3V3` = `RJ45_VCC_1`, `GND` = `RJ45_GND_1`).
   - Zero additional components required for short-to-medium runs (<20m).

2. **Long-Distance / High-Sag Mode (External Buck Converter)**:
   - For long runs (>20m) or high-voltage feeds (e.g., 12V or 24V delivered over Pair 1 or Pair 3):
     1. Slice the copper trace of **`JP18`** to decouple `SAT_3V3` from `RJ45_VCC_1`.
     2. Optionally slice **`JP17`** if full ground isolation is required.
     3. Connect an external step-down buck converter (or daughterboard):
        - **Buck Input**: Connect to `J7` Pin 1 (`RJ45_VCC_1`) and Pin 2 (`RJ45_GND_1`), or Pin 4 (`RJ45_VCC_2`) and Pin 3 (`RJ45_GND_2`).
        - **Buck Regulated 3.3V Output**: Connect to `J9` Pin 1 (`SAT_3V3`) and Pin 2 (`GND`).
   - Because `U1.VDDB` operates over 2.3V to 5.5V, it can run directly from raw 3.3V–5V cable power while local sensors receive clean, regulated 3.3V via `J9`.

## I2C pull-ups — single-cut dual solder jumper

| Reference | Value | Net | Jumper | Footprint |
|---|---|---|---|---|
| `R1` | 4.7kΩ | `SCL_LOCAL` | `JP11` (Pin 2, bridged by default) | `project:SolderJumper-3_P1.3mm_DualPullUp_SingleCut_RoundedPad1.0x1.5mm` |
| `R2` | 4.7kΩ | `SDA_LOCAL` | `JP11` (Pin 3, bridged by default) | `project:SolderJumper-3_P1.3mm_DualPullUp_SingleCut_RoundedPad1.0x1.5mm` |

These pull up the local bus shared by this buffer's I2C-bus side, the ADS1115, the DS2482S-100+, and the Qwiic port (`J8`). Unlike the hub's own pull-ups, which die when firmware switches off the user rail, these are always live whenever the satellite rail is powered.

A custom 3-pad dual-trace solder jumper (`JP11`) replaces separate jumpers:
- **Pin 1 (Top)**: Common `SAT_3V3` supply pad.
- **Pin 2 (Bottom-Left)**: Connects to `R1` (`SCL_LOCAL` pull-up).
- **Pin 3 (Bottom-Right)**: Connects to `R2` (`SDA_LOCAL` pull-up).
- **Collinear Single Cut Channel**: Both etched copper bridge traces (Pin 1 → Pin 2 and Pin 1 → Pin 3) run parallel across a single horizontal cut channel marked by silkscreen cut guides. A single slice with an X-Acto knife severs both pull-up connections simultaneously while preserving complete electrical isolation between SCL and SDA (preventing bus cross-talk).
- **Reversible**: Bridging the pads with solder restores 3.3V to both pull-up resistors.

## ESD protection & Cable Shield Grounding

`U4` (`USBLC6-4SC6`, stock KiCad part) protects the four differential lines. The RJ45 jack
is the only connector on this board designed to carry a cable off-board, and it is the more
exposed end of that cable — outdoors, handled during install.

| Reference | Function |
|---|---|
| `U4` | Low-capacitance ESD protection diode array clamping differential lines to `RJ45_VCC_1` and `RJ45_GND_1` |
| `C6` | 100nF decoupling capacitor for `U4`'s `VBUS` clamp rail (`RJ45_VCC_1` to `RJ45_GND_1`) |
| `JP13` | Cuttable solder jumper connecting `J1.SHIELD` to `RJ45_GND_1` (bridged by default) |

The RJ45 metal shield tabs (`SH1`, `SH2`) connect to `RJ45_GND_1` through solder jumper `JP13`. In industrial or long outdoor cable runs where ground loops between the hub and the satellite are a concern, cutting `JP13` breaks the shield-to-board DC ground connection at the satellite end, leaving the cable shield grounded only at the hub end (single-point shield ground).


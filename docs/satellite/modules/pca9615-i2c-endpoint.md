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
| `DSCL+`/`DSCL-` | `SAT_3V3` → 390Ω (R3) → node `DSCL_P` → 100Ω (R4) → node `DSCL_N` → 390Ω (R5) → `GND` | `R3`, `R4`, `R5` |
| `DSDA+`/`DSDA-` | `SAT_3V3` → 390Ω (R6) → node `DSDA_P` → 100Ω (R7) → node `DSDA_N` → 390Ω (R8) → `GND` | `R6`, `R7`, `R8` |

These standard termination ladders provide:
1. 100Ω AC line matching across `DSCL_P`/`DSCL_N` and `DSDA_P`/`DSDA_N`.
2. Upper bias pull-up (390Ω to `SAT_3V3`) and lower bias pull-down (390Ω to `GND`) guaranteeing an idle high differential state.

For intermediate/midpoint daisy-chain applications where termination should be omitted, a dedicated Midpoint subsheet variant can be swapped in without needing trace-cutting jumpers.

## Power & Auxiliary Expansion

Both supply pins, `VDD(A)` and `VDD(B)`, connect to `SAT_3V3` — this board's local rail.
By default, `SAT_3V3` is fed from `VCC_1` arriving over the RJ45 cable via 3-way solder jumper `JP14` (bridged 1-2 by default).

| Reference | Value / Type | Function |
|---|---|---|
| `C1` | 22µF | Bulk reservoir at the power-in point, absorbing IR drop from the cable run |
| `C2` | 100nF | Local decoupling for `VDD(A)` |
| `C3` | 100nF | Local decoupling for `VDD(B)` |
| `JP14` | SolderJumper_3_Bridged12 | Power source selector (1-2: `VCC_1` default; 2-3: `VCC_2` aux) |
| `JP15` | SolderJumper_2_Bridged | Cable `GND_2` (`GRN_N`) to system `GND` bridge (bridged by default) |
| `J7` | Conn_01x04 (2.54mm) | Auxiliary expansion header: Pin 1 = `VCC_2`, Pins 2–4 = `GND_2` |

Both supply pins get their own capacitor, for the same reason the hub's copy of this circuit
does: two independent supply domains, so one shared capacitor would leave one domain without
local decoupling.

### Auxiliary Power Injection & Expansion (`J7`, `JP14`, `JP15`)

Mirroring the hub's `J2`/`JP2`/`JP3` auxiliary power injection architecture:
- `VCC_2` (conductor 3 on RJ45) is exposed on pin 1 of header `J7` and pin 3 of `JP14`.
- `GND_2` / `GRN_N` (conductor 6 on RJ45) is exposed on pins 2, 3, and 4 of `J7` and connects to system `GND` through cuttable solder jumper `JP15`.
- If an auxiliary power supply (e.g. 5V, 12V, or high voltage for a local buck converter) is injected on `VCC_2`/`GND_2`, `JP14` can be switched from pads 1-2 to pads 2-3 to power the satellite from `VCC_2`.
- If isolated secondary power is used, cutting `JP15` isolates `GND_2` from local system `GND`.
- Header `J7` provides a convenient standard 0.1" (2.54mm) pitch tap to inject power or connect off-board modules to the cable's secondary power pair.

### Why no local regulator by default

The reference designs this circuit is drawn from — SparkFun's QwiicBus Midpoint and the real
QwiicBus EndPoint — both carry a local buck regulator, because their power can arrive at up
to 36V over a dedicated high-voltage pair and needs stepping down on-site.

This board's expected cable runs are short (under roughly 20m). At that length, and at this
board's modest current draw, round-trip cable resistance costs on the order of 0.1–0.2V of
sag — comfortably inside every IC's supply margin, including this part's own 3.0V `VDD(B)`
floor. Adding a regulator here would add cost and a failure point for a problem that does not
exist at this cable length.

If a future installation requires high-voltage power delivery over `VCC_2`, `J7` allows clipping on a daughterboard buck regulator or switching `JP14`.

## I2C pull-ups — single-cut dual solder jumper

| Reference | Value | Net | Jumper | Footprint |
|---|---|---|---|---|
| `R1` | 4.7kΩ | `SCL_LOCAL` | `JP11` (Pin 2, bridged by default) | `project:SolderJumper-3_P1.3mm_DualPullUp_SingleCut_RoundedPad1.0x1.5mm` |
| `R2` | 4.7kΩ | `SDA_LOCAL` | `JP11` (Pin 3, bridged by default) | `project:SolderJumper-3_P1.3mm_DualPullUp_SingleCut_RoundedPad1.0x1.5mm` |

These pull up the local bus shared by this buffer's I2C-bus side, the ADS1115, and the DS2482S-100+. Unlike the hub's own pull-ups, which die when firmware switches off the user rail, these are always live whenever the cable is powered.

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
| `U4` | Low-capacitance ESD protection diode array clamping differential lines to `SAT_3V3` and `GND` |
| `C6` | 100nF decoupling capacitor for `U4`'s `VBUS` clamp rail |
| `JP13` | Cuttable solder jumper connecting `J1.SHIELD` to system `GND` (bridged by default) |

The RJ45 metal shield tabs (`SH1`, `SH2`) connect to `GND` through solder jumper `JP13`. In industrial or long outdoor cable runs where ground loops between the hub and the satellite are a concern, cutting `JP13` breaks the shield-to-board DC ground connection at the satellite end, leaving the cable shield grounded only at the hub end (single-point shield ground).


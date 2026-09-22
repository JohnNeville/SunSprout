---
sidebar_position: 2
title: Satellite Dimensions & Mounting
---

# Satellite Dimensions & Mounting

Everything on this page is measured from the production layout in
`hardware/satellite/SunSproutSatellite.kicad_pcb`. If you need exact three-dimensional geometry — component
heights, connector bodies, mating clearances — use the STEP model linked from
[Design Files](./design-files.md) rather than working from the numbers here.

---

## Board Outline

| Property | Value |
|---|---|
| **Outline Dimensions** | **27.25 × 51.10 mm** |
| **Thickness** | 1.6 mm |
| **Copper Layers** | 4 (`F.Cu`, `In1.Cu`, `In2.Cu`, `B.Cu`) |
| **Corners** | Square — no radius |
| **Cutouts / Notches** | None |

The outline is a clean, slender rectangle engineered to fit inside slim waterproof enclosures, electrical conduit, or outdoor probe housings. There is no asymmetrical keying cutout; orient the board by the RJ45 jack (`J1`) facing the cable entry point.

---

## Coordinate Frame

All positions below are given in millimetres from the **top-left corner of the board, viewed from the component (top) side**:
- **X = 0.0 mm** at the left edge, increasing to the **right** (+X).
- **Y = 0.0 mm** at the top edge, increasing **downward** (+Y).

This matches the coordinate convention used in KiCad 10 and aligns directly with the board layout and interactive pinout diagram.

---

## Mounting Holes

The board provides three non-plated mounting holes sized for standard M2 hardware:

| Hole | X (mm) | Y (mm) | Inset X | Inset Y | Purpose |
|---|---|---|---|---|---|
| **MP1** | 3.00 | 3.00 | 3.0 mm from left | 3.0 mm from top | Top-left corner mounting |
| **MP2** | 24.25 | 3.00 | 3.0 mm from right | 3.0 mm from top | Top-right corner mounting |
| **MP3** | 12.00 | 32.10 | 12.0 mm from left | Mid-board (32.1 mm) | Central mechanical standoff support |

### Mounting Hole Specifications

| Property | Value |
|---|---|
| **Drill Diameter** | **Ø2.1 mm** |
| **Fastener Size** | **M2** (screws or hex standoffs) |
| **Plating** | **Non-plated** (isolated from all internal copper and planes) |
| **Top Hole Span** | 21.25 mm (center-to-center between MP1 and MP2) |
| **Keep-out Diameter** | Ø4.5 mm circular annular clearance around each hole |

:::note[Non-Plated Holes]
Because the mounting holes are non-plated, metal screws or standoffs provide **no electrical ground connection** to the board. If chassis or shield grounding is desired, bond to the shield jumper (`JP13`) or a ground terminal on header `J7`.
:::

---

## Connector Locations & Clearances

All connectors are through-hole components mounted on the **top side** of the PCB:

| Ref | Function | Part / Type | Center X (mm) | Center Y (mm) | Orientation | Height Above PCB |
|---|---|---|---|---|---|---|
| **`J1`** | Differential I2C / Cable Input | Amphenol RJHSE5380 (8P8C / RJ45) | 15.95 | 45.20 | Facing bottom edge | ~13.5 mm |
| **`J6`** | 1-Wire Temperature Probe | JST PH 2.0mm 3-pin vertical | 3.65 | 8.30 | Vertical (left edge) | ~6.0 mm (~7.5 mm mated) |
| **`J2`** | Moisture Sensor Channel 1 | JST PH 2.0mm 3-pin vertical | 3.70 | 17.40 | Vertical (left edge) | ~6.0 mm (~7.5 mm mated) |
| **`J3`** | Moisture Sensor Channel 2 | JST PH 2.0mm 3-pin vertical | 3.65 | 26.50 | Vertical (left edge) | ~6.0 mm (~7.5 mm mated) |
| **`J4`** | Moisture Sensor Channel 3 | JST PH 2.0mm 3-pin vertical | 3.60 | 35.50 | Vertical (left edge) | ~6.0 mm (~7.5 mm mated) |
| **`J5`** | Moisture Sensor Channel 4 | JST PH 2.0mm 3-pin vertical | 3.60 | 44.50 | Vertical (left edge) | ~6.0 mm (~7.5 mm mated) |
| **`J7`** | Auxiliary Power & Tap | 1×4 Pin Header (2.54mm pitch) | 23.95 | 30.89 | Vertical (right edge) | ~8.5 mm mated |

### Connector Spacing Highlights
- **Sensor Port Strip (`J6`, `J2`–`J5`)**: The five sensor connectors form a neat, uniform line along the left edge. The centers sit roughly 3.65 mm from the board edge, with a consistent **~9.0 mm vertical pitch** between successive connectors:
  - `J6` (Y = 8.30 mm)
  - `J2` (Y = 17.40 mm, Δ = 9.1 mm)
  - `J3` (Y = 26.50 mm, Δ = 9.1 mm)
  - `J4` (Y = 35.50 mm, Δ = 9.0 mm)
  - `J5` (Y = 44.50 mm, Δ = 9.0 mm)
- **RJ45 Differential Port (`J1`)**: Positioned at the bottom center (X = 15.95, Y = 45.20 mm). The jack's mating face is flush with the bottom board edge with the release latch facing downward towards the PCB.

---

## Solder Jumpers & Configuration Points

The board incorporates six configuration jumpers (five on the bottom side, one on the top side):

| Ref | Layer | Center (X, Y) | Silk Label | Default State | Function |
|---|---|---|---|---|---|
| **`JP1`** | **Bottom** | (10.34, 23.20) | `ADC 0x48 0x49 0x4A 0x4B` | **Pads 1-2 bridged** (Address `0x48`) | ADS1115 I2C address strap selector. Cut bridge to select alternate address. |
| **`JP11`** | **Top** | (9.35, 14.05) | `I2C PULL UP` | **Both pull-ups bridged** | Dual-trace single-cut jumper for local 4.7kΩ I2C pull-ups on `SCL_LOCAL`/`SDA_LOCAL`. |
| **`JP13`** | **Bottom** | (22.15, 37.40) | `SHLD GND` | **Bridged** | Bonds RJ45 metal shield (`J1.SHIELD`) to system `GND`. Cut for single-point grounding. |
| **`JP14`** | **Bottom** | (23.95, 20.09) | — | **Pads 1-2 bridged** (`VCC_1`) | Power source selector: 1-2 selects `VCC_1` from cable; 2-3 selects `VCC_2`. |
| **`JP15`** | **Bottom** | (21.05, 27.10) | `GND_1 <-> GND_2` | **Bridged** | Bonds cable conductor 6 (`GND_2`) to local system ground. Cut to isolate secondary ground. |
| **`JP16`** | **Bottom** | (13.10, 6.90) | `OneWire AD0 AD1 VCC GND` | **Both grounded** (Address `0x18`) | Configures address strap pins on the DS2482-100+ 1-Wire bridge. |

---

## Enclosure & Mechanical Clearances

When designing or choosing an enclosure for the SunSprout Satellite:

1. **Internal Cavity Width**: At least **29.0 mm** (providing ~0.9 mm clearance on both lateral sides of the 27.25 mm PCB).
2. **Internal Cavity Length**: At least **53.0 mm** for the PCB body, plus cable egress clearance.
3. **Cable Egress Clearance**: Allow at least **35.0 mm** clearance extending off the bottom edge (below `J1`) to accommodate the mating RJ45 plug body, strain relief boot, and minimum bend radius.
4. **Vertical Clearance (Top Side)**: At least **15.0 mm** above the top copper face. The RJ45 jack stands 13.5 mm tall; extra headroom ensures easy mating/unmating of the latch and vertical JST PH plugs.
5. **Vertical Clearance (Bottom Side)**: At least **2.5–3.0 mm** standoff clearance beneath the bottom copper layer to clear through-hole leads, clipped pins, and solder jumper beads.

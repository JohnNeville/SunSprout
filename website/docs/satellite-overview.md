---
sidebar_position: 1
title: Satellite Overview
---

# SunSprout Satellite

:::info[Differential I2C Sensor Leaf Node]

The **SunSprout Satellite** is the dedicated remote sensor endpoint for the SunSprout ecosystem. It terminates a long differential-I2C cable run from the [SunSprout Hub](./overview.md), restores standard local I2C signaling, and monitors up to four capacitive soil-moisture probes plus a 1-Wire soil-temperature probe.

:::

<div style={{textAlign: 'center', margin: '2rem 0'}}>
  <img
    src="/SunSprout/img/satellite-board-top.png"
    alt="SunSprout Satellite 3D top render hero image"
    style={{maxWidth: '85%', borderRadius: '8px', boxShadow: '0 4px 20px rgba(0,0,0,0.15)'}}
  />
</div>

## What is the Satellite?

The **SunSprout Satellite** functions as a remote garden/agricultural probe station. Where standard I2C buses degrade after a few tens of centimetres, the Satellite connects to the Hub over standard Category-rated twisted-pair patch cable (up to 20+ metres) using differential signaling.

At the endpoint, the board translates the differential clock and data signals back into standard 3.3V single-ended I2C, hosts an onboard 16-bit analog-to-digital converter (ADS1115) and a hardware 1-Wire master bridge (DS2482-100+), and distributes power and ground to local sensors.

<div style={{textAlign: 'center', margin: '2rem 0'}}>
  <img
    src="/SunSprout/img/satellite-board-bottom.png"
    alt="SunSprout Satellite 3D bottom render"
    style={{maxWidth: '85%', borderRadius: '8px', boxShadow: '0 4px 20px rgba(0,0,0,0.15)'}}
  />
</div>

---

## Physical Specifications

| Property | Value | Notes |
|---|---|---|
| **Form factor** | 27.25 × 51.10 mm | Slender rectangular profile fits small waterproof enclosures or conduit |
| **Board thickness** | 1.6 mm | Standard FR4 |
| **Layer stackup** | 4 copper layers | `F.Cu` (signals), `In1.Cu` (power), `In2.Cu` (ground plane), `B.Cu` (signals) |
| **Mounting** | 3× M2 non-plated holes | 3.0 mm corner inset at top; 1 mid-board support hole |
| **Primary interface** | 1× Amphenol RJHSE5380 | 8P8C (RJ45) jack with metal EMI shield |
| **Sensor ports** | 5× JST PH 2.0mm 3-pin | 4 moisture probe inputs + 1 temperature probe input |
| **Auxiliary port** | 1× 2.54mm 4-pin header | Secondary power injection / tap header (`VCC_2`, `GND_2`, `GND`, `SAT_3V3`) |

---

## Capabilities & Architecture

### 1. Differential I2C Bus Endpoint (PCA9615)
- **PCA9615DPZ** differential buffer translates `DSCL+`/`DSCL-` and `DSDA+`/`DSDA-` back into local `SCL_LOCAL` and `SDA_LOCAL`.
- **Fixed Onboard Termination**: Populated with matched resistor ladders (390Ω bias pull-ups to `SAT_3V3`, 100Ω line matching resistors, and 390Ω bias pull-downs to `GND`) across both differential pairs. This ensures proper transmission line termination without loose plug-in resistors.
- **TVS / ESD Protection**: An onboard **USBLC6-4SC6** transient voltage suppressor array clamps all four differential lines against outdoor static and handling discharge.

### 2. High-Precision Soil Moisture Monitoring (ADS1115)
- **ADS1115IDGS** 16-bit 4-channel delta-sigma ADC with programmable gain amplifier and internal reference.
- Reads analog voltage outputs from up to **four** independent capacitive soil-moisture probes (e.g., DFRobot SEN0193 / Gravity interface).
- Four 3-pin vertical JST PH connectors (`J2`–`J5`) distribute `GND`, `SAT_3V3`, and signal lines (`MOIST1`–`MOIST4`).
- **Configurable I2C Address (`JP1`)**: 4-way solder jumper on the bottom side selects addresses `0x48`, `0x49`, `0x4A`, or `0x4B` (`0x48` default bridged).

### 3. Dedicated 1-Wire Temperature Bridge (DS2482-100+)
- Hardware I2C-to-1-Wire master bridge eliminates software bit-banging and timing jitter over long probe leads.
- Dedicated 3-pin vertical JST PH connector (`J6`) connects a waterproof DS18B20 digital temperature probe (`SAT_3V3`, `GND`, `ONEWIRE_DQ`).
- Onboard 4.7kΩ pull-up to `SAT_3V3` provides reliable bus drive.
- **Configurable I2C Address (`JP16`)**: Dual solder jumper selects address bits `AD0` and `AD1` (default: `0x18`).

### 4. Power & Auxiliary Flexibility
- **Zero Local Regulator Overhead**: Designed to operate directly from `SAT_3V3` delivered by the Hub over conductor 4 (`VCC_1`). At typical cable lengths (under 20 m) and satellite currents (~15–25 mA), round-trip IR drop is negligible (~0.1–0.2 V).
- **Decoupling & Reservoir**: An onboard 22 µF bulk capacitor (`C1`) buffers cable transients, accompanied by dedicated 100 nF high-frequency ceramic decoupling capacitors directly adjacent to every active IC pin.
- **Auxiliary Power Path (`J7`, `JP14`, `JP15`)**:
  - `VCC_2` (conductor 3) and `GND_2` (conductor 6) pass directly to header `J7`.
  - Solder jumper `JP14` allows rerouting the satellite's power feed from `VCC_1` to `VCC_2`.
  - Cuttable jumper `JP15` permits isolating `GND_2` from system `GND`.
- **Single-Cut Pull-Up Jumper (`JP11`)**: A custom 3-pad solder jumper with a single collinear cut channel allows disconnecting both local 4.7kΩ I2C pull-ups simultaneously with a single craft knife slice.
- **Cable Shield Isolation (`JP13`)**: Cuttable solder jumper on the bottom side connects the RJ45 metal shield to system ground by default, allowing single-point grounding configurations when required.

---

## Further Reading
- [Dimensions & Mounting](./satellite-dimensions.md) — Exact outline, mounting hole locations, connector courtyard extents, and enclosure clearance guidance.
- [Hub Overview](./overview.md) — Main system controller, solar MPPT charger, and differential I2C driver.
- [Design Files](./design-files.md) — Schematic PDFs, Gerbers, and 3D CAD STEP models.

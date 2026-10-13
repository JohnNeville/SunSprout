---
sidebar_position: 1
title: Satellite Overview
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# SunSprout Satellite

:::info[Differential I2C Sensor Leaf Node]

The **SunSprout Satellite** is the dedicated remote sensor endpoint for the SunSprout ecosystem. It terminates a long differential-I2C cable run from the [SunSprout Hub](./overview.md), restores standard local I2C signaling, and monitors up to four capacitive soil-moisture probes plus a 1-Wire soil-temperature probe.

:::

<div style={{textAlign: 'center', margin: '2rem 0'}}>
  <img
    src={useBaseUrl('/img/satellite-board-top.png')}
    alt="SunSprout Satellite 3D top render hero image"
    style={{maxWidth: '85%', borderRadius: '8px', boxShadow: '0 4px 20px rgba(0,0,0,0.15)'}}
  />
</div>

## What is the Satellite?

The **SunSprout Satellite** functions as a remote garden/agricultural probe station. Where standard I2C buses degrade after a few tens of centimetres, the Satellite connects to the Hub over standard Category-rated twisted-pair patch cable using differential signaling. The PCA9615 datasheet quotes a 3 m cable at full speed, and longer runs at lower clock speeds; long runs have not been tested on this board.

At the endpoint, the board translates the differential clock and data signals back into standard 3.3V single-ended I2C, hosts an onboard 16-bit analog-to-digital converter (ADS1115) and a hardware 1-Wire master bridge (DS2482-100+), and distributes power and ground to local sensors.

<div style={{textAlign: 'center', margin: '2rem 0'}}>
  <img
    src={useBaseUrl('/img/satellite-board-bottom.png')}
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
| **Layer stackup** | 4 copper layers | Signals on the outer layers; the two inner layers carry ground and power zones |
| **Mounting** | 3× M2 non-plated holes | 3.0 mm corner inset at top; 1 mid-board support hole |
| **Primary interface** | 1× Amphenol RJHSE5380 | 8P8C (RJ45) jack with metal EMI shield |
| **Sensor ports** | 5× JST PH 2.0mm 3-pin | 4 moisture probe inputs + 1 temperature probe input |
| **Auxiliary ports** | 2.54mm headers, plus a Qwiic port | `J7` taps the cable's power and ground pairs, `J9` is the local 3.3V and ground header, and `J8` is a JST SH Qwiic / STEMMA QT port |

---

## Capabilities & Architecture

### 1. Differential I2C Bus Endpoint (PCA9615)
- **PCA9615DPZ** differential buffer translates `DSCL+`/`DSCL-` and `DSDA+`/`DSDA-` back into local `SCL_LOCAL` and `SDA_LOCAL`.
- **Fixed Onboard Termination**: Populated with matched resistor ladders (bias pull-ups to `RJ45_VCC_1`, line-matching resistors, and bias pull-downs to `RJ45_GND_1`) across both differential pairs. This ensures proper transmission line termination without loose plug-in resistors.
- **TVS / ESD Protection**: An onboard **USBLC6-4SC6** transient voltage suppressor array clamps all four differential lines against outdoor static and handling discharge.

### 2. High-Precision Soil Moisture Monitoring (ADS1115)
- **ADS1115IDGS** 16-bit 4-channel delta-sigma ADC with programmable gain amplifier and internal reference.
- Reads analog voltage outputs from up to **four** independent capacitive soil-moisture probes (e.g., DFRobot SEN0193 / Gravity interface).
- Four 3-pin vertical JST PH connectors (`J2`–`J5`) distribute `GND`, `SAT_3V3`, and signal lines (`MOIST1`–`MOIST4`).
- **Configurable I2C Address (`JP1`)**: 4-way solder jumper on the bottom side selects addresses `0x48`, `0x49`, `0x4A`, or `0x4B` (`0x48` default bridged).

### 3. Dedicated 1-Wire Temperature Bridge (DS2482-100+)
- Hardware I2C-to-1-Wire master bridge eliminates software bit-banging and timing jitter over long probe leads.
- Dedicated 3-pin vertical JST PH connector (`J6`) connects a waterproof DS18B20 digital temperature probe (`SAT_3V3`, `GND`, `ONEWIRE_DQ`).
- The DS2482's internal pull-up drives the 1-Wire line. A footprint for an optional external 4.7kΩ pull-up (`R9`) is left unpopulated.
- **Configurable I2C Address (`JP16`)**: Dual solder jumper selects addresses `0x18` (factory default), `0x19`, `0x1A`, or `0x1B`.

### 4. Power & Auxiliary Flexibility
- **Decoupled Power Architecture**: PCA9615 transceiver power (`VDDB`), the differential termination bias networks, and the ESD clamp array connect directly to the cable supply nets (`RJ45_VCC_1` / `RJ45_GND_1`). Those nets are joined to the local rails by `JP18` and `JP17`, which are bridged by default.
- **Bulk Cable Reservoir (`C1`)**: An onboard 22 µF bulk capacitor (`C1`) sits directly across `RJ45_VCC_1` and `RJ45_GND_1` right at the cable entry, dampening inductive cable ringing and buffering transient load steps. Dedicated 100 nF ceramic decoupling capacitors sit directly adjacent to every active IC pin.
- **Factory Default Operation (Zero Overhead)**: Pre-bridged cuttable solder jumpers `JP18` (`RJ45_VCC_1` $\leftrightarrow$ `SAT_3V3`) and `JP17` (`RJ45_GND_1` $\leftrightarrow$ `GND`) power the board directly from the Hub's regulated 3.3V rail over Pair 1 out of the box with zero external wiring.
- **Cable Power Breakout Header (`J7`)**: Exposes raw Pair 1 (`RJ45_VCC_1`, `RJ45_GND_1`) and Pair 3 (`RJ45_VCC_2`, `RJ45_GND_2`) conductors on a 2.54mm pitch header for secondary power injection or tapping.
- **Satellite Local Power Header (`J9`) & Long-Distance Regulation**: A 2-pin 2.54mm header (`SAT_3V3`, `GND`). On long cable runs where cable IR drop is non-negligible, users can slice `JP18` (and optionally `JP17`), send higher voltage (12V/24V) down Pair 3 (cut `JP2` and `JP3` on the hub first), and connect an off-the-shelf compact buck regulator between `J7` and `J9`.
- **Single-Cut Pull-Up Jumper (`JP11`)**: A custom 3-pad solder jumper with a single collinear cut channel allows disconnecting both local 4.7kΩ I2C pull-ups simultaneously with a single craft knife slice.
- **Power Status LED (`LED1`) & Cuttable Jumper (`JP19`)**: A green 0805 power indicator illuminates whenever `SAT_3V3` is energized. Solder jumper `JP19` allows severing the LED ground connection with a hobby knife to remove the LED's current draw in battery-powered applications.
- **Cable Shield Isolation (`JP13`)**: Cuttable solder jumper on the bottom side connects the RJ45 metal shield to `RJ45_GND_1` by default, allowing single-point grounding configurations when required.

---

## Further Reading
- [Dimensions & Mounting](./satellite-dimensions.md) — Exact outline, mounting hole locations, connector courtyard extents, and enclosure clearance guidance.
- [Hub Overview](./overview.md) — Main system controller, solar MPPT charger, and differential I2C driver.
- [Design Files](./design-files.md) — Schematic PDFs, Gerbers, and 3D CAD STEP models.

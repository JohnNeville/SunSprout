---
sidebar_position: 2
title: Satellite Pins & Jumpers
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# Satellite Pins & Jumpers

The **SunSprout Satellite** acts as a remote sensor endpoint terminating a differential-I2C cable run from the Hub. This page details all physical connector pinouts, sensor interfaces, and the hardware configuration solder jumpers on the bottom of the board.

---

## 1. Top View: Ports & Connectors

The top side exposes the primary **RJ45 differential bus interface (`J1`)**, **five JST PH 2.0mm sensor ports (`J2`–`J6`)**, and the **auxiliary power header (`J7`)**.

import InteractivePinout from '@site/src/components/InteractivePinout';

<InteractivePinout
  board="satellite"
  topSrc="/img/satellite-pinout-top.svg"
  bottomSrc="/img/satellite-pinout-bottom.svg"
/>


### Connector Pinout Tables

#### Primary RJ45 Interface (`J1`)
Terminates standard Category-rated twisted-pair patch cable from the Hub. Uses standard T568B pair pairings for differential integrity.

| RJ45 Pin | Net Name | Function / Description | Twisted Pair |
|:---:|---|---|---|
| **1** | `DSCL_N` | Differential I2C Clock (Negative) | Pair 2 (Orange/White) |
| **2** | `DSCL_P` | Differential I2C Clock (Positive) | Pair 2 (Orange) |
| **3** | `VCC_2` | Auxiliary Power Conductor (Pass-through to `J7`) | Pair 3 (Green/White) |
| **4** | `VCC_1` | Primary System Power (`SAT_3V3` feed via `JP14`) | Pair 1 (Blue) |
| **5** | `GND` | System Ground Return | Pair 1 (Blue/White) |
| **6** | `GND_2` | Auxiliary Ground Return (Pass-through to `J7`) | Pair 3 (Green) |
| **7** | `DSDA_N` | Differential I2C Data (Negative) | Pair 4 (Brown/White) |
| **8** | `DSDA_P` | Differential I2C Data (Positive) | Pair 4 (Brown) |
| **SH** | `SHIELD` | RJ45 Metal Chassis Shield (Tied to `GND` via `JP13`) | Outer Braid / Foil |

#### Soil Moisture Sensor Ports (`J2` – `J5`)
Vertical 3-pin JST PH (2.0mm pitch) connectors. Designed for capacitive analog moisture probes (e.g., Gravity / SEN0193).

| Connector | Pin 1 | Pin 2 | Pin 3 | ADC Channel | Notes |
|---|---|---|---|---|---|
| **`J2`** | `GND` | `SAT_3V3` | `MOIST1` | ADS1115 AIN0 | Moisture Probe Channel 1 |
| **`J3`** | `GND` | `SAT_3V3` | `MOIST2` | ADS1115 AIN1 | Moisture Probe Channel 2 |
| **`J4`** | `GND` | `SAT_3V3` | `MOIST3` | ADS1115 AIN2 | Moisture Probe Channel 3 |
| **`J5`** | `GND` | `SAT_3V3` | `MOIST4` | ADS1115 AIN3 | Moisture Probe Channel 4 |

#### 1-Wire Temperature Sensor Port (`J6`)
Vertical 3-pin JST PH connector for waterproof digital temperature probes (DS18B20). Driven by the onboard DS2482-100+ hardware I2C-to-1-Wire bridge with an onboard 4.7kΩ pull-up.

| Pin | Net Name | Function | Wire Color (Typical DS18B20) |
|:---:|---|---|---|
| **1** | `SAT_3V3` | Power Supply | Red (VCC) |
| **2** | `GND` | Ground Return | Black / Blue (GND) |
| **3** | `ONEWIRE_DQ` | 1-Wire Bidirectional Data | Yellow / White (DATA) |

#### Auxiliary Power & Tap Header (`J7`)
Standard 2.54mm (0.1") pitch 4-pin header for secondary power injection or downstream sensor tapping.

| Pin | Net Name | Description |
|:---:|---|---|
| **1** | `VCC_2` | Secondary power conductor from RJ45 pin 3 |
| **2** | `GND_2` | Secondary ground conductor from RJ45 pin 6 |
| **3** | `GND` | System digital and analog ground |
| **4** | `SAT_3V3` | Satellite local 3.3V power rail |

---

## 2. Bottom View: Hardware Jumpers & Addressing

The bottom side hosts the solder jumpers for configuring I2C addresses, terminating pull-ups, and managing power/ground routing.

<InteractivePinout
  board="satellite"
  src="/img/satellite-pinout-bottom.svg"
/>


### Jumper Configuration Matrix

#### `JP1`: ADS1115 I2C Address Selection (4-Way)
A 4-way solder jumper connecting the ADS1115 `ADDR` pin to select one of four unique I2C bus addresses.

| Configuration | Bridge Position | 7-bit Address | State |
|---|:---:|:---:|---|
| **Pads 1-2** | `ADDR` connected to `GND` | **`0x48`** | **Factory Default** (Pre-bridged with copper trace) |
| **Pads 1-3** | `ADDR` connected to `SAT_3V3` | **`0x49`** | Cut 1-2 trace; solder bridge 1-3 |
| **Pads 1-4** | `ADDR` connected to `SDA_LOCAL` | **`0x4A`** | Cut 1-2 trace; solder bridge 1-4 |
| **Pads 1-5** | `ADDR` connected to `SCL_LOCAL` | **`0x4B`** | Cut 1-2 trace; solder bridge 1-5 |

> [!TIP]
> To change the address, slice the thin copper trace bridging pads 1 and 2 with a hobby knife, then apply a small solder blob between pad 1 (common) and your chosen address pad.

#### `JP16`: DS2482-100+ 1-Wire Master Address Selection (Dual Jumper)
Controls the `AD0` and `AD1` address select pins of the I2C-to-1-Wire bridge.

| Address Bits | Bridge Selection | 7-bit Address | Notes |
|:---:|---|:---:|---|
| **`AD1=0, AD0=0`** | Pads 2A to GND (Pad 1) & 2B to GND (Pad 1) | **`0x18`** | **Factory Default** |
| **`AD1=0, AD0=1`** | Pad 2A to `3V3` (Pad 3) & 2B to GND (Pad 1) | **`0x19`** | Solder bridge to 3.3V |
| **`AD1=1, AD0=0`** | Pad 2A to GND (Pad 1) & 2B to `3V3` (Pad 3) | **`0x1A`** | Solder bridge to 3.3V |
| **`AD1=1, AD0=1`** | Pad 2A to `3V3` (Pad 3) & 2B to `3V3` (Pad 3) | **`0x1B`** | Both bridged to 3.3V |

#### `JP11`: Local I2C Pull-Up Resistor Disconnect
- **Purpose**: Disconnects the two onboard 4.7kΩ pull-up resistors on `SDA_LOCAL` and `SCL_LOCAL`.
- **Design**: Collinear single-cut 3-pad jumper.
- **Usage**: Both pull-ups are enabled by default. Slice across the center cut line with a single blade stroke to disable both local pull-ups if the bus master already provides adequate pull-up strength.

#### `JP14`: Power Source Routing
- **Pads 1-2 (Default)**: Satellite local power (`SAT_3V3`) is fed from RJ45 conductor 4 (`VCC_1`).
- **Pads 2-3**: Reroutes Satellite local power to feed from RJ45 conductor 3 (`VCC_2`). Useful when dedicating an auxiliary external supply to sensors.

#### `JP13`: Cable Shield Grounding
- **Default**: The metal shield of the RJ45 jack is tied directly to system `GND`.
- **Cuttable**: Slicing the copper trace between pads 1 and 2 isolates the cable shield from local satellite ground, enabling single-point earth grounding at the Hub end to prevent ground loops.

#### `JP15`: Auxiliary Ground Return Isolation
- **Default**: Auxiliary ground `GND_2` (RJ45 pin 6) is bridged to system `GND`.
- **Cuttable**: Slicing this bridge completely separates `GND_2` from system ground for isolated multi-supply operation.

---

## 3. Interactive BOM Viewer

For interactive probing and component highlighting:
- **[Open the Satellite Interactive BOM](pathname:///ibom-satellite/)** — Click any component to highlight its footprint, routing, and pin connections.

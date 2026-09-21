# Soil-temperature 1-Wire bridge — DS2482S-100+

| Item | Value |
|---|---|
| Reference | `U3` |
| Part | Analog Devices (Maxim) DS2482S-100+ |
| Package | SOIC-8 (3.9 x 4.9 mm, 1.27 mm pitch) |
| LCSC Part | `C143306` |
| Schematic sheet | `sheets/onewire_v1.kicad_sch` (Sheet 3) |

## Function

The DS2482S-100+ is an I2C-to-1-Wire master bridge. It converts standard I2C commands from the local I2C bus (`SDA_LOCAL`/`SCL_LOCAL`) into 1-Wire time slots on `ONEWIRE_DQ`, and reports the result back. It drives a waterproof DS18B20 probe for soil temperature, alongside the four analog moisture channels on the ADS1115.

Unlike the fixed-address DS2484, the DS2482S-100+ features two address pins (`AD0`, `AD1`) allowing four distinct I2C slave addresses (`0x18` to `0x1B`).

## Pin wiring

| Pin | Name | Net | Notes |
|---|---|---|---|
| 1 | `VCC` | `SAT_3V3` | Power supply rail, decoupled by `C5` (100nF 0603) |
| 2 | `IO` | `ONEWIRE_DQ` | 1-Wire data bus to connector `J6` and optional pullup `R9` |
| 3 | `GND` | `GND` | Ground return |
| 4 | `SCL` | `SCL_LOCAL` | I2C clock input from PCA9615 |
| 5 | `SDA` | `SDA_LOCAL` | I2C data input/output from PCA9615 |
| 6 | `~PCTLZ` | NC | Strong pull-up control for external MOSFET; left open/NC (internal pull-up used) |
| 7 | `AD0` | `AD0_SEL` | Address select bit 0, wired to solder jumper `JP16` |
| 8 | `AD1` | `AD1_SEL` | Address select bit 1, wired to solder jumper `JP17` |

## I2C Address Configuration

The DS2482S-100+ slave address is configured by strapping `AD1` and `AD0` to `GND` (logic 0) or `SAT_3V3` (logic 1).

Two 3-pad solder jumpers (`JP16` and `JP17`, footprint `Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm`) provide complete field address configurability:
- **Pin 1**: `GND`
- **Pin 2**: `AD0_SEL` (JP16) / `AD1_SEL` (JP17)
- **Pin 3**: `SAT_3V3`
- **Default state**: Pins 1-2 bridged with copper trace by default, tying both `AD0` and `AD1` to `GND`.

### Address Mapping Table

| AD1 (`JP17`) | AD0 (`JP16`) | I2C 7-bit Address | Binary | Default State |
|---|---|---|---|---|
| **0 (GND)** | **0 (GND)** | **`0x18`** | `0011000` | **Default (Bridged 1-2)** |
| 0 (GND) | 1 (3V3) | `0x19` | `0011001` | Cut JP16 (1-2), solder (2-3) |
| 1 (3V3) | 0 (GND) | `0x1A` | `0011010` | Cut JP17 (1-2), solder (2-3) |
| 1 (3V3) | 1 (3V3) | `0x1B` | `0011011` | Cut both (1-2), solder both (2-3) |

Because both jumpers default to bridged 1-2 (`GND`), the factory default I2C address is `0x18`, maintaining 100% software and firmware compatibility with existing DS2484/DS2482 drivers.

## Optional 1-Wire Passive Pull-up (`R9`, DNP)

The DS2482S-100+ includes an internal active pull-up with programmable slew-rate control. Under standard operating conditions with short to medium sensor cables, no external pull-up resistor is needed.

To accommodate extra-long field cable runs (which introduce higher line capacitance) or external test equipment, an unpopulated 0603 resistor footprint **`R9`** (`4.7kΩ`, `dnp=True`) is placed across `SAT_3V3` and `ONEWIRE_DQ`. 
- **Default state**: Unpopulated (DNP). The line is driven by the internal active pull-up of the DS2482.
- **Field population**: Soldering a standard 0603 resistor (typically 2.2kΩ to 4.7kΩ) onto the `R9` pads instantly connects the passive pull-up without requiring any trace cutting or separate jumper manipulation.

## Probe Connector (`J6`)

`J6` is a 3-pin JST PA-series connector (`SAT_3V3` / `GND` / `ONEWIRE_DQ`), matching the internal connector family used across the SunSprout ecosystem.
- Pin 1: `SAT_3V3` (Power to DS18B20)
- Pin 2: `GND` (Ground)
- Pin 3: `ONEWIRE_DQ` (1-Wire data bus)

See [Sensor connectors](sensor-connectors.md) for the harness wiring guidelines.

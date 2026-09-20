# Soil-moisture ADC — ADS1115

| Item | Value |
|---|---|
| Reference | `U2` |
| Part | Texas Instruments ADS1115IDGSR |
| Package | VSSOP-10 |
| Schematic sheet | `sheets/sensors_v1.kicad_sch` |

## Function

Four single-ended 16-bit channels, one per moisture probe. The part reads an analog voltage
from each probe and reports it over the local I2C bus (`SDA_LOCAL`/`SCL_LOCAL`) shared with
the PCA9615 and the DS2484.

## Power

`VDD` connects to `SAT_3V3`, with a 100nF decoupling capacitor (`C4`). No separate regulator
— see [the endpoint page](pca9615-i2c-endpoint.md#why-no-local-regulator) for why this board
runs everything off one rail.

## Address strapping

The `ADDR` pin sets the I2C address. TI's mapping: tied to `GND` gives `0x48`, `VDD` gives
`0x49`, `SDA` gives `0x4A`, `SCL` gives `0x4B`.

This board uses a custom 4-way solder jumper block (**`JP1`**, footprint `project:SolderJumper-4_P1.3mm_Bridged12_RoundedPad1.0x1.5mm`) so one bare board serves any of the four addresses:

| Position | Pins | Target Net | Address | Default State | Configuration Procedure |
|---|---|---|---|---|---|
| 1 | 1 ↔ 2 | `ADDR` ↔ `GND` | **`0x48`** | **Bridged / Closed** | Factory default (copper bridge on trace) |
| 2 | 1 ↔ 3 | `ADDR` ↔ `SAT_3V3` | **`0x49`** | Open | Cut bridge 1-2, solder bridge 1-3 |
| 3 | 1 ↔ 4 | `ADDR` ↔ `SCL_LOCAL` | **`0x4B`** | Open | Cut bridge 1-2, solder bridge 1-4 |
| 4 | 1 ↔ 5 | `ADDR` ↔ `SDA_LOCAL` | **`0x4A`** | Open | Cut bridge 1-2, solder bridge 1-5 |

Cut the factory bridge between pads 1 and 2 before bridging any alternative position. Bridge exactly one position at a time — shorting `ADDR` to two straps at once creates a bus conflict. Silkscreen clearly labels each position on the PCB with its resulting I2C address (`0x48`, `0x49`, `0x4A`, `0x4B`).

The DS2482S-100+ sharing this bus has addresses `0x18`–`0x1B` (default `0x18`) and never collides with any of the
four ADS1115 options (`0x48`–`0x4B`).

## Channel assignment

| Channel | Connector | Sensor |
|---|---|---|
| `AIN0` | `J2` | Moisture probe 1 |
| `AIN1` | `J3` | Moisture probe 2 |
| `AIN2` | `J4` | Moisture probe 3 |
| `AIN3` | `J5` | Moisture probe 4 |

`ALERT/RDY` is unused this revision.

## Calibration

Follow the same dry/wet reference-voltage method already documented for this hub-and-
satellite system in [Use Cases](../../../website/docs/use-cases.md) — record each probe's
voltage in dry air and in water individually, rather than assuming a shared value. Probes
vary enough that this matters.

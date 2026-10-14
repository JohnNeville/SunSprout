---
sidebar_position: 1
title: Overview
---

# SunSproutHub

:::warning[Prototype hardware, latest design not yet built]

A first hub was fabricated and tested from commit
[`1645733`](https://github.com/JohnNeville/SunSprout/commit/1645733). Testing found a few
issues. The current design files fix them, but that revision hasn't been built yet.

Until it has, you can build the tested prototype (`1645733`) with its known issues, or the
current design, which has the fixes but is untested on hardware. See
[Testing status](./testing-status.md) for what has been tested.

Treat this as an early design rather than a finished product, and review it yourself before
building one: errors in the charging or protection circuitry could damage a battery.

:::

A compact power-management and connectivity board built around the **ESP32-C5**. It takes power
from USB-C, a small DC/solar source, or a Li-ion/Li-Po battery, charges the battery with MPPT on
the solar input, regulates a 3.3V system rail, and exposes two independent I2C buses for onboard
and remote sensors.

## Physical

- 6-layer PCB.
- External connectors: USB-C power input, screw-terminal DC/solar input, JST battery input, two
  STEMMA QT ports, two 8P8C (RJ45-style) differential-I2C jacks, and two thermistor
  connectors. Headers for GPIO expansion and `VCC_2` injection are left unfitted. See
  [Connectors](./connectors.md).
- Two LEDs: charge status (driven by the charger) and a firmware-controlled status LED.
- Three buttons: reset, boot-mode, and a wake button that brings the charger out of ship mode,
  or, held for about 10 seconds, hard power-cycles the board.
- U.FL connector for an external antenna.

## Capabilities

### Compute & radio

| | |
|---|---|
| MCU | ESP32-C5-WROOM-1U |
| Wireless | Dual-band Wi-Fi 6, Bluetooth LE 5, 802.15.4. The SoC has a CAN FD controller, but no CAN transceiver is fitted. |
| Antenna | U.FL external connector |

### Power management

- **Li-ion/Li-Po charging** with JEITA temperature-qualified fast charge, using a thermistor
  input.
- **Source selection** between USB-C and the DC/solar input. Both can be connected at once.
- **Fuel gauge** for state of charge, with its own thermistor input.
- **MPPT on the solar input**, run by the charger itself with no firmware control loop.
- **Measurements** from the charger's 16-bit ADC: input voltage and current, battery voltage and
  current, and temperature, all readable over I2C.
- **Switched 3.3V user rail** that firmware can power down to save current.

### Protection

- Reverse-polarity protection on the battery and DC/solar inputs. USB-C doesn't need one.
- ESD/TVS protection on the 8P8C jacks' differential I2C lines and the USB-C data lines, and a
  TVS on USB `VBUS`.
- No dedicated ESD protection on the STEMMA QT ports, the expansion headers, the debug UART, the
  thermistor inputs or the USB `CC` lines. If you run a cable from one of them out of the
  enclosure, add protection at that end.
- Separate interrupt lines from the charger and the fuel gauge, each on its own GPIO.

## Interfaces

### I2C: two independent buses

- **Internal bus:** always on, for the charger and fuel gauge, plus the `J6` STEMMA QT port.
- **User bus:** switchable. It feeds a PCA9615 differential buffer that drives the two 8P8C
  jacks, plus the `J203` STEMMA QT port. The unfitted `J7` header also carries it.

The differential side is compatible with the
[SparkFun QwiicBus EndPoint](https://www.sparkfun.com/products/16988): same PCA9615 buffer and
8P8C pinout, so a standard Ethernet patch cable carries I2C to an EndPoint, and Qwiic/STEMMA QT
devices plug into it. This board has no termination resistors, so the far end must be an
EndPoint. See [Notes](./notes.md) for how the buses differ.

## Power

### Input

| Source | Connector | Notes |
|---|---|---|
| USB-C | `USBC1` | 5V only, no USB-PD. The charger's USB source detection is disconnected by default (`R9`/`R11` unpopulated), so the input limit comes from the hardware clamp; see [Notes](notes.md#the-charger-is-disconnected-from-the-usb-data-lines-by-default). |
| DC / small solar panel | `CN5` (screw terminal) | Can be connected at the same time as USB-C. |
| Battery | `J4` (JST PH, 2-pin) | Single cell. Check pack polarity against the silkscreen before connecting. |

### Charging summary

| | |
|---|---|
| Charger | BQ25798, buck-boost, dual-input |
| Cell configuration | **1S**, set in hardware by the `PROG` resistor |
| Chemistry | Li-ion / Li-Po and LiFePO4 |
| Input voltage, either source | **3.6 V to 24 V**; 30 V absolute maximum |
| Solar panel sizing | Up to **24 V**. Use the panel's cold-weather open-circuit voltage, which is above its rated Voc. |
| Input current limit | **About 2.0–2.1 A** (worst case 2.27 A), set in hardware. Firmware cannot exceed it. |
| Charge current | Firmware-set over I2C. Defaults to **1 A**. **Do not exceed 2 A.** |
| Solar tracking | Open-circuit-voltage MPPT, run by the charger |
| Source selection | Both inputs may be connected at once; the charger selects between them |
| Temperature qualification | JEITA, via a thermistor on `J302`. **With no thermistor fitted the charger suspends charging** unless `ts_ignore: true` is set. |

### Output

| Rail | Voltage | Description |
|---|---|---|
| System rail (always on) | 3.3V | MCU, the internal I2C bus, and `J6`. |
| User rail (switched) | 3.3V | The differential buffer and `J203`. Firmware-controlled, off at power-up. |

### Charging & power management

- **Input current limit.** About 2.0 A from USB-C and 2.1 A from a higher-voltage input, up to
  2.27 A worst case. It limits the combined draw of the sources, not the battery charge rate. The
  charger sets it once at power-up from whichever source is present. Details are in the
  [charger notes](https://github.com/JohnNeville/SunSprout/blob/main/docs/hub/modules/bq25798-charger.md).
- **Charging is enabled in hardware** (`CE` is tied to ground), but without a thermistor the
  charger will not charge. Fit a 103AT-type 10 kΩ NTC on `J302`, or set `ts_ignore: true` in the
  firmware, which turns temperature protection off.
- **Charge current** is set over I2C and returns to 1 A on power-up, a watchdog timeout or a
  register reset. Set it for your pack's capacity, and **never above 2000 mA**: it has no
  hardware ceiling, and in buck mode it can exceed the input current.
- **Ship mode and shutdown** open the ship FET `Q3` to disconnect the battery. They can only be
  entered with no adapter present; with USB or solar connected the charger ignores them.
- **`SW3` (WAKE).** Holding it about 1 s wakes the charger from ship mode; a brief tap does
  nothing. Holding it about 10 s hard power-cycles the board, with no firmware or I2C needed.
  The reset restarts the MCU and both 3.3V rails, and the fuel gauge too unless its `FG_PWR`
  jumper is set to the battery. It does not restart the charger itself.
- **Firmware must set `SFET_PRESENT`** (`REG14`, bit 7) at start-up. While it is 0, the charger
  locks out ship mode and shutdown.

### Current consumption

Not yet characterized. Measurements will be added here once testing is complete.

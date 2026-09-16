---
sidebar_position: 1
title: Overview
---

# SunSproutHub

:::warning[Work in progress — never fabricated or tested]

No physical board exists yet. Everything on this site is verified in software only: ERC and DRC
pass, values and pin assignments are checked against manufacturer datasheets, and the
fabrication outputs generate cleanly. Nothing has been powered on or measured.

The design is published at this stage to gather feedback before a fabrication run. Treat it as
an untested design rather than a finished product, and review it yourself before building one —
errors in the charging or protection circuitry could damage a battery.

:::

A compact power-management and connectivity board built around the **ESP32-C5**, designed to
take power from USB-C, a small DC/solar source, or a Li-ion/Li-Po battery — charge the
battery with true maximum-power-point tracking on the solar input, and regulate a clean 3.3V
system rail — while exposing two independent I2C buses for onboard and remote sensors.

Every IC's datasheet-required external components are drawn directly into the schematic rather
than treated as black-box breakout modules, and the board is hand-routed rather than
auto-generated.

## Physical

- 6-layer PCB (F.Cu, 4× inner, B.Cu).
- 10 external connectors: USB-C power input, screw-terminal DC/solar input, JST battery input,
  two STEMMA QT ports, two 8P8C (RJ45-style) differential-I2C jacks, two field-terminable
  thermistor connectors, and two GPIO expansion headers you fit yourself. See
  [Connectors](./connectors.md) for the full list.
- Two LEDs: a charge-status LED driven by the charger, and a firmware-controlled status LED.
- Three buttons: reset, boot-mode, and a wake button that brings the charger out of ship mode —
  or, held for ~10 seconds, hard power-cycles the whole board.
- U.FL external antenna connector (module-side), for installations where the onboard antenna
  isn't sufficient.

## Capabilities

### Compute & radio

| | |
|---|---|
| MCU | ESP32-C5-WROOM-1U |
| Wireless | Dual-band Wi-Fi 6, Bluetooth 5, 802.15.4, CAN FD |
| Antenna | U.FL external connector (module variant) |

### Power management

- **Li-ion/Li-Po battery charging** with JEITA temperature-qualified fast charge, via an
  onboard charge-temperature thermistor input.
- **Automatic source arbitration** between USB-C and the DC/solar input — both can be
  connected simultaneously; the charger ORs them into a single charge-path rail.
- **Fuel gauge** for state-of-charge tracking, with its own independent battery-temperature
  thermistor input (kept separate from the charger's, since each IC applies its own excitation
  to whatever's wired to its thermistor pin).
- **True MPPT on the solar input**, performed by the charger itself. It periodically samples
  the panel's open-circuit voltage and regulates to the corresponding maximum-power point,
  autonomously — no firmware control loop and no separate monitor IC involved.
- **Measurement from the charger's integrated 16-bit ADC** — input voltage, input current,
  battery voltage, battery current and temperature, all readable over I2C. Between that and the
  fuel gauge, every rail is covered without a dedicated power-monitor part.
- **Switched 3.3V "user" rail**, independent from the always-on system rail, that firmware can
  power down to save current when the secondary I2C bus and its downstream devices aren't
  needed.

### Other protections

- Reverse-polarity protection on both the battery and DC/solar inputs, sized to each source's
  expected voltage range. USB-C doesn't need one — it's a keyed, spec-defined connector.
- **ESD/TVS protection on the ports designed to carry a cable off-board**: the four
  differential I2C lines on the two 8P8C jacks, and the USB-C data lines. The USB `VBUS` rail
  gets its own TVS as well.

  The remaining connectors have **no** dedicated ESD parts — both STEMMA QT ports, the two GPIO
  expansion headers and the debug UART on them, both thermistor inputs, and the USB `CC` lines.
  Those are intended for sensors sitting close by inside the same enclosure. If you run a cable
  from one of them out of the enclosure, add protection at that end.
- Hardware alert/interrupt lines from the charger and the fuel gauge are wired to their own
  separate GPIOs, so firmware can react to a fault without polling — and without having to
  interrogate both devices to work out which one raised it.

## Interfaces

### I2C — two independent buses

- **Internal bus** — always-on, dedicated to the board's own power-management ICs (charger and
  fuel gauge) plus a local STEMMA QT connector for directly-attached sensors.
- **User bus** — switchable, feeding a PCA9615 differential I2C buffer that drives two 8P8C
  jacks, plus a second, separate STEMMA QT connector.

The differential side is wired to be compatible with the [SparkFun QwiicBus —
EndPoint](https://www.sparkfun.com/products/16988): same PCA9615 buffer, same 8P8C pinout, so
a standard Ethernet patch cable carries I2C from this board to an EndPoint, and Qwiic/STEMMA QT
devices plug into the EndPoint at the far end. That's how you get sensors metres away from the
hub instead of centimetres.

This board takes the pass-through role, so it carries **no termination resistors** on the
differential lines — the EndPoint at the far end provides them. It therefore needs to connect
to an EndPoint rather than acting as the end of a chain itself.

These buses are deliberately kept apart — see [Notes](./notes.md) for why that matters when
wiring things up.

### Connectors

See the dedicated [Connectors](./connectors.md) page for the full list with mating-part
guidance.

## Power

### Input

| Source | Connector | Notes |
|---|---|---|
| USB-C | `USBC1` | Standard 5V USB-C power/data input. The charger detects BC1.2, HVDCP and non-standard adapters. |
| DC / small solar panel | `CN5` (screw terminal) | Wide-range DC input suitable for a small solar panel; can be connected at the same time as USB-C. |
| Battery | `J4` (JST PH, 2-pin) | Single cell. Double-check pack polarity against the board's silkscreen before connecting — JST-PH battery polarity isn't universally standardized across cable vendors. |

### Charging summary

| | |
|---|---|
| Charger | BQ25798, buck-boost, dual-input |
| Cell configuration | **1S**, set in hardware by the `PROG` resistor at power-on |
| Chemistry | Li-ion / Li-Po and LiFePO4 (the fuel gauge carries profiles for both) |
| Input voltage, either source | **3.6 V to 24 V** for a valid input; 30 V absolute maximum |
| Practical solar ceiling | **24 V**, the charger's own recommended maximum — the input protection no longer sets a lower one. The reverse-polarity FET on that input is self-biased, so the full input voltage appears across its ±20 V gate in normal operation as well as under a reversed source; a Zener gate clamp (`D2`) holds that within rating across the whole range. Size a panel by its cold-weather open-circuit voltage, which rises above the rated Voc. See [input protection](https://github.com/JohnNeville/SunSprout/blob/main/docs/hub/modules/input-protection.md). |
| Input current limit | **~2.0–2.1 A**, set in hardware by a resistor divider. Firmware cannot exceed it. The exact value tracks the charger's REGN rail, which is itself input-dependent — see below. |
| Charge current | Firmware-set over I2C. Defaults to **1 A**; **do not exceed 2 A** (see below). |
| Solar tracking | Autonomous open-circuit-voltage MPPT, run by the charger itself |
| Source arbitration | Both inputs may be connected at once; the charger's internal mux selects between them |
| Measurement | Integrated 16-bit ADC: input voltage/current, battery voltage/current, temperature |
| Temperature qualification | JEITA, via a thermistor on `J302` (not fitted — see [Connectors](./connectors.md)). **With no thermistor fitted the charger reads "too cold" and suspends charging** until firmware sets `TS_IGNORE`; see below. |

### Output

| Rail | Voltage | Description |
|---|---|---|
| System rail (always-on) | 3.3V | Powers the MCU, the internal power-management I2C bus, and its STEMMA QT connector (`J6`). |
| User rail (switched) | 3.3V | Powers the I2C differential buffer and its STEMMA QT connector (`J203`); firmware-controlled, defaults OFF at power-up. |

### Charging & PMU behavior

- **Input current limit: roughly 2.0 A to 2.1 A**, hardware-set by the `R302`/`R303` divider on
  the charger's `ILIM_HIZ` pin. This is an analog ceiling the charger enforces regardless of what
  firmware writes to the corresponding register. It caps the combined draw from whichever source
  (USB-C, DC/solar, or both at once) is feeding the charge path — it isn't the battery's charge
  rate.

  It is not a single fixed number, because the divider is referenced to `REGN`, and `REGN` itself
  depends on the input voltage. The charger computes the clamp as
  `V(ILIM_HIZ) = 1 V + 800 mΩ × I`, and the divider ratio is 130 k / (110 k + 130 k) = 0.542:

  | Input | `REGN` (typical) | Resulting limit |
  |---|---|---|
  | USB-C at 5 V | 4.8 V | **2.00 A** |
  | Solar or DC at 15 V | 5.0 V | **2.14 A** |
  | Across the full `REGN` spec, 4.6 V to 5.2 V | | **1.87 A to 2.27 A** |

  The divider was sized for the 5 V case. On a high-voltage input the ceiling sits about 7% above
  2 A, and worst-case silicon reaches 2.27 A — budget the copper for the top of that range, not
  for 2.00 A. The charger latches this clamp from an ADC reading taken at power-on before the
  converter starts switching, so whichever source is present at power-up sets it for that
  session.
- **Charging is enabled in hardware, but not currently sufficient on its own.** The charger's
  `CE` pin is tied to ground, so nothing has to be written to start a charge. The charger's own
  protections (OVP, OCP, thermal shutdown, UVLO) apply throughout.

  As built, though, a board with no firmware running **will not charge**, because of the
  thermistor. `J302` ships unpopulated, and the `TS` divider (`R305` 5.23 kΩ to `REGN`, `R306`
  30.1 kΩ to ground) then sits at 85.2% of `REGN`. Every JEITA cold threshold is below that —
  the 0 °C threshold is 73.3% of `REGN`, and even the −20 °C OTG threshold is 80% — so the
  charger reads a battery colder than its cold cutoff and suspends charging.

  The network is correct once a thermistor is present: a 103AT-type 10 kΩ NTC at 25 °C puts the
  divider at 58.9% of `REGN`, mid-window. **Fit one** — it is what the charger's datasheet
  expects, and the only arrangement that gives real JEITA temperature protection.

  To run without one, firmware must set `TS_IGNORE` (register `REG18`, bit 0), which tells the
  charger to treat the temperature as always acceptable. The bit defaults to 0 and TI lists it
  as reset by the watchdog and by a register reset; this board's firmware disables the watchdog,
  so in practice only the register-reset control clears it. That route gives up temperature
  qualification entirely, and the ESPHome driver does not currently expose the bit.

  There is deliberately no fixed resistor standing in for the thermistor. It would make the
  charger read a permanent 25 °C and report that as a real measurement, which is a worse
  failure than having no reading at all.
- **Battery charge current is firmware-configured** over I2C, and resets to that 1A default on
  power-up, on a watchdog timeout, and on a register reset. Program a charge current
  appropriate to your specific pack's capacity before relying on fast charging.
- **Firmware must not set the charge current above 2000mA.** Unlike the input limit, the charge
  current has no hardware ceiling, and in buck mode it can exceed the input current — so a
  higher setting can push the charge-side copper past its rating.
- **Ship mode and a true hardware power cycle**, via an external ship FET (`Q3`) on the
  charger's `SDRV` gate-driver pin. The FET sits in series in the battery path, so the charger
  can physically disconnect the pack from the system rail. That gives three states beyond normal
  operation: *ship mode* (FET off, I2C still alive — for shipping and storage), *shutdown* (FET
  off, I2C down, only an adapter brings it back), and a *system power reset* that drops the FET
  for ~350ms and actively pulls the `SYS` rail down before restoring it.
- **Holding `SW3` (WAKE) for about 10 seconds hard power-cycles the board.** This runs entirely
  inside the charger — no working firmware, no I2C — which makes it the recovery path when the
  MCU is wedged. A shorter press (~1s) just wakes the charger out of ship mode.

  Two caveats worth knowing. The reset cycles the `SYS` rail, so it restarts the MCU, both 3.3V
  rails and everything downstream of them — but *not* the charger itself (it's the thing
  performing the reset) and *not* the fuel gauge, which is deliberately wired to the pack side
  of the ship FET so it keeps coulomb-counting straight through. And since neither I2C device
  loses power, the reset can't unstick a hung I2C slave; that still needs the usual nine-clock
  recovery sequence in firmware.
- **Firmware must set the charger's `SFET_PRESENT` bit** (`REG14`, bit 7) during init. It
  defaults to 0, and while it's 0 the charger locks out every ship-FET mode above — the board
  behaves as though no FET were fitted.

### Current consumption

Not yet characterized — measurements will be added here once bring-up testing is complete.

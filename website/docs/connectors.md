---
sidebar_position: 4
title: Connectors
---

# Connectors

Ten external connectors, deliberately spread across distinct connector families by role —
so a solar source can't be physically mis-plugged into the battery input, and the two
temperature-probe inputs use a field-terminable connector rather than requiring a
pre-terminated probe.

The thermistor inputs use JST **PA**, not the JST **PH** of the battery input `J4`, precisely
so a cell can never be plugged into a `TS` sense pin. Both are 2.0 mm pitch; the housings do
not intermate.

| Ref | Type | Purpose | Mating part |
|---|---|---|---|
| `USBC1` | USB-C receptacle | USB-C power input | Any standard USB-C cable |
| `CN5` | 2.54mm screw terminal | DC / small solar panel input | Bare-wire or ferrule termination |
| `J4` | JST PH, 2-pin | Battery input | Single-cell Li-ion/Li-Po pack with a JST-PH cable — check polarity against the silkscreen before connecting |
| `J6` | JST SH, 4-pin (STEMMA QT) | Internal I2C bus — for sensors that should share the always-on power-management bus | Any STEMMA QT / Qwiic cable |
| `J203` | JST SH, 4-pin (STEMMA QT) | User I2C bus — for sensors on the switched, differential-buffer-side bus | Any STEMMA QT / Qwiic cable |
| `J201` / `J202` | 8P8C (RJ45-style) | Differential I2C — connects to a [SparkFun QwiicBus EndPoint](https://www.sparkfun.com/products/16988) for remote sensors | Standard Ethernet patch cable |
| `J2` | 2.54mm header (not fitted) | Optional external supply for the `VCC_2` rail on the 8P8C jacks — see [Notes](./notes.md#vcc_2-is-a-separate-cuttable-power-rail-on-the-8p8c-jacks) | Standard 2.54mm header strip, hand-soldered |
| `J302` | JST PA, 2-pin (`S02B-PASK-2`) | Charger thermistor input | Semitec 103AT-11 NTC thermistor (10kΩ @ 25°C), mounted on the battery pack — see [below](#terminating-your-own-thermistor-probe) |
| `J401` | JST PA, 2-pin (`S02B-PASK-2`) | Fuel-gauge thermistor input | A **second, separate** Semitec 103AT-11 NTC thermistor (10kΩ @ 25°C), also mounted on the pack |
| `J7` / `J8` | 2.54mm header (not fitted) | Spare/expansion GPIO breakout, plus the debug UART | Standard 2.54mm header strip, hand-soldered |

## Why two separate thermistors (J302 and J401)

The charger and fuel gauge each apply their own excitation/bias to whatever's wired to their
thermistor pin. Sharing a single NTC between both active bias circuits would give both ICs a
bad reading, so each gets its own thermistor — both mounted at the same physical location on
the battery cell.

## Terminating your own thermistor probe

`J302` and `J401` are JST PA 2-pin side-entry headers (`S02B-PASK-2`). To make up a probe cable:

| Part | Number | Notes |
|---|---|---|
| Housing | `PAP-02V-S` | 2-circuit, latching |
| Crimp contact | `SPHD-001T-P0.5` | AWG 28–22, insulation O.D. 0.76–1.5 mm |
| Thermistor | Semitec `103AT-11` | 10 kΩ @ 25 °C, B25/85 = 3435 K, 600 mm insulated lead |

The PA series is rated −40 °C to +105 °C and latches. Both matter for a probe that lives on a
battery pack: an intermittent `TS` connection reads as out-of-range and suspends charging, and
the connector should not be the narrowest part of the temperature range it is qualifying.

**Do not substitute the Semitec 103AT-2.** It is the same element electrically, but it ships as
a bare bead on 17 mm solid 42-alloy leads — too short for a crimp barrel, not ductile enough to
form a gas-tight crimp, and with no insulation for the support wings to grip. If you only have
103AT-2 parts, solder them to a 24–26 AWG stranded pigtail, heatshrink the joint, and crimp the
pigtail instead.

**A 3D-printer hotend thermistor will not work here**, despite the familiar-looking connector.
Those are 100 kΩ, B ≈ 3950 parts; the `R305`/`R306` divider is sized for 10 kΩ. Borrow the
connector ecosystem, not the part.

## Why two STEMMA QT ports

`J6` and `J203` sit on genuinely independent I2C buses (see [Pins & Signals](./pinout.md)) —
one always-on and dedicated to the board's own power-management ICs, the other switched and
shared with the differential-buffer path. Plugging a sensor into one vs. the other has real
electrical consequences; see [Notes](./notes.md).

## Controls

Three buttons, all on the top side:

| Ref | Label | Function |
|---|---|---|
| `SW1` | RESET | Pulls the MCU's `EN` pin low. Resets the board. |
| `SW2` | BOOT | Hold during a reset to enter firmware download mode. |
| `SW3` | WAKE | Pulls the charger's `QON` pin low — it does not go to the MCU. The hold time picks the action: a short press (~1s) wakes the charger from ship mode, bringing the board back after it has shut down to preserve the battery. **Holding for ~10 seconds triggers a full system power reset** — the charger opens the ship FET, actively pulls the `SYS` rail down, and restores it after ~350ms, restarting the MCU and both 3.3V rails. That path is pure hardware, so it works even with no firmware running. The charger and the fuel gauge stay powered through it. |

## Headers you fit yourself

`J7` and `J8` are on the board but **not factory-fitted**. They're excluded from both the bill
of materials and the pick-and-place file, so the assembler neither sources nor places them —
the pads are simply left bare for you to solder a standard 2.54mm header strip onto.

They break out the free GPIOs and the debug UART. Several of the exposed pins are strapping
pins, so check [Pins & Signals](./pinout.md) before loading one down at reset.

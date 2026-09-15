---
sidebar_position: 3
title: Connectors
---

# Connectors

Ten external connectors, deliberately spread across distinct connector families by role —
so a solar source can't be physically mis-plugged into the battery input, and the two
temperature-probe inputs use a field-terminable connector rather than requiring a
pre-terminated probe.

| Ref | Type | Purpose | Mating part |
|---|---|---|---|
| `USBC1` | USB-C receptacle | USB-C power input | Any standard USB-C cable |
| `CN5` | 2.54mm screw terminal | DC / small solar panel input | Bare-wire or ferrule termination |
| `J4` | JST PH, 2-pin | Battery input | Single-cell Li-ion/Li-Po pack with a JST-PH cable — check polarity against the silkscreen before connecting |
| `J6` | JST SH, 4-pin (STEMMA QT) | Internal I2C bus — for sensors that should share the always-on power-management bus | Any STEMMA QT / Qwiic cable |
| `J203` | JST SH, 4-pin (STEMMA QT) | User I2C bus — for sensors on the switched, differential-buffer-side bus | Any STEMMA QT / Qwiic cable |
| `J201` / `J202` | 8P8C (RJ45-style) | Differential I2C — connects to a [SparkFun QwiicBus EndPoint](https://www.sparkfun.com/products/16988) for remote sensors | Standard Ethernet patch cable |
| `J302` | JST ZH, 2-pin | Charger thermistor input | 10kΩ @ 25°C NTC thermistor (103AT-2 type), mounted on the battery pack |
| `J401` | JST ZH, 2-pin | Fuel-gauge thermistor input | A **second, separate** 10kΩ @ 25°C NTC thermistor (103AT-2 type), also mounted on the pack |
| `J7` / `J8` | 2.54mm header (not fitted) | Spare/expansion GPIO breakout, plus the debug UART | Standard 2.54mm header strip, hand-soldered |

## Why two separate thermistors (J302 and J401)

The charger and fuel gauge each apply their own excitation/bias to whatever's wired to their
thermistor pin. Sharing a single NTC between both active bias circuits would give both ICs a
bad reading, so each gets its own thermistor — both mounted at the same physical location on
the battery cell.

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

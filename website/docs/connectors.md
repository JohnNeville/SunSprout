---
sidebar_position: 4
title: Connectors
---

# Connectors

The external connectors, plus the unfitted headers, are deliberately
spread across distinct connector families by role —
so a solar source can't be physically mis-plugged into the battery input, and the two
temperature-probe inputs use a field-terminable connector rather than requiring a
pre-terminated probe.

The thermistor inputs use JST **PA**, not the JST **PH** of the battery input, precisely
so a cell can never be plugged into a `TS` sense pin. Both are 2.0 mm pitch; the housings do
not intermate.

| Connector | Type | Purpose | Mating part |
|---|---|---|---|
| USB-C port | USB-C receptacle | Power input, firmware flashing and log output | Any standard USB-C cable |
| Solar input (`SOLAR`) | 2.54mm screw terminal | DC / small solar panel input. Pin 1 is `+` (marked on the silkscreen), pin 2 is ground | Bare-wire or ferrule termination |
| Battery (`BATT +` / `BATT −`) | JST PH, 2-pin | Single-cell battery input. Pin 1 is `BATT+`, pin 2 is `BATT−` | Single-cell Li-ion/Li-Po/LiFePO4 pack with a JST-PH cable. Check polarity against the silkscreen before connecting |
| STEMMA QT port (`Qwiic Sys`) | JST SH, 4-pin | Internal I2C bus (3.3 V from the always-on rail), for sensors that should share the always-on power-management bus | Any STEMMA QT / Qwiic cable |
| STEMMA QT port (`Qwiic User`) | JST SH, 4-pin | User I2C bus (3.3 V from the switched rail), for sensors on the switched bus that also feeds the differential buffer | Any STEMMA QT / Qwiic cable |
| Two 8P8C jacks (`J201`, `J202`) | 8P8C (RJ45-style) | Differential I2C, to a [SparkFun QwiicBus EndPoint](https://www.sparkfun.com/products/16988) for remote sensors | Standard Ethernet patch cable |
| `VCC_2` injection header (`VCC_2 INJ`; not fitted) | 2.54mm header | Optional external supply for the `VCC_2` rail on the 8P8C jacks (pin 1 `VCC_2`, pin 2 its return). See [Notes](./notes.md#vcc_2-is-a-separate-cuttable-power-rail-on-the-8p8c-jacks) | Standard 2.54mm header strip, hand-soldered |
| Charger thermistor (`CHGR_TS`) | JST PA, 2-pin (`S02B-PASK-2`) | Charger thermistor input (pin 1 ground, pin 2 the charger's `TS` sense node) | Semitec 103AT-11 NTC thermistor (10kΩ @ 25°C), mounted on the battery pack. See [below](#terminating-your-own-thermistor-probe) |
| Fuel-gauge thermistor (`FG_TS`) | JST PA, 2-pin (`S02B-PASK-2`) | Fuel-gauge thermistor input (pin 1 the gauge's 2.5 V bias output, pin 2 its `TS` sense node) | A **second, separate** Semitec 103AT-11 NTC thermistor (10kΩ @ 25°C), also mounted on the pack |
| Expansion headers (`J7`, `J8`; not fitted) | 2.54mm header | Spare/expansion GPIO breakout, plus the debug UART | Standard 2.54mm header strip, hand-soldered |

To see where each connector sits on the board, open the [interactive BOM](pathname:///ibom/).
Names in parentheses are printed on the board.

## Pinouts

Pin 1 is the pin marked on the board's silkscreen. Check it against the silkscreen before
connecting anything.

**Battery (JST PH)** and **solar input (screw terminal)**

| Pin | Battery | Solar input |
|:---:|---|---|
| 1 | `BATT+` (`VBAT_RAW`) | `+` DC input |
| 2 | `BATT−` (battery return) | Ground |

**`Qwiic Sys`** (internal bus) and **`Qwiic User`** (user bus) STEMMA QT ports (JST SH, Qwiic order)

| Pin | `Qwiic Sys` | `Qwiic User` |
|:---:|---|---|
| 1 | Ground | Ground |
| 2 | 3.3 V (`3V3_SYS`, always on) | 3.3 V (`3V3_USER`, switched) |
| 3 | `SDA_INT` | `SDA_USER` |
| 4 | `SCL_INT` | `SCL_USER` |

**Differential I2C jacks `J201` / `J202` (8P8C, same pinout on both)**

| Pin | Signal | Pin | Signal |
|:---:|---|:---:|---|
| 1 | `DSCL−` | 5 | Ground |
| 2 | `DSCL+` | 6 | `VCC_2` return (`GRN_N`) |
| 3 | `VCC_2` (`GRN_P`) | 7 | `DSDA−` |
| 4 | `VCC_1` (`3V3_USER`) | 8 | `DSDA+` |

**`VCC_2 INJ` header (unfitted):** pin 1 `VCC_2`, pin 2 its return.

**Expansion headers `J7` and `J8` (unfitted, 9 pins each)**

| Pin | `J7` | `J8` |
|:---:|---|---|
| 1 | `3V3_USER` | `3V3_USER` |
| 2 | Ground | Ground |
| 3 | GPIO0 | GPIO26 |
| 4 | GPIO1 | GPIO25 |
| 5 | GPIO7 | `U0TXD` (GPIO11) |
| 6 | `SDA_USER` | `U0RXD` (GPIO12) |
| 7 | `SCL_USER` | GPIO24 |
| 8 | Ground | GPIO27 |
| 9 | `3V3_USER` | GPIO5 |

Several of these GPIOs are strapping pins. See [Pins & Signals](./pinout.md) before loading them
at reset. The thermistor connectors are described below.

## Why two separate thermistors

The charger and fuel gauge each apply their own excitation/bias to whatever's wired to their
thermistor pin. Sharing a single NTC between both active bias circuits would give both ICs a
bad reading, so each gets its own thermistor — both mounted at the same physical location on
the battery cell.

The two connectors are not wired the same way. Pin 1 of the `CHGR_TS` connector is ground, but pin 1 of the `FG_TS` connector is
the gauge's own 2.5 V bias output, so never short `FG_TS` pin 1 to ground. The thermistor itself
has no polarity.

## Terminating your own thermistor probe

The `CHGR_TS` and `FG_TS` connectors are JST PA 2-pin side-entry headers (`S02B-PASK-2`). To make up a probe cable:

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
Those are 100 kΩ, B ≈ 3950 parts; the charger's thermistor divider is sized for 10 kΩ. Borrow the
connector ecosystem, not the part.

## Why two STEMMA QT ports

`Qwiic Sys` and `Qwiic User` sit on genuinely independent I2C buses (see [Pins & Signals](./pinout.md)) —
one always-on and dedicated to the board's own power-management ICs, the other switched and
shared with the differential-buffer path. Plugging a sensor into one vs. the other has real
electrical consequences; see [Notes](./notes.md).

## Controls

Three buttons, all on the top side:

| Silkscreen label | Function |
|---|---|
| `RESET` | Pulls the MCU's `EN` pin low. Resets the board. |
| `BOOT` | Hold during a reset to enter firmware download mode. |
| `WAKE` | Pulls the charger's `QON` pin low — it does not go to the MCU. The hold time picks the action: a short press (~1s) wakes the charger from ship mode, bringing the board back after it has shut down to preserve the battery. **Holding for ~10 seconds triggers a full system power reset** — the charger opens the ship FET, actively pulls the `SYS` rail down, and restores it after ~350ms, restarting the MCU and both 3.3V rails. That path is pure hardware, so it works even with no firmware running. The charger and the fuel gauge stay powered through it. |

## Headers you fit yourself

The expansion headers `J7` and `J8` are on the board but **not factory-fitted**. They're excluded from both the bill
of materials and the pick-and-place file, so the assembler neither sources nor places them —
the pads are simply left bare for you to solder a standard 2.54mm header strip onto.

They break out the free GPIOs and the debug UART. Several of the exposed pins are strapping
pins, so check [Pins & Signals](./pinout.md) before loading one down at reset.

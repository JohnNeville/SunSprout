---
sidebar_position: 3
title: Pins & Signals
---

# Pins & Signals

The ESP32-C5-WROOM-1U module's pins are split between board-managed functions (things the
board itself wires up — buttons, I2C buses, alerts) and pins left free for your own use.

## Pinout diagram

import InteractivePinout from '@site/src/components/InteractivePinout';

<InteractivePinout
  board="hub"
  topSrc="/img/pinout-top.svg"
  bottomSrc="/img/pinout-bottom.svg"
/>


Auto-generated vector pinout diagrams (`tools/generate-docs-assets.sh`) showing all board peripherals, expansion headers (`J7`, `J8`), Stemma QT ports, buttons, strapping pins, and bottom-side hardware test points with color-coded signal tags. Use the **Top (Signals)** and **Bottom (Test Points)** toggle in the diagram toolbar to inspect both layers.

For something more useful when you're actually holding the board: **[open the interactive
BOM](pathname:///ibom/)** — hover or click any reference designator to highlight
it on the board (and vice versa), search by part/value, and toggle top/bottom layers. Generated
by [InteractiveHtmlBom](https://github.com/openscopeproject/InteractiveHtmlBom) from the same
`.kicad_pcb` source as everything else on this page.

## GPIO map

| GPIO | Function | Category | Strapping pin? | Pull resistor | Notes |
|---|---|---|---|---|---|
| CHIP_PU/EN | Reboot button (SW1) | Fixed | No (dedicated EN pin) | R1 10kΩ pull-up to 3V3_SYS + C2 1µF | Reset button |
| GPIO0 | LP_GPIO0 (Expansion) | Free | No (not a strap on ESP32-C5) | — | Routed to expansion header J7 pin 3. Low-power domain, deep-sleep wake capable |
| GPIO1 | Unused | Free | No | — | Routed to expansion header J7 |
| GPIO2 | SDA_INT — **`LP_I2C_SDA`** | Assigned | No | R20 4.7kΩ pull-up to 3V3_SYS | Internal I2C data. Fixed-function LP pin; see below. |
| GPIO3 | SCL_INT — **`LP_I2C_SCL`** | Assigned | Yes — SDIO sampling/clock-edge select | R21 4.7kΩ pull-up to 3V3_SYS | Internal I2C clock. Fixed-function LP pin; see below. |
| GPIO4 | FG_ALERT (fuel gauge) | Assigned | No — deep-sleep wake capable | R401 10kΩ pull-up to 3V3_SYS | Fuel-gauge alert, wake-capable. Kept on its own net, separate from the charger's interrupt |
| GPIO5 | Unused | Free | No | — | Routed to expansion header J8 |
| GPIO6 | LED1_CTRL (status LED) | Assigned | No | — (push-pull output) | Drives LED1 through R3 (120Ω) |
| GPIO7 | Unused | Free | Yes — paired SDIO edge-select strap | — | Routed to expansion header J7 |
| GPIO8 | CHG_INT (charger interrupt) | Assigned | No | R24 10kΩ pull-up to 3V3_SYS | Short interrupt pulse; recoverable via I2C polling |
| GPIO9 | SDA_USER (user I2C data) | Assigned | No | R201 4.7kΩ pull-up to 3V3_USER | Feeds the I2C differential buffer + external STEMMA QT port |
| GPIO10 | SCL_USER (user I2C clock) | Assigned | No | R202 4.7kΩ pull-up to 3V3_USER | Paired with GPIO9 |
| GPIO11 | U0TXD | Fixed | No | — | Debug console UART, also routed to J8 |
| GPIO12 | U0RXD | Fixed | No | — | Debug console UART, also routed to J8 |
| USB_D− | USB_DN | Fixed | No | R7, 22Ω series | Native USB peripheral. The series resistor Espressif recommends. |
| USB_D+ | USB_DP | Fixed | No | R8, 22Ω series | Native USB peripheral. Shared with the charger's BC1.2 detection input via R9/R11, which ship as cuttable 0Ω bridges. See [Notes](notes.md#the-charger-taps-the-usb-data-lines-through-cuttable-bridges). |
| GPIO15 | Reserved — in-package PSRAM chip-select | Reserved | No | — | Consumed inside the module, not by this board. See below. |
| GPIO16–22 | Not exposed | Reserved | — | — | Internal to the module, not broken out |
| GPIO23 | EN_3V3_USER | Assigned | No | R23 100kΩ pull-down to GND | Enables the switched 3V3_USER rail; defaults OFF at power-up |
| GPIO24 | Unused | Free | No | — | Routed to expansion header J8; free for reassignment |
| GPIO25 | Unused | Free | Yes — boot-mode strap, floating default | — | Routed to expansion header J8 |
| GPIO26 | Unused | Free | Yes — boot-mode strap, floating default | — | Routed to expansion header J8 |
| GPIO27 | Unused | Free | Yes — boot-mode strap | — | Routed to expansion header J8 |
| GPIO28 | Boot/flash button (SW2) | Fixed/Strap | Yes — ROM download boot strap | Internal pull-up + R4 10kΩ pull-up to 3V3_SYS | Primary ESP32-C5 boot strap. Hold SW2 low during reset (SW1) to enter download mode. Also routed to TP18 |

## Why the internal bus is on GPIO2/GPIO3

The ESP32-C5 has **one** general-purpose I2C controller and **one** low-power controller
(datasheet §4.2.1.3: *"ESP32-C5 has an I2C and an LP I2C bus interface"*). Two simultaneous I2C
buses therefore need both.

The HP controller routes to any pin through the GPIO matrix, but `LP_I2C` does not — it is
hard-wired through the LP IO MUX to **GPIO2 (`LP_I2C_SDA`) and GPIO3 (`LP_I2C_SCL`)**. So the
internal bus sits on exactly those two pins, and the user bus takes the HP controller on
GPIO9/GPIO10. Put the internal bus anywhere else and both buses contend for the single HP
controller, which won't build.

That pinning also buys something: the LP peripherals and LP CPU stay powered in deep sleep, so
the charger and fuel gauge can be polled while the main CPU is off, rather than waking the
whole chip to read a register.

## Free IO

GPIO0, GPIO1, GPIO5, GPIO7, GPIO24, GPIO25, GPIO26, and GPIO27 are unused and available for
your own projects. All of them are routed out to the two expansion headers (`J7` and `J8`),
which aren't fitted at the factory — solder a 2.54mm header strip to use them.

Note the strapping-pin caveats on GPIO7, GPIO25, GPIO26, and GPIO27 above: the
MCU samples these at reset to select a boot mode, so check what each strap does before loading
one down at boot. (GPIO28 is dedicated to the SW2 download boot button with an internal and external pull-up).

## Special-function pins

CHIP_PU/EN, GPIO28, GPIO11–12 and the native USB pins are committed to fixed board functions —
reset, boot select (SW2), debug UART and native USB respectively — and aren't available for
reassignment. (GPIO0 is in the low-power domain `LP_GPIO0` and is broken out on header J7 pin 3).

**GPIO15 is a module-level reservation, not a board one.** This design uses the
`ESP32-C5-WROOM-1U-N8R8` variant, where the `R8` denotes 8 MB of PSRAM packaged inside the
module alongside the 8 MB of flash. That PSRAM's chip-select is wired to GPIO15 *within the
module*, so the pin never reaches the module's edge as a usable IO no matter what the host
board does. This board leaves it unconnected, and the firmware doesn't enable the PSRAM either
— so it is neither routed nor in use here. A module variant without in-package PSRAM would free
the pin, at the cost of the PSRAM.

## Hardware Test Points (Bottom View)

The bottom side of the SunSproutHub PCB breaks out key electrical nodes as circular surface-mount test pads for multimeter and oscilloscope probing during bringup and verification:

| Test Point | Signal / Net | Function & Description | Category |
|---|---|---|---|
| **TP17** | `U0TXD` | ESP32-C5 primary UART console transmit | Debug / Serial |
| **TP16** | `U0RXD` | ESP32-C5 primary UART console receive | Debug / Serial |
| **TP18** | `BOOT` (`BTN1_NODE`) | Download boot mode strap (GPIO28) | Control / Strap |
| **TP19** | `RESET` (`RESET_NODE`) | Hardware reset line (`CHIP_PU` / `EN`) | Control / Power |
| **TP2** | `SDA_INT` | Internal `LP_I2C` bus data line (GPIO2) | Internal I2C |
| **TP3** | `SCL_INT` | Internal `LP_I2C` bus clock line (GPIO3) | Internal I2C |
| **TP8** | `3V3_SYS` | Always-on 3.3V system supply from buck converter | Power Rail |
| **TP7** | `3V3_USER` | Switched 3.3V power rail feeding external sensors and J8 | Power Rail |
| **TP12** | `SYS_RAIL` | Main system power bus from BQ25798 NVDC charger | Power Rail |
| **TP14** | `VBAT` | Raw 1S battery cell positive terminal voltage | Battery |
| **TP15** | `VBAT_PRO` | Protected battery voltage after discharge protection FET | Battery |
| **TP9** | `VBUS_INTERNAL` | USB-C and Solar input power rail (5V–20V) | Power Rail |
| **TP13** | `REGN_RAIL` | 5V internal gate drive and bootstrap LDO rail | Power Rail |
| **TP10** | `TS_NODE` (`CHGR_TS`) | Battery thermistor analog sensing node for BQ25798 charger | Thermistor |
| **TP11** | `FG_TS_NODE` (`FG_TS`) | Independent battery temperature sensor for BQ34Z100 fuel gauge | Thermistor |
| **TP4, TP5, TP6** | `GND` | System reference ground test pads | Ground |

### Hardware Solder Jumpers (Bottom)

- **`JUMP_CHGR_GND2` (USB D+/D- Conditioning)**: 3-pad jumper between `CHGR_USB_DN`, `GND`, and `CHGR_USB_DP`. Allows configuring USB data lines for standalone charger BC1.2 port detection.
- **`JP2` (`GRN_P -> 3v3`)**: Connects the status LED anode circuit to `3V3_USER`.
- **`JP3` (`GRN_N -> GND`)**: Solder jumper in series with the status LED cathode ground return. Slice to disable front-panel LED power consumption for ultra-low-power deployments.

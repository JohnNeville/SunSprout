# MCU module — ESP32-C5-WROOM-1U

| Item | Value |
|---|---|
| Reference | `U1` |
| Part | Espressif ESP32-C5-WROOM-1U-N8R8-V1.2 |
| Schematic sheet | Main sheet |

## Function

The module holds the MCU, the radio, the flash memory and the PSRAM. It runs the firmware. It
controls the charger, the fuel gauge and the user rail over I2C and GPIO.

## Why this module

The board is a hub for remote sensors. Its main interface is the differential I2C bus. It is not
a general GPIO breakout board, so a large GPIO count is not the deciding requirement.

An earlier design used a larger module from a different family. That module had many more GPIO
pins. Those pins were not load-bearing for this design.

Three properties decided the change:

- **Dual-band Wi-Fi 6 and CAN FD.** These extend what the board can do in the field.
- **PSRAM headroom.** The `N8R8` variant has 8 MB of flash and 8 MB of PSRAM.
- **An exposed U.FL antenna connector.** This was the deciding factor.

### Why the -1U variant

The `-1U` variant brings the antenna connector out on the module itself. The standard variant
has its antenna inside the module shield, with no way to bring it out from the host board.

An outdoor solar installation often needs an external antenna. A module with a sealed internal
antenna cannot meet that need.

## Power

| Reference | Value | Function |
|---|---|---|
| `C1` | 1 µF | Decoupling on the 3.3 V supply pin. |

The module runs from the always-on 3V3_SYS rail. It therefore stays on while the board charges.

## Reset and boot

| Reference | Value | Function |
|---|---|---|
| `SW1` | — | Reset button. Pulls the `EN` pin low. |
| `R1` | 10 kΩ | Pull-up on the `EN` pin to the 3.3 V rail. |
| `C2` | 1 µF | Filter capacitor on the `EN` pin. |
| `SW2` | — | Boot-mode button. Pulls GPIO0 low. |
| `R2` | 10 kΩ | Pull-up on GPIO0 to the 3.3 V rail. |
| `C21` | 1 µF | Filter capacitor on GPIO0. |

The `EN` filter uses 10 kΩ with 1 µF. These are the values that the module manufacturer
specifies in its hardware design guidelines. An earlier revision used 100 nF here. The change to
1 µF matched the specified time constant.

Hold GPIO0 low during a reset to enter download mode.

## Assigned pins

| GPIO | Net | Function |
|---|---|---|
| `EN` | `RESET_NODE` | Reset button `SW1`. |
| GPIO0 | `BTN1_NODE` | Boot-mode button `SW2`. |
| GPIO1 | `SCL_INT` | Internal I2C clock. `R21` pulls it up with 4.7 kΩ. |
| GPIO2 | `SDA_INT` | Internal I2C data. `R20` pulls it up with 4.7 kΩ. |
| GPIO4 | `FG_ALERT` | Alert output from the fuel gauge. |
| GPIO6 | `LED1_CTRL` | Status LED, through `R3` (120 Ω). |
| GPIO8 | `CHG_INT` | Interrupt output from the charger. `R24` pulls it up with 10 kΩ. |
| GPIO9 | `SDA_USER` | User I2C data. `R201` pulls it up with 4.7 kΩ. |
| GPIO10 | `SCL_USER` | User I2C clock. `R202` pulls it up with 4.7 kΩ. |
| GPIO11 | `U0TXD` | Debug console transmit. |
| GPIO12 | `U0RXD` | Debug console receive. |
| GPIO23 | `EN_3V3_USER` | Enables the switched user rail. `R23` pulls it down with 100 kΩ. |
| USB D+, USB D- | `ESP_USB_DP`, `ESP_USB_DN` | Native USB port. |

The alert lines use separate GPIO pins. The charger and the fuel gauge therefore report faults
independently. Firmware does not have to poll both devices to find which one raised an alert.

## Free pins

GPIO3, GPIO5, GPIO7, GPIO24, GPIO25, GPIO26, GPIO27 and GPIO28 have no board function. They go
to the two expansion headers, `J7` and `J8`. The debug UART pins also go to `J8`.

Both headers are DNP. The board ships without them. Solder a header to use these pins.

### Strapping pins

Some free pins are strapping pins. The MCU samples them at reset to select a boot mode. Check
what each strap does before you load it at reset time.

GPIO28 has a 10 kΩ pull-up, `R4`, to the 3.3 V rail. This reinforces the default state of that
strap.

The expansion headers expose several strapping pins. This follows the precedent of the module
manufacturer's own development board, which does the same.

### Reserved pin

GPIO15 is the chip-select line of the in-package PSRAM on this module variant. It is not
available for any other use. The pin is left unconnected on this board.

## Antenna tuning placeholder — C3

| Item | Value |
|---|---|
| Reference | `C3` |
| Footprint | 0603 |
| Status | **DNP. The board ships without this capacitor.** |

`C3` is a placeholder on GPIO28. It has no value. The board ships without it.

The footprint stays available for tuning after the first build. Do not fit a part here without a
measurement that shows the need.

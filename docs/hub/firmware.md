# Firmware

The board runs ESPHome. The configuration is in [`firmware/`](../../firmware/).

This page explains the firmware decisions. It does not explain how to flash a board. See
[firmware/README.md](../../firmware/README.md) for that.

## Why ESPHome

The board is a sensor hub. Its job is to read remote sensors and report them to a home
automation system. ESPHome does that work already. It also gives OTA updates, a Home
Assistant integration and a deep-sleep scheduler.

An earlier plan used bare ESP-IDF. That plan needed its own code for each of those features.

## Where the code lives

The configuration is split into two parts.

| Part | Location |
|---|---|
| Chip drivers for the BQ25798 and the BQ34Z100 | A separate repository, [esphome-bq-drivers](https://github.com/JohnNeville/esphome-bq-drivers) |
| Board configuration | `firmware/sunsprout-hub.yaml` in this repository |

The two chips are stock Texas Instruments parts. The drivers talk to the chips. They do not
know about this board. A separate repository lets other designs use them. It also matches the
layout that an ESPHome upstream contribution needs.

The board configuration stays here. It holds the values that the hardware sets: the pin map,
the charge limits and the sense resistor value. Those values belong next to the pages that
explain them.

## The charge voltage

The charger reads the `PROG` resistor at power-on. `R301` selects a 1S cell. The charger
then sets its battery voltage limit to **4.2 V**.

A LiFePO4 cell charges to **3.65 V**. 4.2 V damages it.

The configuration declares the cell chemistry. The driver derives the charge voltage limit
from that chemistry. It writes the limit during setup. It writes the limit again after a
register reset.

The firmware does not give a control for the charge voltage. A user must not be able to
change a limit that protects the cell. The chemistry sets the limit, and nothing else does.

This is the most important firmware requirement on the board.

## The two I2C buses

The MCU has one general-purpose I2C controller. It also has one low-power I2C controller.
The low-power controller works only on GPIO2 for `SDA` and GPIO3 for `SCL`.

The board connects `SDA_INT` to GPIO2. The board connects `SCL_INT` to GPIO3. Both match.

The internal bus therefore uses the low-power controller. The user bus uses the
general-purpose controller. Both buses work at the same time.

An earlier revision connected `SCL_INT` to GPIO1. That pin does not match. Neither bus could
then use the low-power controller, and the two buses had to share the one general-purpose
controller. Only one bus worked. The design moved the net to GPIO3 to correct this.

**Do not move the `SDA_INT` or `SCL_INT` nets.** The low-power controller accepts no other
pin pair. Any other pin returns the board to the earlier fault.

GPIO3 is also `MTDI`. `MTDI` is a strapping pin. It selects the SDIO sampling edge together
with GPIO25. Its default state is floating. The bus pull-up resistor sets the strap to 1 at
reset.

This board does not use the SDIO interface. The strap value therefore has no effect. GPIO2
is the `MTMS` strapping pin and carries the same pull-up, so the design already accepts this
condition.

## The watchdog

The charger has an I2C watchdog. The default period is 40 seconds. When the watchdog
expires, the charger returns the charge current, the charge voltage and several other
registers to their `PROG` defaults.

For this board, that means the charge voltage returns to 4.2 V.

The firmware disables the watchdog. A watchdog that can damage the cell gives no safety.

## The charge current limit

`R302` and `R303` limit the input current to 2.00 A. That limit is analog. Firmware cannot
exceed it.

The charge current has no equivalent hardware limit. In buck mode, the charge current can be
larger than the input current. The board copper carries 2 A.

The firmware therefore applies its own ceiling of 2000 mA. The driver clamps every write to
that value. See [Battery charger](modules/bq25798-charger.md).

## Maximum power point tracking

The charger has a VOC-based MPPT algorithm. The charger stops switching at an interval. It
measures the open-circuit input voltage. It then sets its input voltage limit to a fraction
of that voltage.

The firmware enables this algorithm. It does not track the maximum power point itself.

An earlier design used a separate power monitor IC and a firmware loop. The loop read the
input voltage and wrote a new limit. The charger does the same work in hardware. The design
removed the monitor IC, and the firmware does not need the loop.

## The ship FET and the reboot button

The board fits a ship FET, `Q3`, on the `SDRV` pin. See
[Battery charger](modules/bq25798-charger.md).

**The firmware must set the `SFET_PRESENT` bit.** The power-on value of this bit is 0. While
the bit is 0, the charger locks the `SDRV_CTRL` bits and the `EN_BATOC` bit. Ship mode,
shutdown mode and the system power reset are then unavailable.

The board configuration sets `ship_fet_present: true`. The driver writes the bit during
setup. The driver also rejects a configuration that asks for these controls without the
flag. A control that does nothing is worse than no control.

The firmware offers the system power reset as a **Power Cycle Board** button. The charger
opens `Q3` for about 350 ms. Everything on the `SYS` rail loses power. The board reboots.

The charger waits about 10 seconds before it acts, by default. The board configuration sets
`ship_fet_action_delay: false` to remove this wait.

Two parts keep their supply through the reset. The charger performs the reset itself. The
fuel gauge sits on the `VBAT_PROTECTED` net, on the pack side of `Q3`. The firmware therefore
cannot use this reset to clear a stuck I2C slave. Neither device loses power. Use the
nine-clock recovery sequence on `SCL` for that fault.

`SW3` does the same reset in hardware. Hold the button for about 10 seconds. This path needs
no firmware, so it works when the MCU has stopped.

## The battery over-current backstop

Setting `SFET_PRESENT` also unlocks the `EN_BATOC` bit. The board configuration sets
`battery_ocp: true`.

The charger then opens `Q3` when the discharge current passes the `IBAT_OCP` threshold. This
threshold is fixed at about 9.3 A. The board copper carries 2 A.

This protection is therefore a backstop against a short circuit. It does not protect the
copper. The charge-current ceiling does that.

## The fuel gauge chemistry

The gauge holds a chemistry profile in its data flash. A LiFePO4 cell needs a 400-series
profile.

**Firmware cannot load a chemistry profile.** The `CHEM_ID` command reports the active
profile. Texas Instruments gives no I2C command to change it. The profile comes from
bqStudio and an EV2400 programmer, with a `.bqz` chemistry file. This happens once, at the
bench.

Until then, the state of charge is wrong.

The firmware reads the chemistry ID at start-up. It compares the ID against the configured
value. It reports an error when the two do not match. This makes the problem visible.

## Other gauge settings

The firmware can write every other gauge setting. It writes the design capacity, the design
energy, the cell count, the pack configuration bits and the sense resistor calibration.

The sense resistor value is 10 mΩ. See [Fuel gauge](modules/bq34z100-fuel-gauge.md). The
firmware converts this value into the gauge's two calibration constants.

Data flash has a limited write count. The firmware reads each value before it writes. It
writes only a value that differs. It then reads the value back to confirm the write.

These writes are off by default. Set `apply_configuration: true` to turn them on.

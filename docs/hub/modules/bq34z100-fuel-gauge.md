# Fuel gauge — BQ34Z100

| Item | Value |
|---|---|
| Reference | `U3` |
| Part | Texas Instruments BQ34Z100PWR-G1 |
| Package | TSSOP-14 |
| Schematic sheet | `sheets/bq34z100_fuel_gauge_v2.kicad_sch` |

## Function

The fuel gauge measures the charge that flows into and out of the battery. It reports the state
of charge over the internal I2C bus.

## Why this part

The board must support a LiFePO4 battery. LiFePO4 cells have a different voltage curve from
standard lithium-ion cells. A gauge must hold a chemistry profile that matches the cell.

An earlier design used a smaller gauge from the same family. That part holds only lithium-ion
profiles for 4.2 V, 4.35 V and 4.4 V cells. It has no LiFePO4 profile at all. This was a hard
blocker, so the design changed the part.

The BQ34Z100 supports lithium-ion and LiFePO4 chemistries. It also had much better stock at the
assembly house than the other candidates.

## Sense resistor and filter

| Reference | Value | Function |
|---|---|---|
| `R404` | 10 mΩ, 1206 | Current-sense (shunt) resistor, in the battery return path next to `J4` |
| `R402` | 100 Ω, 0603 | `SRN` series filter resistor, on the `R404` ground-side pad |
| `R403` | 100 Ω, 0603 | `SRP` series filter resistor, on the `R404` battery-side pad |
| `C403` | 100 nF, 0402 | Differential filter capacitor across `SRP` and `SRN` |

`R404` is the current-sense resistor. It was `R404` in earlier revisions. It sits in series between
the true negative terminal of the battery and system ground. The full charge current and the full
discharge current flow through it.

The gauge measures the voltage across `R404` with its `SRP` and `SRN` pins. This is a low-side
measurement. The earlier gauge used an integrated high-side shunt inside the IC instead. The
change to an external low-side resistor was part of the part change. The datasheet recommends a
5 mΩ to 20 mΩ resistor and allows ±125 mV across the pins, so 10 mΩ gives a ±12.5 A input range.

### Sense filter

Each sense input goes through a 100 Ω resistor, with one 100 nF capacitor across the two inputs.
This is the differential low-pass filter that the datasheet recommends for the coulomb-counter
inputs (section 10.2.3 and Figure 10-2). The resistors carry only the nanoamp-level sense current,
not the battery current. The gauge's effective input resistance is about 2.5 MΩ, so 100 Ω adds
negligible error. A resistor of 100 kΩ here would add a gain error of several percent.

Layout rules that apply:

- Place `R404` close to the battery connector, in the direct battery return path.
- Take the `SRP` and `SRN` taps from the two pads of `R404` itself, from the side of each pad away
  from where the load current leaves. This is the Kelvin connection. Keep the tap copper separate
  from the high-current return path.
- Place `R402` and `R403` symmetrically about `R404`, with traces of equal length and width.
- Place `C403` as close as possible to the `SRP` and `SRN` pins, on the gauge side of the resistors.

A Kelvin connection measures the voltage at the resistor pads themselves. It excludes the
voltage drop in the tracks that carry the current. Without it the gauge reads a current that is
too high.

## Support components

| Reference | Value | Pin | Function |
|---|---|---|---|
| `C401` | 100 nF | `REGIN` | Decouples the input of the internal LDO. The datasheet requires it close to the pin. |
| `C402` | 1 µF | `REG25` | Decouples the output of the internal 2.5 V LDO. `REG25` also biases the external thermistor. |
| `R401` | 10 kΩ | `P2` (ALERT) | Pull-up for the alert output. The IC drives the pin low to assert the alert. |

`C401` uses the same 100 nF 0402 part as the rest of the board. An earlier revision used a 0603
part here for no recorded reason. The battery voltage never exceeds about 3.65 V, so the smaller
package loses no voltage margin. One shared part also avoids a second feeder-loading fee.

## Battery temperature sensing

The `TS` pin connects to `J401`, a JST PA 2-pin side-entry header (`S02B-PASK-2`). It accepts an
external 103AT-type 10 kΩ NTC thermistor — this board specifies the Semitec **103AT-11**.

The `REG25` rail biases the thermistor. The IC has an internal pull-down for this pin, so the
board needs no external bias resistor. The charger needs an external divider for its own
thermistor, because it works differently.

Each IC applies its own bias to its thermistor pin. Two ICs cannot share one thermistor, because
each bias would corrupt the other reading. The board therefore has two thermistor connectors.
Mount both thermistors at the same place on the cell.

This approach keeps the temperature reading in hardware. Firmware does not have to measure the
temperature elsewhere and then write it into the gauge over I2C.

## Alert routing

The alert output connects to the `FG_ALERT` net. The net connects to GPIO4 on the MCU.

`R401` pulls the net up to the 3V3_SYS rail. An earlier revision pulled it up to the `REG25`
rail. That created two problems. It allowed current to flow back into `REG25`, and the 2.5 V
level gave too little margin for the MCU input. The pull-up now uses the 3.3 V rail.

## Power and battery connection

| Pin | Net | Notes |
|---|---|---|
| `REGIN` (6) | `FG_REGIN` | Powers the gauge (2.7 V to 4.5 V). Selected by the `FG_PWR` jumper. |
| `CE` (5) | `FG_REGIN` | Chip enable. It must be high, so it follows `REGIN`. |
| `BAT` (4) | `VBAT_PROTECTED` | Measures the battery voltage through the gauge's internal 5:1 divider. |

`C401` (100 nF) decouples `REGIN` next to pin 6. The current measurement happens at `R404` on the
low side.

### FG_PWR jumper

`FG_PWR` is a three-pad solder jumper on the bottom of the board. The centre pad is `FG_REGIN`.

| Setting | Source | Use |
|---|---|---|
| Pads 1-2 bridged (default) | `3V3_SYS` | Gauge works with or without a battery. |
| Cut 1-2, bridge 2-3 | `VBAT_PROTECTED` | Gauge keeps counting through ship mode and power resets. |

**`3V3_SYS` (default).** The gauge is powered whenever the board is. The charger removes `3V3_SYS`
in ship mode, shutdown and the system power reset, so the gauge restarts afterwards, does not
count current while off, and may need to relearn the pack. It draws nothing in ship mode.

**`VBAT_PROTECTED`.** The gauge counts through every charger low-power state, but draws a small
standing current from the battery, which ship mode cannot remove. **Always fit a battery in this
setting.** Without one the gauge has no supply, is disabled, and holds the internal I2C clock
low, which blocks the charger as well. The first prototype (commit `1645733`) was wired this
way.

The gauge keeps counting through deep sleep in either setting, because the 3.3 V system rail
stays on. Disconnect the pack at `J4` for storage.

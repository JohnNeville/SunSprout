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

## Sense resistor — R60

| Item | Value |
|---|---|
| Reference | `R60` |
| Value | 10 mΩ |
| Package | 1206 |
| Location | Main sheet, next to the battery connector `J4` |

`R60` is the current-sense resistor. It sits in series between the true negative terminal of the
battery and system ground. The full charge current and the full discharge current flow through
it.

The gauge measures the voltage across `R60` with its `SRP` and `SRN` pins. This is a low-side
measurement. The earlier gauge used an integrated high-side shunt inside the IC instead. The
change to an external low-side resistor was part of the part change.

Two layout rules apply:

- Place `R60` close to the battery connector, in the direct battery return path.
- Route `SRP` and `SRN` as a Kelvin connection to the two pads of the resistor. Keep these
  tracks separate from the high-current return path.

A Kelvin connection measures the voltage at the resistor pads themselves. It excludes the
voltage drop in the tracks that carry the current. Without it the gauge reads a current that is
too high.

### Why the sense resistor is on the main sheet

The sense resistor belongs to the fuel gauge circuit, but it does not sit on the fuel gauge
sheet. It sits on the main sheet, because it belongs in the physical battery return path next to
`J4`. A reader who examines only the fuel gauge sheet does not see it.

### Ground isolation — NT4

`NT4` is a net tie. It joins the `SRN` sense net to the general ground pour at exactly one
point. That point is at `R60`.

This keeps the Kelvin sense path separate from the ground pour. A direct connection to the pour
would let return current change the measured voltage.

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

The `TS` pin connects to `J401`. `J401` accepts an external 103AT-type 10 kΩ NTC thermistor.

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

## Battery connection

The `BAT`, `CE` and `REGIN` pins all connect to the `VBAT` net. No series shunt sits between the
battery and these pins. The current measurement happens at `R60` on the low side instead.

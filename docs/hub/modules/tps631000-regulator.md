# Buck-boost regulator — TPS631000

| Item | Value |
|---|---|
| Reference | `U4` |
| Part | Texas Instruments TPS631000DRLR |
| Package | SOT-583, 8 pin |
| Schematic sheet | `sheets/TPS631000_PowerRegulation_v2.kicad_sch` |

## Function

The regulator makes the 3.3 V system rail. It takes its input from the SYS rail of the charger.
The 3V3_SYS rail supplies the MCU, the internal I2C bus and the `J6` port.

## Why a buck-boost and not a buck

The SYS rail voltage follows the battery and the input source. With a LiFePO4 cell the SYS rail
can fall below 3.3 V. A buck converter cannot raise its output above its input. It would drop
the 3.3 V rail as the cell discharges.

A buck-boost converter holds 3.3 V above and below that point. The buck-boost is therefore a
requirement of the LiFePO4 cell, and not a preference.

## Why the fixed-output variant

This part sets its output with an external resistor divider. It has no I2C interface for output
trim. A programmable variant exists.

The design checked whether a programmable output was needed. The reference firmware for a
similar board never changed the regulator output over I2C in practice. A resistor-set output is
therefore a complete match for the need. The input range of 1.6 V to 5.5 V also matches the
original requirement.

## Feedback divider

| Reference | Value | Position |
|---|---|---|
| `R15` | 510 kΩ | Top leg, from the output |
| `R16` | 91 kΩ | Bottom leg, to ground |

The feedback reference is 0.5 V. The divider gives an output of 0.5 x (1 + 510 / 91) = 3.302 V.

The datasheet sets a maximum value for the bottom resistor. The 91 kΩ value stays about 9 percent
below that ceiling. A larger value would raise the impedance of the feedback node and make it
more sensitive to noise.

## Power inductor — L2

`L2` is 1 µH. Its saturation current is 6.5 A. Its DC resistance is 16 mΩ.

The part is not one of the four listed in Table 7-2 of the datasheet, but it beats all of them.
The strongest entry there, the Murata DFE252012P-1R0M=P2, is rated 4.3 A with 42 mΩ in the same
2.5 × 2.0 × 1.2 mm body. `L2` has half the DC resistance and half again the saturation margin at
the same size and price.

Section 7.2.2.2 asks for a saturation current 20 percent above the calculated peak. At the worst
case for this board — boost mode, 3.0 V in, 3.3 V out, 1.5 A out — Equation 3 gives a peak of
about 1.9 A, so the requirement is roughly 2.3 A. The converter cannot exceed this by much in
any case: section 6.1 sets the Q1 peak current limit at typically 3 A, which caps the inductor
current in hardware. The 6.5 A rating covers that ceiling more than twice over.

An earlier revision used a small-signal multilayer inductor rated at 50 mA. The rating was 40
times too small for this circuit. Such a part saturates under load. A saturated inductor loses
its inductance, so the current rises quickly and the converter cannot regulate. The design
replaced it with a true power inductor.

## Capacitors

| Reference | Value | Function |
|---|---|---|
| `C13` | 10 µF | Input capacitor at `VIN`. |
| `C14` | 47 µF | Output capacitor at `VOUT`. This matches the value that the datasheet recommends. |

The design removed a second, 1 nF output capacitor (`C29`) that an earlier revision placed between
`U4` and `C14`. The datasheet asks for a single output capacitor placed as close as possible to
`VOUT`/`PGND` (Section 7.4.1); the extra part only pushed `C14` further from the IC and was not a
datasheet requirement.

## Enable pin

The `EN` pin connects directly to the SYS rail, which is also the input. The regulator therefore
starts as soon as it has an input voltage.

A GPIO cannot control this pin. The regulator makes the rail that powers the MCU, so the MCU
cannot exist before the regulator runs. This connection is deliberate.

## Mode pin

The `MODE` pin connects to ground. This selects power-save mode.

In power-save mode the converter pulses only as often as the load requires. This raises the
efficiency at light load. The output ripple increases. A battery-powered board spends most of
its time at light load, so this trade is correct here.

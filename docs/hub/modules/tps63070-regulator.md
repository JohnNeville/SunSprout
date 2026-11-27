# Buck-boost regulator — TPS63070

| Item | Value |
|---|---|
| Reference | `U4` |
| Part | Texas Instruments TPS63070RNMR |
| Package | VQFN-HR, 15 pin, 2.5 × 3 mm |
| Schematic sheet | `sheets/TPS631000_PowerRegulation_v2.kicad_sch` |

The board layout still carries the earlier regulator. Boards up to now are fitted with a TPS631000.

## Function

The regulator makes the 3.3 V system rail. It takes its input from the SYS rail of the charger.
The 3V3_SYS rail supplies the MCU, the internal I2C bus and the `J6` port.

## Why a buck-boost and not a buck

The SYS rail voltage follows the battery and the input source. With a LiFePO4 cell the SYS rail
can fall below 3.3 V. A buck converter cannot raise its output above its input. It would drop
the 3.3 V rail as the cell discharges.

A buck-boost converter holds 3.3 V above and below that point. The buck-boost is therefore a
requirement of the LiFePO4 cell, and not a preference.

## Why this part: the input rating

The charger's Minimum System Voltage register accepts values up to 16 V. A wrong setting
therefore puts that voltage on the SYS rail. The earlier TPS631000 is rated for 6 V at most.
Firmware once allowed the full register range, and one prototype was destroyed during solar
testing in a way that matches this fault. The cause was not proven.

The TPS63070 operates from 2 V to 16 V and survives 20 V. It needs no protection part in front
of it. The firmware limit on the setting stays, because 16 V is also the top of the operating
range.

The only other parts on the SYS rail are the charger, capacitors rated 25 V or more, and test
points.

The cost of this choice is idle current. The typical value rises from 8 µA to 54 µA, about
1.1 mAh per day.

## Feedback divider

| Reference | Value | Position |
|---|---|---|
| `R15` | 470 kΩ | Top leg, from the output |
| `R16` | 150 kΩ | Bottom leg, to ground |

The feedback reference is 0.8 V. The divider gives an output of 0.8 x (1 + 470 / 150) = 3.31 V.
The values are the ones in Table 4 of the datasheet.

## Power inductor — L2

`L2` is 1 µH with a saturation current of 6.5 A and a DC resistance of 16 mΩ. The datasheet
allows an effective inductance of 0.7 µH to 2.8 µH, and 0.7 µH to 1.8 µH for large step-down
ratios.

At 3.0 V in and 1.5 A out the calculated peak current is about 1.9 A.

## Capacitors

| Reference | Value | Function |
|---|---|---|
| `C13` | 10 µF, 25 V | Input capacitor directly at `VIN`. |
| `C20` | 10 µF, 25 V | Not fitted. A spare position beside `C13`. |
| `C30` | 10 µF, 25 V | Output capacitor next to the `VOUT` pins. |
| `C14`, `C24`, `C29` | 47 µF, 6.3 V | Output bulk capacitance. |
| `C23` | 100 nF | The internal supply, pin `VAUX`. Nothing else connects to it. |

### Input capacitance

The input pins share the SYS rail with the charger's output capacitors, `C308` to `C312`, five
10 µF parts at 25 V. Together with `C13` that is 60 µF nominal, against a datasheet minimum of
4.7 µF effective. The regulator therefore needs only one capacitor of its own, to carry the fast
switching current at the pins. Fit `C20` if the input ripple measures high.

### Output capacitance

Above about 11 V in, the buck duty cycle is below 30 percent. The datasheet then asks for at
least 40 µF of effective output capacitance. Ceramic capacitors lose much of their value under a
DC voltage. The four output capacitors total 151 µF nominal, so they meet 40 µF even if only
30 percent remains. No derating curve for the 47 µF part was available to confirm the actual
figure.

## Output current

The datasheet rates 2 A only when the input or the output is at least 4.5 V. This board often
has both below that, and the datasheet has no graph for a 3.3 V output.

| Input | Calculated limit at 3.3 V out |
|---|---|
| 3.0 V | about 2.3 A |
| 2.7 V | about 2.1 A |

The calculation uses the minimum input current limit of 3.05 A and 85 percent efficiency. It is
optimistic: the measured graph for a 5 V output shows about 1.6 A to 1.8 A at 3 V in. Measure
the output current on the first assembled board.

During start-up the current limit is much lower, typically about 1 A at the input, until the
output is in regulation.

## Enable and power-save pins

`EN` and `PS/SYNC` connect to the SYS rail through `R12`, 100 kΩ. The datasheet asks for a series
resistor when `PS/SYNC` is tied to the input.

- A high `EN` starts the regulator as soon as it has an input voltage. A GPIO cannot control this
  pin, because the regulator makes the rail that powers the MCU.
- A high `PS/SYNC` selects power-save mode. The sense is the opposite of the `MODE` pin on the
  TPS631000.

The regulator starts at about 2.7 V rising and stops at about 1.85 V falling. While its output
is below 3 V it needs 3.0 V at the input to start.

## Unused pins

`VSEL` connects to ground. `FB2` and `PG` are left open.

## Layout notes

- Place `C13` directly across the `VIN` and `PGND` pins with the shortest possible loop, and `C20` beside it.
- Place `C30` directly across the `VOUT` and ground pins.
- Run a wide copper area from the charger's SYS capacitors to the `VIN` pins.
- Keep the `L1` and `L2` traces short and wide.
- Connect `PGND` and `GND` at the ground plane under the part.
- The footprint follows TI drawing RNM0015A. It uses the drawn opening sizes as copper pads with a
  normal mask expansion, where TI shows mask-defined pads for pins 7 to 13.
- Check the part's rotation in the assembly preview before an order.

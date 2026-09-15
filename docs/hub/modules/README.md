# Per-IC design notes

This folder explains the design decisions for each integrated circuit on the board. Each page
covers one IC and the passive components that belong to it.

These pages tell you *why* the design uses a part or a value. They do not repeat the
manufacturer datasheets. The board does not include the datasheets. Each page gives the exact
part number, so you can get the datasheet from the manufacturer.

## Writing style

These pages use ASD-STE100 Simplified Technical English. Sentences are short. Each sentence
gives one idea. The text uses the active voice and one term for each concept.

## Reference terms

| Term | Meaning |
|---|---|
| SYS rail | The charger output rail. The voltage changes with the battery and the input source. |
| 3V3_SYS | The always-on 3.3 V rail. It supplies the MCU and the internal I2C bus. |
| 3V3_USER | The switched 3.3 V rail. Firmware controls it. It defaults to off. |
| Internal I2C bus | The always-on bus. The charger, the fuel gauge and the `J6` port share it. |
| User I2C bus | The switched bus. The differential buffer, the `J203` port and the 8P8C jacks share it. |
| DNP | Do not populate. The part is on the schematic and the layout, but the board ships without it. |

## The BOM is optimised for small batches, not for volume

This is the single decision that most shapes the passive selection, and it is not obvious from
any individual part. **The board is costed for runs of tens, not thousands.**

At an assembly house like JLCPCB, an order carries two different kinds of cost. There is the
per-unit price of each component, and there is a one-off charge for every *distinct* part
number in the design — a feeder-loading or setup fee, plus an extended-part fee for anything
outside the house's basic library. On a run of ten boards, those one-off charges dominate.
A part that costs 2 cents more per unit is irrelevant next to a few dollars of setup for the
line it sits on.

So the design repeatedly does something that looks wrong in isolation: it fits a
higher-specified, more expensive component where a cheaper one would be electrically
sufficient, because that component is *already on the board somewhere else*.

Worked examples, all visible in the schematic's per-part notes:

- The 4.7 µF positions all use one 25 V 0805 part, including where the rail never exceeds
  3.3 V and a 6.3 V 0402 would have been fine. One feeder instead of two.
- The 10 µF positions use two parts rather than five: a 0603 for the low-voltage rails and a
  25 V 0805 where derating demands it.
- A 1 nF 0402 was chosen for the charger's gate-driver pin specifically because the regulator
  sheet already used that exact part.
- One 100 nF 0402 part covers every high-frequency decoupling position on the board.

The result is **61 distinct part numbers across 112 placements**, with the passives at 27
part numbers covering 70 placements — roughly 2.6 placements per unique passive.

**If you are building this at volume, reverse these decisions.** Once per-unit cost dominates,
the calculus inverts: fit the cheapest adequate part in each position, accept more distinct
part numbers, and the setup fees amortise away. Nothing in the electrical design depends on
these choices — a 6.3 V part where 6.3 V suffices works exactly as well.

## Pages

| Page | Reference | Part |
|---|---|---|
| [ESP32-C5 module](esp32-c5-mcu.md) | `U1` | ESP32-C5-WROOM-1U |
| [Battery charger](bq25798-charger.md) | `U8`, `Q301`–`Q304`, `L1` | BQ25798RQMR |
| [Fuel gauge](bq34z100-fuel-gauge.md) | `U3`, `R60` | BQ34Z100PWR-G1 |
| [Buck-boost regulator](tps631000-regulator.md) | `U4`, `L2` | TPS631000DRLR |
| [User-rail load switch](tps22918-load-switch.md) | `U5` | TPS22918DBVR |
| [Differential I2C buffer](pca9615-i2c-buffer.md) | `U201` | PCA9615DPZ |
| [ESD protection](usblc6-esd-protection.md) | `D5`, `U202` | USBLC6-4SC6-ES |
| [Input reverse-polarity protection](input-protection.md) | `Q1`, `Q2` | MDD3415, DMP3098L-7 |

## Removed parts

The board does not have a separate power monitor IC. An early design had one. The charger
reports the input voltage and the input current through its own ADC. The fuel gauge reports the
battery voltage and the battery current. Together they cover the same measurements, so the
design removed the separate monitor.

# Input reverse-polarity protection — Q1 and Q2

| Item | Value |
|---|---|
| References | `Q1`, `Q2` |
| Parts | MDD3415 (battery), DMP3098L-7 (solar and DC) |
| Package | SOT-23 |
| Schematic sheet | Main sheet |

## Function

Each protection FET blocks current if the user connects a source backwards. Two inputs have this
protection: the battery input `J4`, and the solar or DC input `CN5`.

| Reference | Input | Gate resistor |
|---|---|---|
| `Q1` | Battery, `J4` | `R17`, 100 kΩ |
| `Q2` | Solar and DC, `CN5` | `R19`, 100 kΩ |

## Topology

Both FETs use a self-biased P-channel arrangement. The source connects to the input. The drain
connects to the board. The gate connects to ground through a 100 kΩ resistor.

With correct polarity the gate sits below the source, so the FET turns on. With reversed
polarity the FET stays off and blocks the current.

This arrangement has one important consequence. The gate is at ground, not at a small offset
from the source. The gate-to-source voltage therefore equals the full input voltage, and not a
small logic-level swing. The gate-to-source rating of the FET must cover the full input range.

## Why each input has a different part

The two inputs see very different voltages, so they need different FETs.

### Battery input — Q1

The battery voltage range is about 3 V to 4.8 V. Almost any P-channel FET covers this range.

The part is an MDD3415. The design chose it for stock. The previous part had low stock at the
assembly house.

### Solar and DC input — Q2

The raw input can reach 18 V to 24 V with no load. This input drove the part selection.

An earlier revision used the same FET on both inputs. That FET had a gate-to-source rating of
±8 V. With the self-biased topology, a reversed 16 V source puts 16 V across the gate oxide. That
is genuine overstress, and the protection part itself fails.

The current part is a DMP3098L-7. Its gate-to-source rating is ±20 V. Its drain-to-source rating
is -30 V. Both cover the real range of this input.

One high-stock candidate was checked and rejected during this work. It is rated at ±12 V
gate-to-source. That rating is also below this input's real range, so it would fail in the same
way.

## Why USB-C has no reverse-polarity protection

USB-C is a keyed connector and the specification fixes its pinout. A user cannot connect it
backwards. An earlier revision had a protection stage on this input. The design removed it,
because it protected against a fault that cannot occur.

Removing the stage also removes its voltage drop and its conduction loss from the USB path.

## Lesson from this work

This part selection started from a direct question about how the original FET was chosen. The
answer was that no fitness check existed for each input. One part had been used on both inputs.

Check the real voltage range of each input against the gate-to-source rating of the FET. A
protection part that fails under the fault it protects against gives no protection.

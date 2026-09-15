# Input reverse-polarity protection — Q1 and Q2

| Item | Value |
|---|---|
| References | `Q1`, `Q2`, `D2` |
| Parts | MDD3415 (battery), DMP3098L-7 (solar and DC), BZT52C12S (gate clamp) |
| Package | SOT-23 (`Q1`, `Q2`), SOD-323 (`D2`) |
| Schematic sheet | Main sheet |

## Function

Each protection FET blocks current if the user connects a source backwards. Two inputs have this
protection: the battery input `J4`, and the solar or DC input `CN5`.

| Reference | Input | Gate resistor | Gate clamp |
|---|---|---|---|
| `Q1` | Battery, `J4` | `R17`, 100 kΩ | none needed |
| `Q2` | Solar and DC, `CN5` | `R19`, 100 kΩ | `D2`, 12 V Zener |

## Topology

Both FETs use a self-biased P-channel arrangement. The source connects to the input. The drain
connects to the board. The gate connects to ground through a 100 kΩ resistor.

With correct polarity the gate sits below the source, so the FET turns on. With reversed
polarity the FET stays off and blocks the current.

This arrangement has one important consequence. The gate is at ground, not at a small offset
from the source. The gate-to-source voltage therefore equals the full input voltage, and not a
small logic-level swing.

The stress is symmetric, and that is the part which is easy to get wrong. Both polarities put
the full input voltage across the gate oxide:

| Condition | Source | Gate | Gate-to-source |
|---|---|---|---|
| Correct polarity, conducting | +Vin | 0 V | **-Vin** — this is what turns the FET on |
| Reversed polarity, blocking | -Vin | 0 V | **+Vin** — this is what keeps it off |

A correctly connected 24 V panel therefore stresses the gate just as hard as a reversed one,
for as long as it stays plugged in. The gate rating has to cover the everyday input range, not
only the fault.

## Why each input has a different part

The two inputs see very different voltages, so they need different FETs.

### Battery input — Q1

The battery voltage range is about 3 V to 4.8 V. Almost any P-channel FET covers this range.

The part is an MDD3415. The design chose it for stock. The previous part had low stock at the
assembly house.

#### Where Q1 sits in the battery path

The battery path has two series FETs. The nets have separate names, because each FET separates a
different part of the path.

| Net | Position |
|---|---|
| `VBAT_RAW` | The battery connector `J4`. This is the source of `Q1`. |
| `VBAT_PROTECTED` | The pack side. This is the drain of `Q1` and the drain of the ship FET `Q3`. |
| `VBAT` | The system side. This is the source of `Q3`. It feeds the charger `BAT` pins. |

The full path is `VBAT_RAW` → `Q1` → `VBAT_PROTECTED` → `Q3` → `VBAT`.

`Q1` blocks a reversed battery. `Q3` is the ship FET. The charger opens `Q3` in ship mode, in
shutdown mode and during the system power reset. The two FETs have different jobs, so do not
treat them as one stage.

The fuel gauge `U3` connects to `VBAT_PROTECTED`. It therefore keeps its supply when the charger
opens `Q3`. See [Battery charger](bq25798-charger.md) and [Fuel gauge](bq34z100-fuel-gauge.md).

### Solar and DC input — Q2

The raw input can reach 18 V to 24 V with no load. This input drove the part selection.

An earlier revision used the same FET on both inputs. That FET had a gate-to-source rating of
±8 V. With the self-biased topology, a reversed 16 V source puts 16 V across the gate oxide. That
is genuine overstress, and the protection part itself fails.

The current part is a DMP3098L-7. Its gate-to-source rating is ±20 V. Its drain-to-source rating
is -30 V.

One high-stock candidate was checked and rejected during this work. It is rated at ±12 V
gate-to-source. That rating is also below this input's real range, so it would fail in the same
way.

The ±20 V rating is enough to survive this input, but on its own it capped the usable input at
20 V — below the 24 V the charger itself accepts. `D2` lifts that cap.

## Gate clamp — D2

`D2` is a 12 V Zener across the gate and source of `Q2`. Its cathode connects to the source at
`CN5` pin 1, its anode to the gate. It holds the gate-to-source voltage inside the FET's rating
no matter how high the input goes.

| Condition | Zener | Gate-to-source |
|---|---|---|
| Input below about 12 V | Not conducting | -Vin, exactly as before |
| Input above about 12 V | Reverse breakdown | Clamped near -12 V |
| Reversed polarity | Forward conducting | Clamped near +0.7 V |

`R19` limits the clamp current. At 24 V in that is (24 - 12) / 100 kΩ = 120 µA, which dissipates
about 1.4 mW in a part rated for 200 mW.

### Why 12 V

The DMP3098L-7 specifies its 120 mΩ on-resistance at a gate-to-source voltage of -4.5 V, and its
threshold sits around 2.1 V. A 12 V clamp is well above the voltage the FET needs to be fully
on, and 8 V below the ±20 V limit. Tolerance and temperature drift do not close that gap — the
worst case runs to about 13 V.

Clamping harder than necessary would cost on-resistance, and `Q2` carries the whole input
current. At the board's 2.00 A input limit the FET dissipates I²R, so keeping it fully enhanced
matters thermally as well as electrically.

### The clamp sits below the Zener's knee

`D2` is specified at a 5 mA test current. This clamp draws 120 µA, which is on the soft part of
the curve, so the real clamp voltage lands nearer 10 V to 11 V than 12 V.

That is harmless, and it is deliberate. 10 V is still more than twice what the FET needs to be
fully on. Reaching the rated test current would need `R19` down near 2.4 kΩ, which would draw
5 mA continuously from the panel for as long as the input is live. On a solar harvester that is
a poor trade for a clamp point that does not need tightening. `R19` stays at 100 kΩ.

### What the clamp does not fix

The clamp protects the gate. Two other limits are unchanged:

- Under a reverse fault the full input voltage appears across the drain and source of `Q2`,
  which is rated -30 V. At 24 V reversed, that is 20% margin.
- The charger's own absolute maximum is 30 V, with 24 V as its recommended ceiling.

The clamp also adds a current path that did not exist before. Under a reverse fault, current
flows from ground through `R19`, into the gate, through the forward-biased Zener and back to the
source — about 230 µA at 24 V. A reversed input is therefore no longer a perfect open circuit.
Nothing downstream is powered by that current.

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

A second lesson came later, from asking what the ±20 V rating actually constrained. It is not
only the fault case. A self-biased FET puts the full input across its gate in normal operation
too, so the gate rating caps the everyday input range rather than just the survivable fault.
Once that was clear the fix was one Zener, not a hunt for a scarcer FET.

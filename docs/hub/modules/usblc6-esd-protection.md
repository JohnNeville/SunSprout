# ESD protection — USBLC6-4SC6-ES

| Item | Value |
|---|---|
| References | `D5`, `U202` |
| Part | USBLC6-4SC6-ES |
| Package | SOT-23, 6 pin |
| Schematic sheets | Main sheet (`D5`), `sheets/i2c_buffer_v2.kicad_sch` (`U202`) |

## Function

The part protects data lines against electrostatic discharge. It has four protected channels and
a supply pin. Each channel clamps a line to the supply rail or to ground during a discharge
event.

The board uses two of these parts:

| Reference | Protects | Channels used |
|---|---|---|
| `D5` | The USB-C data lines, D+ and D- | 2 of 4 |
| `U202` | The four differential I2C lines to the 8P8C jacks | 4 of 4 |

## Why one part number for both positions

An earlier revision used a two-channel part at `D5` and this four-channel part at `U202`. The
two positions needed different channel counts, so they used different parts.

JLCPCB charges a feeder-loading fee for each unique component in an assembly. Two similar parts
cost two fees. The design changed `D5` to the four-channel part and rewired it to the correct
pinout. The board now carries one ESD part number instead of two.

Two channels on `D5` stay unconnected. This is deliberate. The cost of the unused channels is
lower than the cost of a second feeder.

## Supply pins

Each part needs its supply pin connected, not left floating. The clamp path runs to this pin.

| Reference | Supply | Nearby decoupling |
|---|---|---|
| `D5` | `VUSB` | `C15` (4.7 µF) and `C16` (100 nF) decouple the `VUSB` rail at the connector. |
| `U202` | 3V3_USER | `C203` (100 nF), fitted specifically for this part. |

`C203` was added during a design review. The supply pin of `U202` was floating before that
change. A floating supply pin gives the clamp current nowhere to go, so the protection does not
work. The capacitor gives a low-impedance path during a surge.

## USB-C data lines

The USB-C connector carries the D+ and D- lines. Two circuits share them: the native USB port of
the MCU, and the BC1.2 charger detection input of the battery charger.

`D5` protects these lines at the connector. The protection sits between the connector and both
circuits, so it clamps a discharge before it reaches either one.

An additional part, `D3`, protects the USB `VBUS` rail. `D3` is a PESD5V0S1BA bidirectional TVS
diode. It protects the power line, not the data lines.

### The star point on D+ and D-

Each data line meets three places at `D5`: the connector, the MCU and, through its isolation
resistor, the charger. A clamp works from one point. If the line branched somewhere else on the
board, a discharge would reach part of the circuit before the clamp saw it.

An earlier revision made that junction with a separate net tie component. The tie carried its own
footprint and its own reference, and the joint sat next to `D5` rather than inside it.

The board now uses `project:USBLC6-4SC6-ES_WIthNetTie`, a local footprint that builds the
junction into the part. Pins 1 and 3 each split into three pads — `1a`/`1b`/`1c` and
`3a`/`3b`/`3c` — declared to KiCad as two tie groups:

```
(net_tie_pad_groups "1a,1b,1c" "3a,3b,3c")
```

Each branch lands on its own pad, so the three nets join at the die pin itself. The separate net
tie component is gone. DRC accepts the shorted pads because the footprint declares the groups;
without that declaration it would report the joins as errors.

## Series resistors on the USB data lines

| Reference | Value | Status |
|---|---|---|
| `R7` | 22 Ω | DNP |
| `R8` | 22 Ω | DNP |

The module manufacturer recommends 22 Ω series resistors on the USB data lines. The footprints
are on the board. The board ships without the resistors, so the lines run directly.

The footprints stay available. If a build shows signal-integrity problems on the USB port, the
resistors can be fitted without a board change.

## Charger isolation resistors

| Reference | Value | Function |
|---|---|---|
| `R9` | 10 kΩ | Isolates the charger D+ input from the shared data line. |
| `R11` | 10 kΩ | Isolates the charger D- input from the shared data line. |

The charger and the MCU share the two data lines. Before this change the charger connected
directly to them. The charger detection input then loaded the live USB signals.

The two resistors separate the charger from the signal path. The charger can still detect the
charger type. It no longer disturbs USB traffic.

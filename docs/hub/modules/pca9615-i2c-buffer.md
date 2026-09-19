# Differential I2C buffer — PCA9615

| Item | Value |
|---|---|
| Reference | `U201` |
| Part | NXP PCA9615DPZ |
| Package | TSSOP-10 |
| Schematic sheet | `sheets/i2c_buffer_v2.kicad_sch` |

## Function

The buffer converts a standard two-wire I2C bus into a four-wire differential bus. The
differential bus drives two 8P8C jacks. It lets the board reach sensors over a long cable.

Standard I2C works over a short distance only. It is single-ended and open-drain, so it picks up
noise and its rise time depends on the cable capacitance. A differential pair rejects
common-mode noise and drives a longer cable.

## Connectors

| Reference | Part | Function |
|---|---|---|
| `J201` | Amphenol RJHSE5380 | 8P8C jack |
| `J202` | Amphenol RJHSE5380 | 8P8C jack |

Both jacks connect to the same four differential nets. The board therefore works as a
pass-through node. A cable enters one jack and leaves the other.

## Scope of this circuit

This circuit takes the wiring pattern of a published differential I2C adapter. It does not copy
the whole design. Two differences matter.

### No termination resistors

The board has no termination resistors on the differential lines. The datasheet requires
termination at both true ends of the transmission line. It does not require termination at an
intermediate tap.

This board is an intermediate node, so it must connect to an adapter that provides the
termination. The board cannot act as the end of a differential chain on its own.

### No local regulator

The reference adapter includes its own buck regulator. It needs one, because it takes its power
from the cable and the cable drops voltage over a long run.

This board already has a 3.3 V rail from its own buck-boost regulator. A second regulator would
add parts and cost with no benefit, so the buffer takes its power from the existing rail.

## Power

Both supply pins, `VDD(A)` and `VDD(B)`, connect to the 3V3_USER rail. The `EN` pin also
connects to that rail, so the buffer is enabled whenever the rail is on.

The load switch controls the rail. See [tps22918-load-switch.md](tps22918-load-switch.md).

| Reference | Value | Function |
|---|---|---|
| `C201` | 100 nF | Local decoupling for `VDD(A)`. |
| `C202` | 100 nF | Local decoupling for `VDD(B)`. |
| `C25` | 47 µF | Bulk reservoir on the rail at the buffer. |

Both supply pins get their own 100 nF capacitor. The part has two supply domains, so one shared
capacitor would leave one domain without local decoupling.

## VCC_2 — optional independent power rail

The two 8P8C jacks carry two separate power nets, mirroring the SparkFun QwiicBus reference
layout rather than collapsing them into one rail:

| Net | Carries | Default state |
|---|---|---|
| `VCC_1` | The board's own `3V3_USER` rail, feeding `U201` directly | Always connected — this is the buffer's supply |
| `VCC_2` / `GRN_P` | A second rail on the green wire pair, independent of the buffer's supply | Bridged to `3V3_USER` by `JP2` |
| `GRN_N` | Return path for `VCC_2` | Bridged to `GND` by `JP3` |

`JP2` and `JP3` are cuttable solder-jumper bridges, shorted as fabricated. Cutting both fully
isolates `VCC_2`/`GRN_N` from this board's 3.3 V rail and ground.

`J2` sits on the `VCC_2`/`GRN_N` pair with no other connection on this board. It was added late,
specifically so that an external supply — a 5 V or 12 V boost converter, for example — can be
injected onto `VCC_2` later without changing this sheet, once `JP2` and `JP3` are cut. The intent
is to support satellite sensors (e.g. soil-moisture ADCs) that may need more than 3.3 V, without
making that a first-class part of this revision.

Cutting the jumpers only isolates the rail on this board. The EndPoint at the far end of the
cable needs its own BP/PSEL jumpers (see the SparkFun QwiicBus EndPoint schematic) set to accept
the injected voltage instead of pulling `VCC_2` from its own `VCC_1`.

## Bus pull-up resistors

| Reference | Value | Net |
|---|---|---|
| `R201` | 4.7 kΩ | `SDA_USER` |
| `R202` | 4.7 kΩ | `SCL_USER` |

I2C is an open-drain bus. Devices pull the line low. A resistor must pull it high. Without
pull-up resistors the bus never returns to a high level and no transfer completes.

A design review found that this bus had no pull-up resistors anywhere on the board. The
datasheet is explicit that the single-ended side needs them. `R201` and `R202` were added near
the buffer.

The pull-up resistors connect to the 3V3_USER rail, not to the always-on rail. This matters.
When firmware turns the user rail off, the pull-up resistors go off with it. No current then
leaks into an unpowered bus.

Downstream STEMMA QT and Qwiic devices usually carry their own pull-up resistors. These combine
in parallel as devices are chained. A long chain therefore lowers the total pull-up resistance.

## ESD protection

`U202` protects the four differential lines. See
[usblc6-esd-protection.md](usblc6-esd-protection.md).

The two 8P8C jacks are the only connectors on this board that are designed to carry a cable to
another circuit board. They are therefore the most exposed to electrostatic discharge.

An earlier revision used a TVS part with a working voltage of 26.5 V and a clamping voltage of
38 V on these lines. Both supply pins of the buffer run at 3.3 V, so these lines never exceed
about 3.3 V. A 38 V clamp gives no useful protection at that level, because the damage happens
long before the part conducts. The design changed to a part rated for this voltage.

## Bus separation

The buffer sits on the user I2C bus. The charger and the fuel gauge sit on the internal I2C bus.
The two buses are separate.

This keeps the remote cable run away from the power-management traffic. A fault on a long
external cable cannot then stall the bus that reports the battery state.

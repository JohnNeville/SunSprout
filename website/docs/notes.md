---
sidebar_position: 6
title: Notes & FAQ
---

# Notes & FAQ

A few things that aren't obvious from the schematic alone.

## The two I2C buses are not interchangeable

This board has two independent I2C buses:

- **Internal bus** (`J6` STEMMA QT) — always-on, shared with the charger and the fuel gauge.
  Adding your own devices here means sharing bus time and address space with the board's own
  power-management traffic.
- **User bus** (`J203` STEMMA QT, plus the two 8P8C jacks via the differential I2C buffer) —
  switched, and electrically isolated from the internal bus by the buffer IC. This is the
  right bus for your own sensors and peripherals.

The 8P8C jacks speak differential I2C, not Ethernet. They use the same PCA9615 scheme and
pinout as the [SparkFun QwiicBus EndPoint](https://www.sparkfun.com/products/16988), so an
ordinary Ethernet patch cable runs from a jack here to an EndPoint, and your Qwiic/STEMMA QT
sensors plug into that. Don't plug a network switch into these — nothing will be damaged, but
nothing will work either.

This board is a pass-through node and carries no termination resistors, so the far end has to
be an EndPoint that provides them.

Downstream STEMMA QT/Qwiic accessories typically carry their own pull-up resistors, which
combine in parallel as you chain more devices onto a bus — worth keeping in mind if you chain
many devices onto the user bus.

## VCC_2 is a separate, cuttable power rail on the 8P8C jacks

Each 8P8C jack carries two power nets, not one. `VCC_1` feeds the differential I2C buffer
itself and is always tied to the board's 3.3V user rail. `VCC_2` — routed on its own wire pair
— is a second, independent rail that only reaches `VCC_1`/`GND` through two solder-jumper
bridges (`JP2` and `JP3`), which are shorted as shipped.

This mirrors the SparkFun QwiicBus reference layout, and it exists for one reason: to leave the
door open for powering hungrier sensors — soil-moisture ADCs, for example — at something other
than 3.3V, without a board revision. Cut `JP2` and `JP3` and `VCC_2` is fully isolated from this
board's own supply and ground. An unpopulated 2-pin header sits on that same net pair, ready to
accept an external 5V or 12V boost converter once the jumpers are cut.

Cutting the jumpers only isolates the rail here. The EndPoint at the far end of the cable needs
its own jumpers set to accept the injected voltage instead of drawing `VCC_2` from its own
`VCC_1`.

## J7 and J8 aren't fitted at the factory

These headers exist in the schematic and PCB layout, but they're excluded from both the bill of
materials and the pick-and-place file. The assembler leaves the pads bare. If you want them,
solder a standard 2.54mm header strip on yourself.

## Connector families are intentionally mismatched

The battery input (`J4`, JST PH) and the DC/solar input (`CN5`, screw terminal) use physically
different connector families on purpose, so a solar panel can't be plugged into the battery
input (or vice versa) even by accident.

## Reverse-polarity protection doesn't cover USB-C

The battery and DC/solar inputs both have reverse-polarity protection, sized to each source's
expected voltage range. USB-C doesn't — it's a mechanically keyed, spec-defined connector, so
there's no practical way to connect it backwards in the first place.

## Battery polarity

Double-check your battery pack's JST-PH cable polarity against the board's silkscreen marking
before connecting. JST-PH battery cables aren't universally standardized across vendors, and a
mismatched cable is one of the few ways to damage the board despite the onboard protection.

## The charger taps the USB data lines through cuttable bridges

The USB-C D+ and D- lines are shared. Each one meets the ESD diode `D5`, the MCU's native USB
peripheral, and the charger's BC1.2 detection input. The three branches join at `D5` itself,
whose footprint carries the junction internally so the clamp sits at a single star point.

The charger's branch runs through `R9` (D+) and `R11` (D-). These are **not** fitted resistors.
They are 0603 pads with a 0.3 mm copper bridge built into the footprint, shorted from the
factory and excluded from the assembly BOM. The charger therefore sees the data lines directly,
and BC1.2 detection works as intended on a prototype out of the box.

The bridges exist so the link can be broken later without a board revision. If the charger's
input capacitance turns out to disturb USB enumeration — most likely during firmware flashing —
cut the bridge through the soldermask window and, if a real value is wanted, hand-solder a 0603
resistor onto the same pads.

`JUMP_CHGR_GND2` is a three-way solder jumper that grounds the charger-side pins after a cut:
bridge the centre pad to one outer pad to ground D+, to the other to ground D-. Grounded is the
correct resting state for those pins, since a floating detection input can read as anything.

:::warning Cut before you ground
Bridging `JUMP_CHGR_GND2` while `R9`/`R11` are still intact shorts the live USB data lines to
ground and kills the port. Cut the bridges first, then ground. Nothing on the board prevents
this — the jumper is an open footprint and the bridges are declared as net ties, so neither
DRC nor the ratsnest will flag the mistake.
:::

Cutting a bridge also puts the board out of step with the design files, which continue to show
the nets as connected.

## Thermistors are required, not optional, for full charger/fuel-gauge behavior

The charger's JEITA temperature-qualified fast charging and the fuel gauge's temperature
compensation both depend on their respective thermistor inputs (`J302` and `J401`) actually
having a thermistor attached. Without them, both ICs still function, but you lose
temperature-qualified charging and accurate temperature-compensated state-of-charge.

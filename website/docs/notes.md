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
  a separate I2C port on the ESP32-C5, powered from the switched 3.3V user rail, which firmware
  controls and which defaults to off. The buffer IC only converts this bus to differential
  signalling for the jacks; it does not isolate it from anything. The unfitted `J7` header also
  carries these two lines (pins 6 and 7). This is the right bus for your own sensors and
  peripherals.

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
itself and is tied to the switched 3.3V user rail (`3V3_USER`), so it is off whenever firmware
disables that rail. `VCC_2` — routed on its own wire pair — is a second, independent rail that
only reaches `VCC_1`/`GND` through two solder-jumper bridges (`JP2` and `JP3`), which are
shorted as shipped.

This mirrors the SparkFun QwiicBus reference layout, and it exists for one reason: to leave the
door open for powering hungrier sensors — soil-moisture ADCs, for example — at something other
than 3.3V, without a board revision. Cut `JP2` and `JP3` and `VCC_2` is fully isolated from this
board's own supply and ground. An unpopulated 2-pin header, `J2` (pin 1 `VCC_2`, pin 2 the
`VCC_2` return), sits on that same net pair, ready to accept an external 5V or 12V boost
converter once the jumpers are cut.

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
before connecting. On `J4`, pin 1 is `BATT+` (`VBAT_RAW`) and pin 2 is `BATT−` (the battery
return). JST-PH battery cables aren't universally standardized across vendors, and a mismatched
cable is one of the few ways to damage the board despite the onboard protection.

## The charger is disconnected from the USB data lines by default

The USB-C D+ and D- lines are shared. Each one meets the ESD diode `D5` and the MCU's native USB
peripheral. The charger's BC1.2 detection input has pads for a third branch. The branches join at
`D5` itself, whose footprint carries the junction internally so the clamp sits at a single star
point.

The charger's branch runs through `R9` (D+) and `R11` (D-). **These positions are unpopulated.**
They are empty 0603 pads, excluded from the assembly BOM, so the charger does not connect to the
USB data lines on a stock board. This keeps its input capacitance and detection signalling off
the bus, which matters during firmware flashing over the native USB port.

The charger therefore gets no BC1.2 detection from the host. Its input current limit does not
depend on that: the hardware clamp on `ILIM_HIZ` still caps the input at roughly 2 A. To bring
detection back, hand-solder a 10 kΩ 0603 resistor onto each pad.

`JUMP_CHGR_GND2` is a three-way solder jumper that grounds the charger-side pins: bridge the
centre pad to one outer pad to ground D+, to the other to ground D-. The datasheet does not say
whether unused D+/D- pins should float or be grounded. They are analog I/O pins, so grounding
them gives a defined state, but it is optional.

:::warning Leave R9 and R11 empty before you ground
Bridging `JUMP_CHGR_GND2` while a resistor is fitted on `R9` or `R11` shorts that live USB data
line to ground and kills the port. Close the jumper only while both positions are empty. Nothing
on the board prevents this, so neither DRC nor the ratsnest will flag the mistake.
:::

## Thermistors are required, not optional, for full charger/fuel-gauge behavior

The charger and the fuel gauge each have their own thermistor input (`J302` and `J401`), and
both need a thermistor attached.

- **Charger (`J302`).** With nothing fitted, the charger's temperature input reads as far too
  cold and, by default, it **suspends charging**, and the charge LED blinks at 1 Hz. Fit a
  103AT-type 10 kΩ NTC. Or, to charge without one, set `ts_ignore: true` in the firmware, which
  gives up temperature protection.
- **Fuel gauge (`J401`).** With nothing fitted, the gauge's temperature reading is invalid. On
  the first prototype it read about −38 °F and reported "Charge inhibited". Fit a thermistor,
  or configure the gauge to use its internal temperature sensor.

Both thermistors should sit against the cell, so temperature-qualified charging and
temperature-compensated state of charge work as intended.

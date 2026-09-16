---
sidebar_position: 5
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

## Thermistors are required, not optional, for full charger/fuel-gauge behavior

The charger's JEITA temperature-qualified fast charging and the fuel gauge's temperature
compensation both depend on their respective thermistor inputs (`J302` and `J401`) actually
having a thermistor attached. Without them, both ICs still function, but you lose
temperature-qualified charging and accurate temperature-compensated state-of-charge.

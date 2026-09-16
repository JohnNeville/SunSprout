---
sidebar_position: 6
title: Use Cases
---

# Use Cases

:::warning[Not yet validated on this board]

The system described here runs today on an earlier, different board. The satellite enclosure
and its sensor wiring are stable and in service; the hub half has **not** been built, flashed,
or tested, and the ESPHome configuration has not yet been adapted to this board's components.

Treat this as the intended design, not a working recipe.

:::

## Garden soil monitoring

The design driver for this board: a solar-powered garden monitor where the sensors need to sit
some distance from the electronics.

```
  ┌──────────────────────┐              ┌─────────────────────────┐
  │  SunSproutHub        │              │  Satellite 1            │
  │  (weatherproof box)  │   Ethernet   │  EndPoint + ADS1115     │
  │                      │   patch      │  @ 0x48 ── 4 probes     │
  │  solar panel ────────┤   cable      └─────────────────────────┘
  │  battery      8P8C ──┼──────────────►
  │  ESP32-C5     8P8C ──┼──────────────►
  │                      │              ┌─────────────────────────┐
  └──────────────────────┘              │  Satellite 2            │
                                        │  EndPoint + ADS1115     │
                                        │  @ 0x49 ── 4 probes     │
                                        └─────────────────────────┘
```

The hub sits in one weatherproof enclosure with the panel and battery. Each satellite is its
own enclosure out among the plants, holding a [SparkFun QwiicBus
EndPoint](https://www.sparkfun.com/products/16988) and a single ADS1115. An ordinary Ethernet
patch cable carries I2C to each one.

The board's two 8P8C jacks are wired in parallel onto the *same* differential bus, not two
separate ones — so a satellite can hang off either jack, or chain from another satellite. That
is why each ADC needs its own address.

The deployed system uses **two satellites covering eight plants** — four probes per satellite,
one per ADC channel.

### Why not just run the sensor wires

Capacitive soil probes output an analog voltage, and analog over a long run picks up noise and
drifts with wire resistance. Digitising at the plant and sending I2C differentially is far more
robust — and plain I2C itself won't survive the distance, which is what the differential buffer
on this board solves.

### Inside a satellite

| Part | Role |
|---|---|
| QwiicBus EndPoint | Converts the differential pair back to standard I2C, and terminates the line |
| ADS1115 | 16-bit ADC, four single-ended channels |
| Capacitive soil probes | Up to four, one per channel |

One ADC per enclosure keeps each satellite simple and puts the probes close to what digitises
them. Scaling means adding satellites, not stuffing more into one.

The ADS1115's address is strap-selected across `0x48`–`0x4B`, so up to four satellites can
share the bus — sixteen probes in total before addressing runs out. The deployed pair sit at
`0x48` and `0x49`.

Each probe is calibrated with a dry and a wet reference voltage, measured per-probe rather than
assumed — roughly 2.43 V dry and 1.12 V wet in the deployed setup, with one probe needing its
own value. Probes vary enough that this is worth doing individually.

### Power behaviour

Soil moisture changes slowly, so the node spends most of its life asleep: wake, read, publish,
sleep. The deployed configuration polls soil every 300 s and runs a 120 s awake window against
a 10 minute deep sleep cycle.

That pattern suits this board's switched user rail — the differential buffer and everything
downstream of it can be powered down between readings, leaving only the MCU, charger and fuel
gauge on the always-on rail. See [Overview](./overview.md#power).

## Adapting the existing configuration

The reference configuration is
[`plant_sensor.yaml`](https://github.com/JohnNeville/esphome-garden-sensor/blob/main/plant_sensor.yaml)
in the [esphome-garden-sensor](https://github.com/JohnNeville/esphome-garden-sensor)
repository. It targets the earlier board, so the satellite half carries over unchanged while
the hub half does not:

| | Earlier board | SunSproutHub |
|---|---|---|
| MCU | ESP32-S3 | ESP32-C5 |
| Charger | BQ25628E @ `0x6A` | BQ25798 |
| Fuel gauge | LC709204F @ `0x0B` | BQ34Z100 |
| Rail monitoring | INA3221 | Charger's integrated 16-bit ADC |
| I2C pins | GPIO35/36, GPIO47/48 | GPIO2/3 (internal, on `LP_I2C`), GPIO9/10 (user) — see [Pins & Signals](./pinout.md) |

The satellite side — ADS1115 addressing, the soil-probe template, calibration voltages — needs
no change, because nothing about it depends on which board is at the other end of the cable.

Two things are genuinely unresolved, and are the reason this page is marked work in progress:

- **ESPHome component support.** The earlier board's charger and fuel gauge had usable ESPHome
  components. Whether equivalents exist for the BQ25798 and BQ34Z100, or whether they need
  writing, has not been established.
- **MPPT handling.** The earlier configuration adjusted a target voltage in software based on
  the detected supply. This board's charger performs open-circuit-voltage MPPT in hardware, so
  that logic should be removed rather than ported — but that needs confirming against real
  behaviour once a board exists.

## Other shapes this fits

Nothing about the board is specific to soil. The same hub-and-satellite pattern suits any
deployment where I2C sensors need to be metres from the power electronics: greenhouse climate
monitoring, water tank levels, or several satellites chained from one hub. The constraint is
I2C's — total bus capacitance and address collisions — rather than anything this board imposes.

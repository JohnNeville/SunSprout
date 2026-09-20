---
sidebar_position: 7
title: Use Cases
---

# Use Cases

:::warning[Not yet validated on this board]

The system described here runs today on an earlier, different board, with an off-the-shelf
SparkFun QwiicBus EndPoint standing in for the satellite. Neither half of the design
described on this page has been built yet: the hub has **not** been built, flashed, or
tested, and the satellite is a custom board (`hardware/satellite/`) that currently exists
only as a schematic-capture spec — no board has been fabricated, and the ESPHome
configuration has not been adapted to either board's components.

Treat this as the intended design, not a working recipe.

:::

## Garden soil monitoring

The design driver for this board: a solar-powered garden monitor where the sensors need to sit
some distance from the electronics.

```
  ┌──────────────────────┐              ┌───────────────────────────┐
  │  SunSproutHub        │              │  Satellite 1              │
  │  (weatherproof box)  │   Ethernet   │  SunSproutSatellite       │
  │                      │   patch      │  @ 0x48 ── 4 moisture     │
  │  solar panel ────────┤   cable      │           probes + 1 temp │
  │  battery      8P8C ──┼──────────────►└───────────────────────────┘
  │  ESP32-C5     8P8C ──┼──────────────►
  │                      │              ┌───────────────────────────┐
  └──────────────────────┘              │  Satellite 2              │
                                         │  SunSproutSatellite       │
                                         │  @ 0x49 ── 4 moisture     │
                                         │           probes + 1 temp │
                                         └───────────────────────────┘
```

The hub sits in one weatherproof enclosure with the panel and battery. Each satellite is its
own enclosure out among the plants, holding a `SunSproutSatellite` board
(`hardware/satellite/`) — a custom differential-I2C endpoint that integrates the PCA9615
buffer, the ADS1115, and a DS2484 for soil temperature onto one PCB, replacing what was
previously an off-the-shelf [SparkFun QwiicBus
EndPoint](https://www.sparkfun.com/products/16988) wired to a breadboarded ADS1115. An
ordinary Ethernet patch cable carries I2C to each one.

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
| PCA9615 | Converts the differential pair back to standard I2C, and terminates the line — see `docs/satellite/modules/pca9615-i2c-endpoint.md` |
| ADS1115 | 16-bit ADC, four single-ended channels — one per moisture probe |
| DS2484 | I2C-to-1-Wire bridge, drives one DS18B20 soil-temperature probe |
| Capacitive soil probes | Up to four, one per ADS1115 channel |
| DS18B20 probe | One, on the DS2484's 1-Wire bus |

One PCB per enclosure keeps each satellite simple and puts the probes close to what
digitises them. Scaling means adding satellites, not stuffing more into one.

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

The ADS1115 addressing, the soil-probe template, and calibration voltages carry over
unchanged, because nothing about them depends on which board is at the other end of the
cable. The `SunSproutSatellite` board itself is new, though — its DS2484/DS18B20
soil-temperature channel has no equivalent in the earlier configuration.

Three things are genuinely unresolved, and are the reason this page is marked work in progress:

- **ESPHome component support.** The earlier board's charger and fuel gauge had usable ESPHome
  components. Whether equivalents exist for the BQ25798 and BQ34Z100, or whether they need
  writing, has not been established.
- **MPPT handling.** The earlier configuration adjusted a target voltage in software based on
  the detected supply. This board's charger performs open-circuit-voltage MPPT in hardware, so
  that logic should be removed rather than ported — but that needs confirming against real
  behaviour once a board exists.
- **DS2484/DS18B20 support.** The earlier satellite had no soil-temperature channel, so
  `plant_sensor.yaml` has nothing to adapt here — this is new firmware work, not a port,
  once a `SunSproutSatellite` board exists to test it against.

## Other shapes this fits

Nothing about the board is specific to soil. The same hub-and-satellite pattern suits any
deployment where I2C sensors need to be metres from the power electronics: greenhouse climate
monitoring, water tank levels, or several satellites chained from one hub. The constraint is
I2C's — total bus capacitance and address collisions — rather than anything this board imposes.

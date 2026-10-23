---
sidebar_position: 8
title: Current measurements
---

# Current measurements

How much current the SunSprout hub draws in each power state, measured with a Nordic Power Profiler Kit II
(PPK2). This page is a placeholder: the method is settled, but most states have not been measured yet. Rows
marked **Not measured** will be filled in, with a trace for each, as the measurements are made.

Every figure here comes from one hub prototype in one set-up. They show what a board can do, not a
specification.

## Test set-up

- **Supply:** the PPK2 in source meter mode, set to 3.7 V, connected to the battery connector (`J4`). There is no
  battery and no USB or solar input.
- **Fitted:** a hub with no thermistor, the fuel gauge enabled, nothing on the satellite ports and nothing on
  the user rail.
- **Sampling:** 100,000 samples per second. A state is reported as the settled value, read after the board has
  entered it, and as an average over a full cycle where the state has periodic activity.
- **Digital channels:** the PPK2's logic inputs record the internal I2C bus (`SDA_INT`, `SCL_INT`), `3V3_SYS`
  and `3V3_USER`, so a change in current can be matched against a rail or a bus event.
- **Firmware:** the hub firmware with deep sleep enabled. In the states marked "ADC off", the charger's ADC is
  switched off just before sleep.

## Results

| State | Settled | Average over the cycle | Status |
|---|---|---|---|
| Deep sleep, charger ADC left on | 1.06 mA | about 1.23 mA | Initial result |
| Deep sleep, charger ADC off before sleep | 0.47 mA | about 0.63 mA | Initial result |
| Deep sleep, fuel gauge sleep mode confirmed on | | | Not measured |
| Deep sleep, fuel gauge sleep mode off | | | Not measured |
| Charger ship mode | | | Not measured |
| Charger shutdown mode | | | Not measured |
| Awake, WiFi connected, idle | | | Not measured |
| Awake, WiFi connected, satellites fitted | | | Not measured |
| Boot and WiFi connect | | | Not measured |

### Deep sleep

In deep sleep the hub switches off `3V3_USER`, and the ESP32 stops. The charger and the fuel gauge stay powered
on the battery and keep working.

**Charger ADC on or off.** The firmware turns the charger's ADC on when it starts, and the ADC is what makes
the voltage and current readings. Left on through sleep, the ADC accounts for most of the sleep current. With it
switched off before sleep, the settled current fell from 1.06 mA to 0.47 mA. The charger's datasheet gives a
similar difference, 17 µA with the ADC disabled against 540 µA with it enabled (battery only, 8 V on the
battery), and the ADC also keeps a regulator running that biases the temperature divider. This measurement does
not separate the two.

**Bursts every 19.7 s.** A burst of about 35 mA lasting 124 ms repeats every 19.7 s while the board sleeps. It
adds about 0.16 mA to the average. Nothing moves on `3V3_SYS` or on the internal I2C bus during a burst, and it
is the same with the ADC on or off. Its source has not been found.

**Fuel gauge sleep mode.** The fuel gauge has its own low-power mode. It has not been confirmed whether it is on
in this set-up, and a gauge that stops counting while it sleeps could matter for lithium iron phosphate cells.
Both rows above are placeholders for that check.

## Traces

Each measured state will have a screenshot of the PPK2 trace and a link to the raw capture. None are published
yet.

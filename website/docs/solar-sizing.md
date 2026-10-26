---
title: Solar Sizing
---

import SolarSizing from '@site/src/components/SolarSizing';

# Solar Sizing

How big a panel and battery do you need to keep a SunSprout running through a week of cloud? This
page gives you a calculator and tells you what to measure so its answer is worth trusting.

:::warning[An estimate, not a guarantee]

The result is only as good as the numbers you enter. Two of them, the cloudy-day sun and your
average current, can each move the answer by a factor of two. The calculator shows how much the
answer moves, and the sections below say how to pin each input down. Treat the output as a
starting point and check it against a few weeks of your own data.

:::

## The calculator

The fields start from the stock firmware configuration: a 6000 mAh LiFePO4 pack, a 1000 mA charge
limit, and deep sleep with 120 s awake then 15 min asleep. Change anything your setup does
differently. The sleep and awake currents are bench measurements (PPK2) from one hub with no sensors
or satellites attached, and the awake figure leaves out boot and WiFi connect, so replace both with
your own readings.

<SolarSizing />

## How it works

1. **Daily load** is your average battery current times the pack's nominal voltage times 24 h.
2. **Battery** gives you a usable reserve: 80% of the rated capacity for Li-ion, 90% for LiFePO4.
3. **Cloudy stretch.** Each cloudy day the panel covers part of the load and the battery covers the
   rest. The panel has to be big enough that the reserve lasts your chosen number of days.
4. **Recovery.** After the cloud, the panel must carry the normal load and also refill the reserve
   within the recovery time you allow. A panel that survives the cloud but takes a month to refill
   leaves you exposed to the next spell.
5. The answer is the larger of the two panel sizes. The calculator tells you which one set it.

A bigger battery lowers the panel you need for the cloudy stretch but raises the one you need to
refill it. If the cloudy figure dominates, add battery or cut the load. If the recovery figure
dominates, add panel or allow longer to refill.

The charge current limit also caps what a panel can deliver. At the default of 1000 mA a LiFePO4
pack accepts about 3.7 W (4.2 W for Li-ion), which is roughly a 6 to 7 W panel after losses, so a
20 W panel mostly helps in weak light. The limit may never exceed 2000 mA.

## What to measure

Five inputs matter. Ordered by how much they move the answer:

### 1. Average current (the biggest lever)

You need the mean battery current over a full wake cycle, with your real sensors, satellites and
WiFi conditions. The device sleeps most of the time, so **averaging the Battery Current entity in
Home Assistant is wrong.** It only reports when the board is awake, and a mean of those samples
is far too high. Use one of these instead:

- **Fuel gauge drain test (no extra equipment).** Charge the pack full, disconnect the panel and
  USB, and let the hub run its normal schedule for 3 to 7 days. Note **Battery Level** at the start
  and end. Average current in mA is `(percent drained / 100) × capacity in mAh / hours`. Load the
  gauge chemistry profile first, because until you do the state of charge is wrong.
- **Current analyser (most accurate).** A Nordic PPK2 or similar on the battery lead for at least
  three complete wake cycles, plus a long capture of the sleep floor. Average is
  `(sleep mA × sleep time + awake mA × awake time) / cycle time`.
- **Duty-cycle estimate (rough).** Use the calculator's second tab. Awake time depends heavily on
  how quickly WiFi connects and the API is reached, so measure it from the ESPHome log rather than
  guessing.

Measure at the temperature you expect. Cold lowers usable capacity and raises awake time.

### 2. Normal sun hours at your site

"Peak sun hours" is the daily solar energy on the panel in kWh per square metre, which equals
the number of hours at full 1000 W/m² sun. Use the **worst month you need the device to run**,
not the annual average. Look it up for your latitude and your actual panel tilt:

- PVGIS (European Commission) monthly radiation tool, at the "in-plane" value for your tilt.
- NASA POWER, "all sky surface shortwave downward irradiance".

A winter month in a high-latitude garden can be under 1 hour.

### 3. How dark a cloudy week is

This is the weakest input, and no tool gives it exactly. Overcast days typically deliver 10% to
30% of normal, and a thick-cloud or snow week can be less. Options, best first:

- **Your own data.** If a panel is already connected, log harvest on your worst weeks (see below).
- **Weather station records.** Look at the lowest 7-day sum of solar radiation in a local station's
  history for your target month, divided by the normal 7-day sum.
- **Rule of thumb.** 0.2 for a typical cloudy stretch, 0.1 if you must survive the worst case.

### 4. System efficiency

Rated panel watts are for ideal lab conditions. What reaches the battery is lower because of
panel temperature, dirt and shade, wiring, the MPPT's open-circuit-voltage tracking (an
approximation, not true maximum-power tracking), and charger losses. Use 0.5 to 0.7. Use the
low end for a small panel in a shaded or dusty spot.

### 5. Battery capacity and chemistry

Use the rated capacity, then let the calculator derate it. Old packs and cold nights hold less,
so enter a lower figure if either applies.

## Calibrate with your own harvest

Once a panel is connected, log a few weeks and replace the guesses with a measurement.

1. Record the **Input Current** and **Solar Input Voltage** entities in Home Assistant at a fixed
   interval while the board is awake, or use an external energy meter on the panel lead.
2. Sum energy into the battery per day, in Wh.
3. Divide each day's Wh by the panel's rated watts. That is your effective sun hours **after**
   all losses, which already includes the efficiency input.
4. Your worst 7-day total, divided by 7, is the real cloudy-stretch figure. Set the calculator's
   efficiency to 1.0 and normal sun hours to your effective figure, and enter the cloudy fraction
   from your worst week.

:::note[Check the panel against the hub's limits]

Use the panel's **cold-weather open-circuit voltage** and keep it within the hub's **3.6 to 24 V**
input range. The calculator does not check voltage.

:::

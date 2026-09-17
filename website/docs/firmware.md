---
sidebar_position: 5
title: Firmware
---

# Firmware

:::warning[Never flashed or run]

No physical board exists, so this configuration has never been flashed, powered on, or talked
to a real charger. It builds — CI validates the ESPHome config on every change — but building
is not the same as working. Treat everything here as the intended behaviour, not as observed
behaviour.

:::

The board runs [ESPHome](https://esphome.io/). It joins Home Assistant as a device with the
charger, the fuel gauge and the user rail exposed as ordinary entities, and it updates over
the air after the first flash.

| | |
|---|---|
| Board configuration | [`firmware/sunsprout-hub.yaml`](https://github.com/JohnNeville/SunSprout/blob/main/firmware/sunsprout-hub.yaml) |
| Example device | [`firmware/example-device.yaml`](https://github.com/JohnNeville/SunSprout/blob/main/firmware/example-device.yaml) |
| Chip drivers | [esphome-bq-drivers](https://github.com/JohnNeville/esphome-bq-drivers) |
| Why it is configured this way | [docs/hub/firmware.md](https://github.com/JohnNeville/SunSprout/blob/main/docs/hub/firmware.md) |

The board configuration is a *package*: it describes the hardware and nothing else. Your own
device file adds WiFi, the API, OTA and deep sleep on top of it. The two chip drivers live in
a separate repository because they drive stock TI parts and have nothing to do with this
board.

## Flashing

```bash
pip install esphome
```

Create a `secrets.yaml` beside your device file containing `wifi_ssid`, `wifi_password`,
`fallback_password`, `api_encryption_key` and `ota_password`, then:

```bash
esphome run firmware/example-device.yaml
```

For the **first** flash the board has to be in download mode: hold `SW2` (BOOT) while pressing
`SW1` (RESET). After that, OTA handles it.

## Set the cell chemistry before you attach a cell

This is the one setting that can damage something.

The charger reads its `PROG` resistor at power-on and comes up configured for a **4.2 V** 1S
cell. A LiFePO4 cell charges to **3.65 V**. If the firmware never corrects that, a LiFePO4
pack is charged half a volt over its limit.

The configuration declares the chemistry instead of the voltage:

```yaml
substitutions:
  cell_chemistry: "lifepo4"     # or li_ion, li_ion_4_35, li_ion_4_40
  battery_capacity: "6000"      # mAh
```

The driver derives the charge-voltage limit from the chemistry, writes it during setup, and
writes it again after any register reset. There is deliberately **no charge-voltage control**
in Home Assistant — a limit that protects the cell should not be something anyone can drag on
a dashboard.

Set `battery_capacity` to your actual cell. It sets the charge-termination current to C/10 and
the fuel gauge's design capacity.

## Battery size

The charger's power-on default charge current is **1 A**, and that default is fixed in the
silicon — the `PROG` resistor selects cell count and switching frequency, not current. The
configuration lowers it to 1000 mA immediately and clamps the maximum at 2000 mA, which is what
the board's copper is rated for.

That still implies a floor on cell size. At 1 A, a 1000 mAh cell is being charged at 1C and a
500 mAh cell at 2C. **Prefer a cell of 1000 mAh or more**, and lower `charge_current` if you
fit something small.

## What you get in Home Assistant

Roughly fifty entities. The ones you will actually look at:

| Entity | What it tells you |
|---|---|
| **Battery Level** | State of charge, from the fuel gauge |
| **Battery Voltage**, **Battery Current** | Pack voltage and charge/discharge current |
| **Solar Input Voltage**, **USB Input Voltage** | Which source is present and at what voltage |
| **Charging**, **Charge Status** | Whether it is charging, and in which phase |
| **Charger Fault** | Faults reported by the charger |
| **Battery Temperature** | Cell temperature — see the caveat below |

Controls include **Enable Charging**, **Enable MPPT**, **Charge Current Limit**, the user-rail
switch, and a **Power Cycle Board** button. Ship mode and shutdown are hidden by default.

## Two things need a bench visit

**The fuel gauge chemistry profile.** The gauge ships set up for lithium-ion. LiFePO4 needs a
400-series profile, and until it is loaded the state of charge is wrong no matter what else is
set — which matters most for exactly this chemistry, whose flat discharge curve makes
voltage-based estimates useless.

There is **no I2C command that sets the chemistry**: `CHEM_ID` only reports it, and the one
selection path TI documents is the BQChem feature in bqStudio. The chemistry data itself,
though, is ordinary data flash — reachable either through bqStudio or through the same data
flash block transfers the firmware already uses, and the datasheet explicitly describes
capturing the result as a Golden Image File that "can then be written to multiple battery
packs".

So this is a **bqStudio-once** step to obtain the values, not a per-board one. After that the
bytes can be replayed over I2C. The firmware reads the gauge's chemistry ID at boot and logs an
error if it does not match `expected_chem_id`, so a gauge running the wrong profile is at least
visible.

Everything else the gauge needs *can* be written from firmware: set `apply_configuration: true`
with a cell attached, reflash once, then run **Calibrate Gauge Current Offset** and **Calibrate
Gauge Board Offset** with the pack at rest.

**The battery thermistor.** `J302` ships with nothing fitted, and an empty thermistor input
reads as a cell far below the charger's cold cutoff — so **the charger refuses to charge**.
Fit a 103AT-type 10 kΩ NTC, which is the part the charger's datasheet recommends.

There is deliberately no fixed resistor standing in for it. A resistor would hold the input at
a constant voltage, and **Battery Temperature** would then report a steady 25 °C that no sensor
measured — a convincing wrong reading is worse than an absent one. To run without a thermistor
and accept losing temperature qualification, the charger's `TS_IGNORE` bit is the honest route;
the driver does not expose it yet.

With nothing fitted, **Battery Temperature** reports an implausibly cold value. That is the
signature of a missing thermistor, not a real reading.

## Rebooting

**Power Cycle Board** opens the ship FET for about 350 ms. The whole `SYS` rail drops — MCU,
regulator, both STEMMA QT ports, the user rail — and the board restarts.

It does not reset everything. The charger performs the reset itself, and the fuel gauge sits on
the pack side of the FET so it keeps counting through it. That is deliberate — a gauge that
loses power has to relearn the pack — but it means **a power cycle cannot clear a stuck I2C
device**, because neither I2C device actually loses power.

Holding `SW3` for about ten seconds does the same thing in hardware, with no firmware involved.
That is the one that still works when the MCU is hung.

## Solar tracking

The charger finds the panel's maximum power point by itself. Every couple of minutes it stops
switching, measures the open-circuit input voltage, and sets its input-voltage limit to a
fraction of it. The **Enable MPPT** switch turns it on; the configuration enables it by
default.

There is no tracking loop in the firmware and no separate power-monitor chip on the board,
because the charger already does this work.

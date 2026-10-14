---
sidebar_position: 2
title: Getting started
---

# Getting started

Power up a hub, flash it with ESPHome, and check that it can talk to its own chips. You need
the board, a USB-C cable, and a computer with Python.

:::danger[Unverified charging hardware]

The current design has not been built. Before you connect a battery:

- **Set the cell chemistry in the firmware first.** The charger powers up for a 4.2 V cell. A
  LiFePO4 cell charges to 3.65 V, so a LiFePO4 pack left on the power-up default is charged
  0.55 V over its limit. The shipped configuration declares `lifepo4`; for any other cell,
  change `cell_chemistry` (see [Firmware](./firmware.md)).
- **Fit a 10 kΩ NTC thermistor** on the `CHGR_TS` connector, mounted on the cell. With none
  fitted the charger will not charge.
- **Never set the charge current above 2000 mA.** Nothing in hardware limits it.
- **Check the battery polarity** against the `BATT +` and `BATT −` markings. The reverse-polarity
  protection was redesigned and has not been tested on hardware.

Do steps 1 to 4 with **no battery connected**.

:::

## 1. Download the configuration

The ESPHome files are in the [`firmware/`](https://github.com/JohnNeville/SunSprout/tree/main/firmware)
folder of the repository.

```bash
git clone https://github.com/JohnNeville/SunSprout.git
cd SunSprout
pip install esphome
```

Copy `firmware/example-device.yaml` as your starting point, and create a `secrets.yaml` next
to it with `wifi_ssid`, `wifi_password`, `fallback_password` and `api_encryption_key`.

## 2. Connect the board

Plug a USB-C cable into the board's USB-C port. This one port powers the board, flashes it and
carries its log output. The ESP32-C5 uses its built-in USB, so there is no separate USB-serial
chip or driver to install.

## 3. Start the flash

```bash
esphome run firmware/example-device.yaml
```

If ESPHome cannot find the board, or the upload does not start, put the board into download
mode:

1. Hold the **BOOT** button (`BOOT` on the silkscreen).
2. Press and release the **RESET** button.
3. Release **BOOT**.

Then run the command again. After this first flash, updates can go over Wi-Fi.

The USB port disconnects and reappears every time the board reboots. Use a terminal that
reconnects, such as `esphome logs`.

## 4. Check the internal bus

On boot the firmware scans the **internal I2C bus**, which carries the charger and fuel gauge.
Look for these two addresses in the log:

| Chip | Address |
|---|---|
| Charger | `0x6B` |
| Fuel gauge | `0x55` |

If either is missing, stop and check the board before going further.

The **sensor** bus is not scanned at boot, because its 3.3 V rail is switched off at power-up.
Only after the internal bus looks right, turn on the **User 3V3 Rail** switch in Home Assistant.
That powers the `Qwiic User` port and the two 8P8C jacks.

## 5. Connect the battery

Only now, with the chemistry set, the thermistor fitted and the first four steps passing,
connect the battery to the `BATT` connector. In the firmware's entities, confirm that **Battery
Voltage** matches a multimeter on the cell, and that **Charging** behaves as expected.

A LiFePO4 cell also needs a fuel-gauge chemistry profile loaded before its state of charge is
correct. That is a one-time step; see [Firmware](./firmware.md).

## Where things are

Connector and button names on these pages are the labels printed on the board where it has them (`SOLAR`, `BATT +`/`BATT −`, `Qwiic Sys`, `Qwiic User`, `RESET`, `BOOT`, `WAKE`, `CHGR_TS`, `FG_TS`). To find a part on
the physical board, use the [interactive BOM](pathname:///ibom/); and see
[Connectors](./connectors.md) for what each one does.

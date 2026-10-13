---
sidebar_position: 7
title: Testing status
---

# Testing status

A checklist of what has and hasn't been tested on real hardware. The first hub prototype was
built from commit [`1645733`](https://github.com/JohnNeville/SunSprout/commit/1645733). The
current design files include fixes for problems found on it, and that revision has not been
built yet.

| Status | Meaning |
|---|---|
| **Tested** | Worked on the prototype. |
| **Issue, fixed in design** | Failed or misbehaved on the prototype. The fix is in the current files but has not been tested on a board. |
| **Not yet tested** | No result yet. |

Features not listed here have not been tested.

## Power and charging

| Feature | Status | Notes |
|---|---|---|
| Power from USB-C | Tested | |
| DC / solar input | Not yet tested | |
| Source selection between USB-C and DC | Not yet tested | |
| Solar MPPT | Not yet tested | |
| Charging a battery | Tested | Reached fast charge from USB at about 470 mA with no thermistor fitted and `ts_ignore: true` set. Without that setting the charger suspends charging by default. |
| Charger status LED | Tested | Blinks while charging is suspended. Too bright, so the series resistor was raised in the current design (untested). |
| Charger and input readings in Home Assistant | Tested | Input source, input voltage and fault status. |
| Reverse-polarity protection | Not yet tested | Still being validated. Do not rely on it. |
| 3.3 V system rail | Tested | |
| Switched user rail | Tested | Toggling it from Home Assistant powers the STEMMA QT port's device on and off. |
| Power Cycle Board (Home Assistant button) | Tested | |
| Ship mode, and waking with `SW3` | Tested | Works on battery power alone. With USB connected it does nothing, as the charger ignores it while an adapter is present. A brief tap of `SW3` does not wake the board; holding it does. |
| `SW3` held about 10 s to hard power-cycle | Tested | The board dropped off the API and reconnected. |

## Fuel gauge

| Feature | Status | Notes |
|---|---|---|
| Battery voltage and level | Tested | With a battery connected, after a driver fix for the state-of-charge reading. |
| Operation with no battery | Issue, fixed in design | The gauge blocked the internal I2C bus. It is now powered from the system rail. |
| Current-sense filter | Not yet tested | Added in the current design. |
| Temperature reading | Issue | Reads implausibly cold without a thermistor on its connector. |
| Learned capacity and calibration | Not yet tested | |

## Connectivity and programming

| Feature | Status | Notes |
|---|---|---|
| Flashing over the native USB port | Issue, fixed in design | Failed until the charger's USB data-line links were removed. They are now unpopulated by default. |
| Boot-mode and reset buttons | Tested | Used to enter download mode for the first flash. |
| Debug UART header | Not yet tested | |
| ESPHome, Wi-Fi and Home Assistant | Tested | |
| Over-the-air updates | Tested | |
| Internal I2C bus (`J6`) | Tested | Charger and gauge, and devices on the STEMMA QT port. |
| User I2C bus (`J203`) | Tested | Devices on the STEMMA QT port. |
| Differential I2C jacks (`J201`, `J202`) | Tested | Both jacks work with SparkFun QwiicBus EndPoint modules and the I2C devices attached to them. |
| SunSprout Satellite board | Not yet tested | The PCB is fabricated but not yet assembled. The same pattern has been tested with the off-the-shelf EndPoint it is based on. |
| Deep sleep and wake | Tested | Sleep current has not been measured. |
| Status LED | Issue, fixed in design | Too bright, so the series resistor was raised (untested). |

## Update this page

When a board from the current design is built, change the status of each item as it is tested,
and add the commit that was tested.

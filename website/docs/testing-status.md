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
| Reverse-polarity protection | Issue, fixed in design | On the prototype the protection FETs were mounted the wrong way round, so their body diodes would conduct on a reversed input. The current design turns them around. Do not connect a reversed supply to the prototype. |
| 3.3 V system rail | Tested | |
| Switched user rail | Tested | Toggling it from Home Assistant powers the STEMMA QT port's device on and off. |
| Power Cycle Board (Home Assistant button) | Tested | |
| Ship mode, and waking with `SW3` | Tested | Works on battery power alone. With USB connected it does nothing, as the charger ignores it while an adapter is present. A brief tap of `SW3` does not wake the board; holding it does. |
| `SW3` held about 10 s to hard power-cycle | Tested | The board dropped off the API and reconnected. |
| Running on battery alone | Not yet tested | Board keeps running with USB unplugged; battery current and time to empty look sensible. |
| End of charge | Not yet tested | Charging stops and "Battery Fully Charged" turns on. |
| Charge current setting | Not yet tested | Measured current follows "Charge Current Limit". Check board temperature at higher currents. |
| Input current limit | Not yet tested | A low "Input Current Limit" caps the input current while charging. |
| Charger shutdown mode | Not yet tested | On battery only, "Charger Shutdown" turns the board off and plugging in USB wakes it. |
| Charger temperature and thermal regulation | Not yet tested | "Charger Temperature" reads sensibly while charging. |
| Enable USB / Enable Solar Input switches | Not yet tested | Turning one off drops the board to the other source or the battery. |
| Charger HIZ mode | Not yet tested | The input stops supplying the board. |
| Charger status LED switch | Not yet tested | "Enable Charger Status LED" off turns the LED dark. |
| Reset Charger Registers | Not yet tested | The firmware restores its settings afterwards, including the charge voltage limit and the ship-FET setting. |
| Charger interrupt (`CHG_INT`) | Not yet tested | "Charger Interrupt" fires when USB is plugged or unplugged. |

## Fuel gauge

| Feature | Status | Notes |
|---|---|---|
| Battery voltage and level | Tested | With a battery connected, after a driver fix for the state-of-charge reading. |
| Operation with no battery | Issue, fixed in design | The gauge blocked the internal I2C bus. It is now powered from the system rail. |
| Current-sense filter | Not yet tested | Added in the current design. |
| Temperature reading | Issue | Reads implausibly cold without a thermistor on its connector. |
| Learned capacity and calibration | Not yet tested | Run the current and board offset calibrations with the pack at rest, and compare the gauge's battery current with the charger's. |
| Thermistors on `J302` and `J401` | Not yet tested | Both temperatures read sensibly, charging works with `ts_ignore` off, and the gauge stops reporting "Charge inhibited". |
| Fuel-gauge alert (`FG_ALERT`) | Not yet tested | An alert such as low charge fires, and can wake the board from deep sleep. |

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
| Deep sleep current | Not yet tested | Battery current while asleep. |
| Status LED | Issue, fixed in design | Too bright, so the series resistor was raised (untested). |
| Expansion headers (`J7`, `J8`) | Not yet tested | Unfitted by default. Check a GPIO and the 3.3 V pins once fitted. |
| `VCC_2` injection (`J2`) | Not yet tested | Cut `JP2`/`JP3`, inject through `J2`, and confirm it reaches the far end of the cable. |
| Wi-Fi range on the external antenna | Not yet tested | Signal at the real install distance. |

## Update this page

When a board from the current design is built, change the status of each item as it is tested,
and add the commit that was tested.

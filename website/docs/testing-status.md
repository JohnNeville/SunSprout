---
sidebar_position: 7
title: Testing status
---

import TestingStatus from '@site/src/components/TestingStatus';

# Testing status

A checklist of what has and hasn't been tested on real hardware. The first hub prototype was
built from commit [`1645733`](https://github.com/JohnNeville/SunSprout/commit/1645733). The
current design files include fixes for problems found on it, and that revision has not been
built yet.

| Status | Meaning |
|---|---|
| **Tested** | Worked on the prototype. |
| **Issue, fixed in design** | Failed or misbehaved on the prototype. The fix is in the current files but has not been tested on a board. |
| **Issue** | Misbehaves, with no fix yet. |
| **Not yet tested** | No result yet. |

Features not listed here have not been tested. Results for the SunSprout Satellite board are on the
[Satellite testing status](./satellite-testing-status.md) page.

<TestingStatus />

## Test hardware

Notes in the tables above point here with a superscript, such as <sup>LFP</sup>, where the hardware used made a
difference to the result.

| Ref | Item | Details |
|---|---|---|
| <a id="hw-lfp"></a>**LFP** | LiFePO4 cell | CBAK 26650FS4: 4000 mAh, 3.2 V nominal, 12.8 Wh. Charged to 3.6 V (the cell's charge cut-off), discharged to 2.75–2.8 V. |
| <a id="hw-li-ion"></a>**Li-ion** | Lithium-ion cells | Samsung INR18650-25R (2500 mAh, 4.2 V charge), a 2000 mAh cell, and earlier a 1200 mAh LiPo pouch. |
| <a id="hw-gauge"></a>**Gauge** | Fuel gauge | BQ34Z100-G1, firmware 0x0016, 10 mΩ sense resistor. TI's chemistry profile for each cell. On this firmware the LiFePO4 relax handling only switches on for chemistry IDs 0x04xx, so the CBAK profile is loaded under such an ID. |
| <a id="hw-load"></a>**Load** | LED load | 10 WS2812 LEDs on the user 3.3 V rail through a 5 V boost, about 0.75–1.1 A from the battery. |
| <a id="hw-bench"></a>**Bench** | Instruments | FNIRSI DPS-150 bench supply on the DC input; Nordic PPK2 as source meter for current measurements. |

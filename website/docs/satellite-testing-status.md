---
sidebar_position: 4
title: Satellite testing status
---

import TestingStatus from '@site/src/components/TestingStatus';

# Satellite testing status

A checklist of what has and hasn't been tested on the SunSprout Satellite board. The results so far
come from two prototype boards assembled by hand with reflow soldering, tested against the hub's
Qwiic port and its differential I2C jack. Hub results are on the [Testing status](./testing-status.md)
page.

| Status | Meaning |
|---|---|
| **Tested** | Worked on a prototype board. |
| **Issue, fixed in design** | Failed or misbehaved on a prototype. The fix is in the current files but has not been tested on a board. |
| **Issue** | Misbehaves, with no fix yet. |
| **Not yet tested** | No result yet. |

Features not listed here have not been tested.

<TestingStatus urlField="satelliteTestingStatusUrl" />

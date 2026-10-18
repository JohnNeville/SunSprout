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

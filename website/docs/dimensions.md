---
sidebar_position: 2
title: Dimensions & Mounting
---

# Dimensions & Mounting

Everything on this page is measured from the Rev 1.0 layout in
`hardware/hub/SunSproutHub.kicad_pcb`. If you need exact three-dimensional geometry — component
heights, connector bodies, mating-face positions — use the STEP model linked from
[Design Files](./design-files.md) rather than working from the numbers here.

## Board outline

| Property | Value |
|---|---|
| Outline | 56.0 × 85.0 mm |
| Thickness | 1.6 mm |
| Copper layers | 6 (`F.Cu`, `In1`–`In4`, `B.Cu`) |
| Corners | Square — no radius |
| Cutouts / notches | None |

The outline is a plain rectangle. There is no keying feature, so nothing stops the board going
into an enclosure the wrong way round — orient it by the connectors.

## Coordinate frame used here

All positions below are given in millimetres from the **top-left corner of the board, viewed
from the component (top) side**, with X increasing to the right and Y increasing downward. That
is the same orientation as the pinout drawing on [Pins & Signals](./pinout.md), and the same
convention KiCad itself uses, so numbers here can be compared directly against the design files.

## Mounting holes

Four holes, one near each corner, inset 5.0 mm from both adjacent edges:

| Hole | X | Y |
|---|---|---|
| Top-left | 5.0 | 5.0 |
| Top-right | 51.0 | 5.0 |
| Bottom-left | 5.0 | 80.0 |
| Bottom-right | 51.0 | 80.0 |

| Property | Value |
|---|---|
| Drill | Ø2.7 mm |
| Fastener | M2.5 |
| Plating | **Non-plated** |
| Hole pattern | 46.0 × 75.0 mm |

The holes are non-plated, so a metal standoff makes no electrical connection to the board — the
mounting points are not a ground path, and you cannot use them to bond the board to a chassis.
If your enclosure design needs that bond, take it from a ground pin on `J7` or `J8` instead.

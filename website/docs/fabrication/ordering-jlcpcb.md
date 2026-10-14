---
sidebar_position: 1
title: Order from JLCPCB
---

# Order the hub from JLCPCB

How to go from the GitHub repository to an assembled hub board, and what to check before you
pay. The design is drawn for JLCPCB's assembly service: the bill of materials uses LCSC part
numbers and the placement file uses JLCPCB's own column format.

:::warning[The current design has not been built yet]

The current board files fix problems found on the first prototype (commit
[`1645733`](https://github.com/JohnNeville/SunSprout/commit/1645733)), but that revision has
not been built, and not every feature has been bench-tested. See
[Testing status](../testing-status.md).

- **Order a small run first.** Build one and check the power path on the bench before ordering
  a panelised batch.
- **Power up with no battery attached** before you connect a cell.

## 1. Get the fabrication files

The gerbers, bill of materials and placement file are **not** committed to the repository. They
are built from the board file and attached to each tagged release.

1. Open the [Releases page](https://github.com/JohnNeville/SunSprout/releases) and pick a
   `hub-v…` release.
2. Download the three files for the hub:

| File | What it is |
|---|---|
| `GERBER-SunSproutHub_*.zip` | Gerbers and drill files for all six copper layers. |
| `BOM-SunSproutHub_*.csv` | Bill of materials with LCSC part numbers. |
| `CPL-SunSproutHub_*.csv` | Component placement list, in JLCPCB's column format. |

If there is no release for the revision you want, the release workflow can be run by hand from
the repository's Actions tab. To build the same files yourself, open
`hardware/hub/SunSproutHub.kicad_pcb` in KiCad and export with the
[Fabrication Toolkit](https://github.com/bennymeg/Fabrication-Toolkit) plugin.

:::note
`tools/generate-docs-assets.sh` is not part of ordering. It makes the board renders, pinout
diagrams and interactive BOM for this website.
:::

## 2. Board settings

Set these on JLCPCB's PCB options page after uploading the gerber zip.

| Setting | Value | Why |
|---|---|---|
| Layers | **6** | The board has six copper layers. A four-layer order will not match the files. |
| Board thickness | **1.6 mm** | The design stackup is 1.6 mm. |
| Copper weight | **1 oz** (0.035 mm) on every layer | What the design stackup assumes. Nothing on the board needs heavier copper. |
| Surface finish | **ENIG** | The board file specifies it. It suits the fine-pitch ICs and the module's ground pad. |
| Vias | Plain through-hole, **tented** | The design uses no blind, buried or micro vias, and tents both sides. |
| Board size | 56 × 85 mm | Check this against the size JLCPCB reads from the zip. |

Leave the stackup, impedance control and via-in-pad options at JLCPCB's defaults unless a
quote warning says otherwise.

## 3. Assembly settings

1. Turn on **PCB assembly**.
2. Upload `BOM-SunSproutHub_*.csv` and `CPL-SunSproutHub_*.csv`.
3. On the part-matching screen, check that every line has an LCSC part number and a stock
   count. A line with no match, or no stock, has to be fixed before the order can go ahead.

Not every part is assembled:

- The two **expansion headers** (the unfitted 9-pin headers beside the module) are excluded
  from the bill of materials and placement file on purpose. Solder a 2.54 mm header strip on
  yourself if you want them.
- The **`VCC_2 INJ` header** is also left unfitted.
- Every other connector (USB-C, solar terminal, battery, thermistors, STEMMA QT ports and the
  8P8C jacks) is part of the placement file. Check each one in the 3D view.

The BOM is tuned for small runs, with few distinct part numbers; see
[Design files](../design-files.md#a-note-on-the-bom).

## 4. Check the assembly preview before you pay

JLCPCB shows each placement in its component viewer before you confirm. Go through it
carefully, since a rotated part cannot be reworked after you pay:

- **IC pin 1.** Every IC's pin-1 dot in the viewer should line up with the pin-1 mark on the
  board. Pay particular attention to the charger, the fuel gauge, the buck-boost regulator,
  the load switch and the differential I2C buffer.
- **Diode and LED polarity.** The cathode bar or marking should match the silkscreen.
- **The ESP32-C5 module.** It is the `ESP32-C5-WROOM-1U-N8R8`, the version with a U.FL
  antenna connector. Check that it is centred on its pads and rotated as in the interactive
  BOM, with the U.FL connector on the side shown there.
- **The USB-C receptacle and the connectors.** Each should sit at the board edge in the
  same orientation as the render.
- **Parts shown as not placed** should be only the ones listed above.

Compare against the [interactive BOM](pathname:///ibom/), which shows every part on the board.
It is built from the files as of its last regeneration, so it can lag the latest commit.

## 5. After the boards arrive

Do not connect a battery yet. Follow [Getting started](../getting-started.md), which brings the
board up on USB power first.

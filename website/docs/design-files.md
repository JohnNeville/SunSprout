---
sidebar_position: 8
title: Design Files & Key Components
---

# Design Files & Key Components

![Board render, top view](../static/img/board-top.png)

![Board render, bottom view](../static/img/board-bottom.png)

## Key components

| Ref | Part | Function |
|---|---|---|
| U1 | ESP32-C5-WROOM-1U | Main MCU, Wi-Fi 6 / Bluetooth 5 / 802.15.4 / CAN FD radio module |
| U8 | BQ25798 | Li-ion/Li-Po battery charger |
| U3 | BQ34Z100 | Fuel gauge |
| U4 | TPS631000 | Buck-boost regulator, 3.3V system rail |
| U5 | TPS22918 | Load switch, switched 3.3V user rail |
| U201 | PCA9615 | Differential I2C buffer, drives the two 8P8C jacks |
| D5, U202 | USBLC6-4SC6-ES | USB-C and I2C-buffer ESD protection |
| Q1, Q2, D2 | MDD3415, DMP3098L-7, BZT52C12S | Reverse-polarity protection on the battery and DC/solar inputs; D2 clamps Q2's gate |

For why each of these parts was chosen, and why its surrounding passives have the values they
do, see the per-IC design notes in the repository's `docs/hub/modules/` folder.

## A note on the BOM

The bill of materials is optimised for **small-batch assembly**, not for volume production.

Assembly houses charge a one-off setup fee per distinct part number on top of each component's
per-unit price. On a run of tens of boards, that setup cost dominates — so this design
deliberately fits a higher-specified part where a cheaper one would do, whenever that part is
already used elsewhere on the board. All the 4.7 µF positions share one 25 V 0805 part, for
instance, even where 6.3 V would be sufficient.

That yields 61 distinct part numbers across 112 placements. If you intend to build this at
volume, revisit those choices: once per-unit cost dominates, fitting the cheapest adequate part
in each position is the cheaper answer. Nothing electrical depends on it.

## Downloads

Interactive viewers hosted with the documentation site:

- **[Hub Interactive BOM](pathname:///ibom/)** — inspect component placements, values, and LCSC part numbers directly on the Hub board layout.
- **[Satellite Interactive BOM](pathname:///ibom-satellite/)** — inspect component placements and solder jumper configurations on the Satellite board layout.

Published per release on the [Releases page](https://github.com/JohnNeville/SunSprout/releases):

- **Schematic PDFs** — full multi-sheet vector schematics for both boards (`SunSproutHub-schematic_*.pdf`, `SunSproutSatellite-schematic_*.pdf`), regenerated directly from the KiCad source files.
- **3D models (STEP)** — board mechanical models (`SunSproutHub_*.step`, `SunSproutSatellite_*.step`), including the MCU module and embedded connector geometry.
- **Gerbers, BOM, and pick-and-place** — ready-to-order JLCPCB fabrication archives.

Large build outputs (schematic PDFs, 19 MB STEP mechanical models, and fabrication zips) are attached directly to each release on GitHub rather than committed to the repository history or static web bundle.

Everything above is a build artifact of the KiCad source. Regenerate the local documentation assets with `tools/generate-docs-assets.sh`; Docker is the only prerequisite there, and no local KiCad install is needed. The fabrication set, STEP models, and schematic PDFs are built automatically by the Release artifacts workflow.


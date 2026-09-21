# Attribution & Licensing

## Third-party files used

These files are vendored directly into this project and actively used in the schematic/PCB;
their licenses require this credit.

These files keep their own licenses. They are **not** covered by this project's CERN-OHL-S v2
license, which applies to the design itself.

### Espressif KiCad Libraries

Source: [github.com/espressif/kicad-libraries](https://github.com/espressif/kicad-libraries).
License: **CC BY-SA 4.0**, © Espressif Systems.
Used for: the `ESP32-C5-WROOM-1U` MCU symbol and footprint
(`hardware/libraries/vendor/espressif-kicad-libraries/`), plus its 3D model, which is
embedded in the board file.

### SnapMagic Search (SnapEDA)

Source: [snapeda.com](https://www.snapeda.com/).
License: **CC BY-SA 4.0 with the Design Exception 1.0**, © SnapMagic and the respective
original authors.
Used for: the footprints and 3D models of `U8` (BQ25798), `U3` (BQ34Z100), and `J201`/`J202`
(8P8C jacks), and as the basis for `project:USB-C_TYPE-C-31-M-12`.

That last one is a modified derivative of SnapMagic's `SAMESKY_UJ20-C-H-G-SMT-2A-P16-TR`,
retargeted to the HRO `TYPE-C-31-M-12` connector this board actually uses. The twelve signal
pads were moved 0.15 mm toward the locating holes so they start exactly 0.50 mm from the hole
centres per HRO's drawing, and lengthened 0.10 mm for extra fillet. Slot and hole geometry are
unchanged. Being a derivative of CC BY-SA content, that footprint file remains CC BY-SA 4.0.

The [Design Exception
1.0](https://support.snapmagic.com/en/articles/2957815-what-is-the-design-exception-1-0)
permits combining these into a board design and conveying that combination under terms of
one's choice, which is what covers this project's schematic, PCB, board renders, and exported
STEP model. This credit is given because CC BY-SA applies to the content itself.

### CDFER JLCPCB KiCad Library

Source: [github.com/CDFER/JLCPCB-Kicad-Library](https://github.com/CDFER/JLCPCB-Kicad-Library).
License: **MIT**, Copyright (c) 2023 Chris.
Used for: the `C_0402` footprint and 3D model, used by thirteen 0402 capacitors.

This library is used in preference to KiCad's own `C_0402_1005Metric` because the stock
footprint's silkscreen does not meet JLCPCB's fabrication rules: its silk lines are 0.12 mm
wide, under JLCPCB's 0.15 mm minimum, and their inner edge lands on the pad rather than
clearing it. The CDFER library is built to JLCPCB's DFM rules, so it needs no per-part
rework.

MIT requires the copyright and permission notice to travel with the work:

> Permission is hereby granted, free of charge, to any person obtaining a copy of this
> software and associated documentation files (the "Software"), to deal in the Software
> without restriction… subject to the following conditions: The above copyright notice and
> this permission notice shall be included in all copies or substantial portions of the
> Software.

See the upstream `LICENSE` file for the full text.

### 3D models are embedded in the board

The `.kicad_pcb` carries its own copy of every 3D model, via KiCad's "Collect and Embed 3D
Models". The board therefore renders completely with no external library installed, and no
separate model files are stored in this repository.

Those models come from the three sources credited above, from KiCad's own bundled libraries,
and from `hardware/libraries/3dmodels/DB125-2.54-XXP-C-S.step`, drawn for this project and covered
by this repository's own CERN-OHL-S licence.

## Acknowledgments

Not a license requirement — credit given because it genuinely helped.

### PowerFeather

[PowerFeather's published ESP32-S3 board documentation](https://docs.powerfeather.dev/) was a
useful reference during early design — it helped surface the feature set and day-to-day
usability worth aiming for in an early prototype, motivated by the needs of a downstream
project ([esphome-garden-sensor](https://github.com/JohnNeville/esphome-garden-sensor)) this
board is ultimately going into. The circuit itself — component selection, values, and
connectivity — was implemented independently from each IC's own datasheet. No PowerFeather
schematic, board file, or library file is reproduced in this design.

## Datasheets are not redistributed

Manufacturer datasheets were used throughout to verify pinouts, absolute maximum ratings and
required external components, but none are included in this repository — they remain the
property of their respective manufacturers.

Each page under `docs/hub/modules/` names the exact part number it describes, so you can obtain
the datasheet from the manufacturer directly. Those pages are written to carry the reasoning
that the datasheets informed, so they stand on their own without them.

---
sidebar_position: 8
title: Attribution
---

# Attribution

The board design itself is licensed **CERN-OHL-S v2**, copyright John Neville. See
[Design Files](./design-files.md) for the source location.

The third-party content below keeps its own licence and is **not** covered by CERN-OHL-S.

## Espressif KiCad Libraries

Source: [github.com/espressif/kicad-libraries](https://github.com/espressif/kicad-libraries)
License: **CC BY-SA 4.0**, © Espressif Systems

Used for the `ESP32-C5-WROOM-1U` MCU symbol and footprint, plus its 3D model.

## SnapMagic Search (SnapEDA)

Source: [snapeda.com](https://www.snapeda.com/)
License: **CC BY-SA 4.0 with the Design Exception 1.0**, © SnapMagic and the respective
original authors

Used for the footprints and 3D models of `U8` (BQ25798), `U3` (BQ34Z100) and `J201`/`J202`
(the 8P8C jacks), and as the basis for the `USBC1` USB-C footprint.

That last one is a modified derivative: SnapMagic's Same Sky pattern, retargeted to the HRO
`TYPE-C-31-M-12` connector this board actually uses. The twelve signal pads were moved 0.15 mm
toward the locating holes to match HRO's drawing, and lengthened 0.10 mm. It remains CC BY-SA
4.0.

The [Design Exception
1.0](https://support.snapmagic.com/en/articles/2957815-what-is-the-design-exception-1-0)
permits combining this content into a board design and conveying that combination under terms
of one's choice — which is what covers this project's schematic, PCB, board renders and STEP
model. This credit is given because CC BY-SA still applies to the content itself.

## CDFER JLCPCB KiCad Library

Source: [github.com/CDFER/JLCPCB-Kicad-Library](https://github.com/CDFER/JLCPCB-Kicad-Library)
License: **MIT**, Copyright (c) 2023 Chris

Used for the `C_0402` footprint and 3D model, shared by thirteen 0402 capacitors.

It's used in preference to KiCad's own `C_0402_1005Metric` because the stock footprint's
silkscreen doesn't meet JLCPCB's fabrication rules — 0.12 mm lines against a 0.15 mm minimum,
with the inner edge landing on the pad instead of clearing it. The CDFER library is built to
JLCPCB's DFM rules.

MIT requires its notice to travel with the work:

> Permission is hereby granted, free of charge, to any person obtaining a copy of this software
> and associated documentation files (the "Software"), to deal in the Software without
> restriction… subject to the following conditions: The above copyright notice and this
> permission notice shall be included in all copies or substantial portions of the Software.

## 3D models are embedded in the board

The `.kicad_pcb` carries its own copy of every 3D model, so the board renders with no external
library installed. Those models come from the three sources credited above, from KiCad's own
bundled libraries, and from a STEP model drawn for this project.

## Acknowledgments

Not a licence requirement — a thank-you, because it genuinely helped.

[PowerFeather's published ESP32-S3 board documentation](https://docs.powerfeather.dev/) was a
useful reference during early design. It helped surface the feature set and day-to-day
usability worth aiming for in an early prototype, motivated by the needs of a downstream
project ([esphome-garden-sensor](https://github.com/JohnNeville/esphome-garden-sensor)) this
board is ultimately going into. The circuit itself was designed independently from each IC's
own datasheet, not adapted from PowerFeather's schematic, board files, or library files.

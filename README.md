# SunSprout

> [!WARNING]
> **Work in progress. This board has never been fabricated or tested.**
>
> Everything here has been verified only in software — ERC and DRC pass, pin assignments and
> component values are checked against manufacturer datasheets, and the fabrication outputs
> generate cleanly. No physical board exists. Nothing has been powered on, measured, or
> proven to work.
>
> It is published at this stage deliberately, to get design feedback before a fabrication run.
> Manufacturing and bring-up are intended; this page will say so once real measurements exist.
>
> **If you are thinking of building one:** treat it as an untested design, not a finished
> product. Expect to find mistakes. Errors in the charging or protection circuitry could damage
> a battery. Review it yourself before spending money on a panelised order.
>
> Feedback is genuinely welcome — especially on the power path, the charger and fuel-gauge
> configuration, and anything in [docs/hub/modules/](docs/hub/modules/) where the reasoning
> looks wrong.

An open-hardware solar and battery powered sensor system. SunSprout covers both halves of a
deployment: the **hub**, a custom board that manages power and talks to the network, and the
**remote sensors** that connect back to it over a long cable run.

The hub is the custom hardware in this project. The remote sensors are largely assembled from
existing modules, and are documented here so that a whole system can be reproduced rather than
inferred.

## The hub

A compact power-management and connectivity board built around the **ESP32-C5**. It takes power
from USB-C, a small DC or solar source, or a lithium battery. It charges the battery, regulates
a 3.3 V system rail, and exposes two independent I2C buses — one for its own power-management
ICs, and one for sensors, buffered onto a differential pair so it can drive a long cable.

| | |
|---|---|
| Documentation site | **[johnneville.github.io/SunSprout](https://johnneville.github.io/SunSprout/)** — pinout, connectors, power behaviour |
| Design files | [hardware/hub/](hardware/hub/) — KiCad 10 project, hand-routed |
| Why it is built this way | [docs/hub/modules/](docs/hub/modules/) — per-IC design notes |
| Firmware | [firmware/](firmware/) — ESPHome configuration; [docs/hub/firmware.md](docs/hub/firmware.md) for the reasoning |
| Off-board parts you need | [docs/hub/extra-components.md](docs/hub/extra-components.md) |

Every IC's datasheet-required external components are drawn directly into the schematic rather
than treated as black-box breakout modules. The schematic and PCB are maintained by hand in
KiCad; there is no generator producing them.

### Design decisions worth knowing up front

- **Two independent I2C buses.** An always-on internal bus carries the charger and the fuel
  gauge. A separate switched bus feeds the differential buffer that drives the two 8P8C jacks,
  plus its own STEMMA QT connector. A fault on a long external cable cannot stall the bus that
  reports the battery state.
- **Protection sized to what each port is for.** ESD/TVS on the ports meant to carry a cable
  off-board — the differential I2C lines on the 8P8C jacks, the USB-C data lines, and the USB
  `VBUS` rail. The STEMMA QT ports, GPIO headers and thermistor inputs have none, by design:
  they are for sensors inside the same enclosure. Reverse-polarity protection guards the
  battery and solar inputs, each sized to that input's real voltage range; USB-C gets none,
  being a keyed, spec-defined connector that cannot be connected backwards.
- **Alert lines go to their own GPIOs.** The charger and the fuel gauge each get a dedicated
  interrupt pin, so firmware reacts to a fault without polling, and without interrogating both
  devices to find which one raised it.
- **Connector families differ by role on purpose.** The battery and solar inputs use physically
  different connectors, so a solar source cannot be plugged into the battery input. The two
  thermistor inputs are a third family again, chosen to be field-terminable rather than
  requiring a pre-terminated probe.

## Remote sensors

Not yet documented. This is where the sensor-side build notes will live.

## Repository layout

```
.
├── hardware/
│   └── hub/                  # the hub's KiCad project, libraries, and SPICE decks
├── firmware/                 # ESPHome configuration for the hub
├── docs/
│   └── hub/
│       ├── modules/          # per-IC design notes: part choice, passive values, constraints
│       ├── firmware.md       # why the firmware is configured the way it is
│       └── extra-components.md
├── tools/                    # Dockerised KiCad CLI: validation, fab outputs, doc assets
└── website/                  # Docusaurus documentation site
```

## Documentation

The prose documentation is split by audience:

- **[docs/hub/modules/](docs/hub/modules/)** explains *why* the hub is built the way it is —
  why each part was chosen, and why its passives have the values and packages they do. Written
  for someone reading the design cold. Start at the [index](docs/hub/modules/README.md).
- **[docs/hub/firmware.md](docs/hub/firmware.md)** explains the firmware decisions — why the
  watchdog is off, why the charge voltage comes from the declared chemistry, and what the
  `SFET_PRESENT` bit unlocks. The configuration itself is in [firmware/](firmware/); the chip
  drivers live in [esphome-bq-drivers](https://github.com/JohnNeville/esphome-bq-drivers).
- **[website/](website/)** is the source for the user-facing documentation site, published at
  **[johnneville.github.io/SunSprout](https://johnneville.github.io/SunSprout/)**: pinout,
  connectors, power behaviour, and downloads.

Manufacturer datasheets are deliberately not redistributed here. Each design note names the
exact part number, so you can get the datasheet from the manufacturer.

## Building and validating

Docker is the only prerequisite. No local KiCad installation is required.

```bash
tools/run_kicad_validation.sh
```

```bash
tools/generate-docs-assets.sh
```

The first runs ERC and DRC. The second regenerates the board renders, schematic PDF, STEP
model, interactive BOM, and pinout diagram under `website/static/`. Re-run it after any
schematic or layout change, so that the published assets never go stale.

See [hardware/hub/README.md](hardware/hub/README.md) for what you can do with the KiCad project
without any extra setup, and which external libraries are optional.

## License

Copyright John Neville 2026.
This source describes Open Hardware and is licensed under the CERN-OHL-S v2.

You may redistribute and modify this source and make products using it
under the terms of the CERN-OHL-S v2 (https://ohwr.org/cern_ohl_s_v2.txt).

This source is distributed WITHOUT ANY EXPRESS OR IMPLIED WARRANTY,
INCLUDING OF MERCHANTABILITY, SATISFACTORY QUALITY AND FITNESS FOR A
PARTICULAR PURPOSE. Please see the CERN-OHL-S v2 for applicable conditions.

Source location: https://github.com/JohnNeville/SunSprout

See [LICENSE](LICENSE) for the full license text.

This design also vendors Espressif's official CC BY-SA 4.0 KiCad library for the ESP32-C5
module. See [NOTICE.md](NOTICE.md) for that credit and an acknowledgment of other technical
references consulted during design.

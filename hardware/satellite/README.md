# SunSproutSatellite — KiCad project

The satellite board's KiCad 10 project. Open `SunSproutSatellite.kicad_pro`.

This board is a differential-I2C endpoint: it terminates the far end of the cable coming
from a [SunSproutHub](../hub/), converts the differential pair back to standard I2C, and
reads four capacitive soil-moisture probes plus one 1-Wire soil-temperature probe. For the
design reasoning behind each part, see [docs/satellite/modules/](../../docs/satellite/modules/).

**Status: schematic-capture spec only.** The project files here are a scaffold — an empty
hierarchical schematic and an empty board outline, with the two custom parts the hub already
had to create copied in. No components are placed yet. See the plan this was built from for
the exact wiring spec (nets, part values, footprints) to key in by hand in the KiCad GUI.

## Layout

| Path | Contents |
|---|---|
| `SunSproutSatellite.kicad_sch` | Root/hierarchical top sheet |
| `sheets/` | Hierarchical sub-sheets (differential I2C endpoint, sensors) — currently empty |
| `SunSproutSatellite.kicad_pcb` | Board outline only — no layout yet |
| `SunSproutSatellite.kicad_dru` | Generic JLCPCB design rules (no board-specific power/zone rules — this board has no high-current path) |
| `libraries/` | Project-specific symbol library (footprints are all stock this board) |

## External library dependencies

Two parts have no stock KiCad equivalent and are copied in from the hub's own libraries
rather than referenced externally:

| Part | Symbol | Footprint |
|---|---|---|
| PCA9615 differential I2C buffer | `project:PCA9615DPZ` | `Snapeda:TSSOP10_SOT552-1_NXP-L` |
| 8P8C/RJ45 jack | `project:RJHSE5380_QwiicBusCompatible` | `Snapeda:AMPHENOL_RJHSE5380` |

Both footprints resolve externally via `KICAD_3RD_PARTY` the same way the hub's do (see
[hardware/hub/README.md](../hub/README.md#external-library-dependencies)) — or, simpler for
a board with only two such parts: place each once, then use KiCad's "Update PCB from
Schematic" so the footprint geometry gets embedded directly into this project's own files,
exactly as the hub does for every part once placed. After that, no external dependency
remains for either part.

Every other part on this board — the ADS1115 ADC, the DS2484 1-Wire bridge, the ESD
protection diode array, and all connectors — resolves from KiCad's own stock libraries with
zero setup.

## Regenerating the documentation assets

Not wired up yet for this board — see the plan's Phase 5 for what's needed. For now, this
board isn't part of `tools/generate-docs-assets.sh`'s output.

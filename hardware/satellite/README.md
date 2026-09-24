# SunSproutSatellite — KiCad project

The satellite board's KiCad 10 project. Open `SunSproutSatellite.kicad_pro`.

This board is a differential-I2C endpoint: it terminates the far end of the cable coming
from a [SunSproutHub](../hub/), converts the differential pair back to standard I2C, and
reads four capacitive soil-moisture probes plus one 1-Wire soil-temperature probe. For the
design reasoning behind each part, see [docs/satellite/modules/](../../docs/satellite/modules/).

**Status: Complete 4-layer PCB layout.** The project schematic and PCB layout are fully completed, featuring a 4-layer stackup (JLC04161H-7628), controlled-impedance differential I2C routing, dedicated inner reference planes (`In1.Cu` and `In2.Cu`), ESD protection, cable power decoupling, and complete DFM rule verification with 0 DRC violations.

## Layout & Architecture

| Path | Contents |
|---|---|
| `SunSproutSatellite.kicad_sch` | Root hierarchical schematic |
| `sheets/i2c_endpoint_v1.kicad_sch` | Differential I2C endpoint, PCA9615 buffer, termination array, cable power entry, power status LED (LED1), cut jumper (JP19), and headers J1, J7, J8, J9 |
| `sheets/adc_sensors_v1.kicad_sch` | ADS1115 16-bit 4-channel ADC, JST PH moisture probe headers (J2–J5), and address jumper JP1 |
| `sheets/onewire_v1.kicad_sch` | DS2482S-100+ I2C to 1-Wire bridge, JST PH probe header (J6), and bit-weighted address jumper JP16 |
| `SunSproutSatellite.kicad_pcb` | Completed 4-layer PCB layout (27.25 mm × 51.10 mm) with inner ground/power planes |
| `SunSproutSatellite.kicad_dru` | Custom JLCPCB 4-layer design rules (clearances, trace widths, track angles, and annular rings) |
| `../libraries/` | Project-specific symbol & footprint library (shared with Hub) |

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

Documentation assets (3D board renders, interactive BOM, and interactive pinout SVGs) are generated via `tools/generate-docs-assets.sh`. The generated assets live under `website/static/` and `website/static/img/`. Release assets (schematic PDFs, STEP models, and fabrication zips) are produced by the release workflow.

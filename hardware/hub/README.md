# SunSproutHub — KiCad project

The hub board's KiCad 10 project. Open `SunSproutHub.kicad_pro`.

For the design reasoning behind each IC and its passives, see [docs/hub/modules/](../../docs/hub/modules/).

## Layout

| Path | Contents |
|---|---|
| `SunSproutHub.kicad_sch` | Root/hierarchical top sheet |
| `sheets/` | Hierarchical sub-sheets (charger, fuel gauge, regulator, user I2C) |
| `SunSproutHub.kicad_pcb` | Board layout, hand-routed |
| `SunSproutHub.kicad_dru` | Custom design rules |
| `../libraries/` | Project-specific and vendored symbol/footprint libraries (shared with Satellite) |
| `spice_models/` | ngspice decks used to verify the reverse-polarity FETs |

## What you can do without any extra setup

KiCad writes the full geometry of every symbol and footprint directly into the
`.kicad_sch` and `.kicad_pcb` files at placement time. The schematic and the board are
therefore self-contained. After cloning you can open both, run ERC and DRC, inspect every
part, and export gerbers and a pick-and-place file, with no libraries beyond the ones KiCad
ships with.

## External library dependencies

**3D models are not external.** The board file carries an embedded copy of every 3D model
(KiCad's "Collect and Embed 3D Models"), so the board renders completely with nothing
installed.

Footprints are mostly in-repo too. Three library entries still resolve outside it, and they
are only consulted when you update a footprint *from its library* — not to open, review,
render, or fabricate the board, because the geometry is already in the board file.

| Library | Resolves via | Parts |
|---|---|---|
| `Snapeda` | `KICAD_3RD_PARTY` | `J201`, `J202`, `U3`, `U8`, `U4`, `U5`, `U201`, `D5`, `U202`, `Q301`-`Q304` |
| `PCM_JLCPCB` | PCM package ([CDFER](https://github.com/CDFER/JLCPCB-Kicad-Library), MIT) | The 0402 capacitors |
| `PCM_SparkFun-Connector` | PCM package | The 13 test points |
| `PCM_Capacitor_SMD_AKL` | PCM package | `C17` only, which is DNP and not fitted |

If KiCad reports these as missing, the board is still correct. To silence the warnings,
install the matching PCM packages and point `KICAD_3RD_PARTY` at your own third-party library
directory, or remove the unused entries from `fp-lib-table`.

The `USBC1` USB-C footprint and the `CN5` screw terminal are project footprints, in
`../libraries/footprints/project.pretty/`. The Espressif module's footprint and 3D model are
vendored under `../libraries/vendor/`.

### A note on licensing

Every library this design still depends on has stated terms: SnapEDA is CC BY-SA 4.0 with the
Design Exception 1.0, CDFER's library is MIT, and Espressif's is CC BY-SA 4.0. All three are
credited in [NOTICE.md](../../NOTICE.md). Earlier revisions used EasyEDA/LCSC content, whose
redistribution terms are not published; it has since been replaced throughout and no longer
appears in the design or the embedded model set.

## Regenerating the documentation assets

The board renders, schematic PDF, STEP model, interactive BOM, and pinout SVG under
`website/static/` are all build artifacts of the files here. Regenerate them from the
repository root after any schematic or layout change:

```bash
tools/generate-docs-assets.sh
```

Docker is the only prerequisite. No local KiCad installation is required.

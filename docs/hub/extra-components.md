# Extra / Off-Board Components

Hardware that isn't part of this board's own BOM but is required (or optional) for the design
to work as intended — things you need to source and wire in separately, usually onto the
battery pack itself.

## J302 — charger thermistor input (BQ25798 TS)

- **Connector:** JST PA 2-pin, side entry (`S02B-PASK-2`, LCSC `C265094`), net `TS_NODE`/GND,
  biased on-board from the charger's `REGN` rail by the R305/R306 divider (5.1kΩ / 30kΩ).
- **Required part:** a **Semitec 103AT-11 NTC thermistor (10kΩ @ 25°C, B25/85 = 3435 K)**
  mounted directly on/against the battery cell.
- **Purpose:** feeds BQ25798's TS pin for JEITA charge-temperature qualification (charger
  won't fast-charge outside its configured safe temperature window without this).
- **Status:** intended, not yet physically sourced/mounted.

## J401 — fuel gauge thermistor input (BQ34Z100 TS)

- **Connector:** JST PA 2-pin, side entry (`S02B-PASK-2`, LCSC `C265094`), net `FG_TS_NODE`,
  biased from the gauge's own `REG25` rail (the IC's internal pull-down means no external bias
  resistor is needed here).
- **Required part:** a second, separate **Semitec 103AT-11 NTC thermistor (10kΩ @ 25°C,
  B25/85 = 3435 K)**, also mounted on/against the battery cell.
- **Purpose:** lets BQ34Z100 read pack temperature directly in hardware via its TH pin, instead
  of firmware having to compute temperature elsewhere and write it into the fuel gauge's
  Temperature register over I2C. This was a deliberate choice to keep temperature reporting out
  of firmware.
- **Why a separate thermistor from J302, not a shared one:** BQ25798 and BQ34Z100 each apply
  their own excitation/bias to whatever's on their thermistor pin — sharing one physical NTC
  between two active bias circuits would give both ICs a bad reading. Two independent 103AT-11
  units (both mounted at the same physical location on the cell) is the correct approach.
- **Status:** intended, not yet physically sourced/mounted.

## J4 — main battery connector

- **Connector:** JST PH 2-pin (`Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal`),
  labeled "BATTERY" in the schematic.
- **Required part:** the Li-ion/Li-Po battery pack itself (cell + any pack-level protection),
  sourced separately — standard JST-PH 2-pin battery cable.
- **Status:** external to this board by design; no action needed here beyond having a pack with
  a matching JST-PH connector.

## J7 / J8 — expansion headers (optional)

- **Connectors:** 2.54mm pin headers (1x08 and 1x10), both marked DNP — the board ships without
  them.
- **Required part:** standard 2.54mm pin header strip, hand-soldered, only if you want the free
  GPIOs or the debug UART broken out. See [docs/modules/esp32-c5-mcu.md](modules/esp32-c5-mcu.md)
  for which pins land where, and which of them are strapping pins.
- **Status:** optional, not needed for the board to function.

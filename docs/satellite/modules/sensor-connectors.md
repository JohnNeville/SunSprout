# Sensor connectors

| Reference | Part | Function |
|---|---|---|
| `J2`–`J5` | JST PH 2.0mm, 3-pin | Capacitive soil-moisture probe (DFRobot SEN0193 / "Gravity" interface) |
| `J6` | JST PA 2.0mm, 3-pin | 1-Wire soil-temperature probe (DS18B20) |

All five connectors are internal pigtail points, not field connectors. Each probe's own
waterproof cable exits the enclosure through a separate weatherproof gland or connector,
which is the user's own choice and outside the scope of this board — the same split the hub
already uses for its own thermistor inputs (`J302`/`J401`).

## Moisture-sensor connectors (`J2`–`J5`)

The sensor uses the standard DFRobot Gravity PH2.0-3P interface:

| Pin | Function | Net / Destination | Wire Color |
|---|---|---|---|
| 1 | `GND` | `GND` | Black |
| 2 | `VCC` | `SAT_3V3` | Red |
| 3 | `Signal` | `MOIST1`–`MOIST4` (ADS1115 `AIN0`–`AIN3`) | Blue / Green / Yellow |

Each connector's `Signal` pin goes to its own ADS1115 channel — see
[ADS1115 ADC](ads1115-adc.md#channel-assignment) for the mapping. `VCC` and `GND` bus in
parallel across all four connectors to `SAT_3V3`/`GND`.

No ESD protection on these connectors — matching the hub's own rule and its own precedent
(`J302`/`J401` get none either): protection is for connectors that carry a cable off-board
to another circuit board, not for a same-enclosure field-wired sensor lead.

## Temperature-probe connector (`J6`)

3-pin JST PA (`SAT_3V3`/`GND`/`ONEWIRE_DQ`), matching the hub's own thermistor-probe connector
family. See [DS2482 1-Wire bridge](ds2482-1wire-bridge.md) for the pin wiring.

### Terminating your own probe cable

`J6` is a JST PA 2-pin side-entry header family, extended to 3 circuits. To make up a probe
cable, following the same parts the hub's own thermistor probes use (see
[Connectors — Terminating your own thermistor probe](../../../website/docs/connectors.md#terminating-your-own-thermistor-probe)),
but in the 3-circuit housing:

| Part | Number | Notes |
|---|---|---|
| Housing | `PAP-03V-S` | 3-circuit, latching — the 3-circuit sibling of the hub's 2-circuit `PAP-02V-S` |
| Crimp contact | `SPHD-001T-P0.5` | Same crimp as the hub's thermistor probes, AWG 28–22 |
| Board connector | `S03B-PASK-2` | JLCPCB/LCSC `C265095` |

A generic waterproof DS18B20 probe typically ships with three loose or lightly-jacketed
leads (`VDD`, `GND`, `DQ`) rather than a pre-terminated connector — crimp them into the
housing above in the order that matches this connector's pinout.

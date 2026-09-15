# User-rail load switch — TPS22918

| Item | Value |
|---|---|
| Reference | `U5` |
| Part | Texas Instruments TPS22918DBVR |
| Package | SOT-23, 6 pin |
| Schematic sheet | `sheets/TPS631000_PowerRegulation_v2.kicad_sch` |

## Function

The load switch makes the 3V3_USER rail from the 3V3_SYS rail. Firmware controls the switch. The
rail supplies the differential I2C buffer, the `J203` port and the ESD protection part on that
side.

## Why the board has a second rail

The differential I2C buffer draws current whenever it has power. Remote sensors on the 8P8C
jacks also draw current. A board that sleeps for long periods must not pay that cost when it
does not use the bus.

A load switch lets firmware remove power from that whole group. The MCU, the charger and the
fuel gauge stay on the always-on 3V3_SYS rail, so the board keeps charging and keeps its state
of charge while the user rail is off.

## Control

| Reference | Value | Function |
|---|---|---|
| `R23` | 100 kΩ | Pull-down on the `ON` pin. |

The `ON` pin connects to GPIO23 on the MCU and to `R23`.

`R23` holds the `ON` pin low while the MCU is in reset. The rail therefore defaults to off at
power-up. Firmware must drive GPIO23 high to enable the rail. This order is deliberate: an
unprogrammed board must not power a bus that nothing controls.

## Rise-time capacitor — C17

| Item | Value |
|---|---|
| Reference | `C17` |
| Footprint | 0805 |
| Status | **DNP. The board ships without this capacitor.** |

The `CT` pin sets the output slew rate. A capacitor on this pin makes the output rise more
slowly. A slower rise reduces the inrush current when the rail turns on.

The board ships with no capacitor here, so the switch uses its own default rise time. The
footprint stays on the board as a tuning point. If a future load draws too much inrush current
at turn-on, a capacitor can be fitted here without a board change.

No value is given, because the correct value depends on the real load. Measure the inrush
current first, then choose the value.

## Output discharge

The `QOD` pin connects to the `VOUT` pin. This is the connection that the datasheet describes.
It discharges the output rail through the internal discharge path when the switch turns off.

Without this connection the output rail floats after turn-off. Downstream devices then power
down slowly and unpredictably.

## Input decoupling

| Reference | Value | Function |
|---|---|---|
| `C19` | 1 µF | Input decoupling at `VIN`. |

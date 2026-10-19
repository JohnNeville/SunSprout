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

### Firmware must switch the rail on before it sets up the user I2C bus

With the rail off, `R201` and `R202` pull the user bus lines up to a rail that the load switch is
holding at 0 V, so both lines sit low. Firmware that sets up the bus in that state and only then
switches the rail on can find that the chips on the bus do not come up.

This was seen on a prototype waking from deep sleep with a satellite attached. The ESPHome hub
package turned the rail on after it had set up the user bus. On every wake the ADS1115 failed its
setup, which ESPHome treats as permanent for that boot, and the DS2482 1-Wire probe was never read.
No sensor on the satellite reported for the whole awake period, although the same chips answered an
address scan a few seconds later. Switching the rail on first, then setting up the bus, fixed it. The exact mechanism inside the ESP32 I2C driver was not isolated.

The chips themselves are quick. With the rail off for 1.5 s, each of the four satellite chips
answered a real register read 13 to 16 ms after the rail came on, in ten of ten cycles.

Components that sit on the user bus need to set up after it. Most ESPHome I2C devices do (they set up
at priority 600, after the bus at 700), but the DS2484 1-Wire bridge sets up at priority 999 by
default, before the bus and before the rail. On the satellite test the bridge then reported "1-wire
bus is held low" and found no devices, so no temperature probe was read, while the ADS1115 beside it
worked. Give the bridge a `setup_priority` below 700 (the test used 500, which leaves time for the
satellite to power up) and the Dallas sensors one below that (450).

The hub firmware does this through ESPHome's setup order. The rail switch is `ALWAYS_ON`, so it is
switched on when the switch is set up (priority 800), and the user bus has a later `setup_priority`
of 700 in `sunsprout-hub.yaml`. If you write your own firmware, drive `GPIO23` high before you
initialise the user I2C bus (`GPIO9` and `GPIO10`), and leave at least 20 ms before the first
transfer.

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

## Output decoupling

| Reference | Value | Function |
|---|---|---|
| `C18` | 100 nF | Decoupling at `VOUT`, on the 3V3_USER rail. |

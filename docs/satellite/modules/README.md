# Per-IC design notes

This folder explains the design decisions for each integrated circuit on the satellite
board. Each page covers one IC and the passive components that belong to it.

These pages tell you *why* the design uses a part or a value. They do not repeat the
manufacturer datasheets. The board does not include the datasheets. Each page gives the exact
part number, so you can get the datasheet from the manufacturer.

See [docs/hub/modules/](../../hub/modules/) for the hub's own per-IC notes. This satellite
is the far end of the cable the hub's differential I2C buffer drives — several design
decisions here are direct mirrors, or direct contrasts, of decisions made there.

## Writing style

These pages use ASD-STE100 Simplified Technical English. Sentences are short. Each sentence
gives one idea. The text uses the active voice and one term for each concept.

## Reference terms

| Term | Meaning |
|---|---|
| `SAT_3V3` | This board's local 3.3V rail. In default direct mode, it is bridged to the cable's `RJ45_VCC_1` rail via solder jumper `JP18`. For long cable runs, it can be powered by an external buck converter connected between headers `J7` and `J9`. |
| `SDA_LOCAL` / `SCL_LOCAL` | The single-ended I2C bus on this board's own side of the PCA9615. The ADS1115 and the DS2482S-100+ both sit on this bus. |
| `ADDR_SEL` | The ADS1115's address-select pin, net-named separately from `SDA_LOCAL`/`SCL_LOCAL` because it is solder-jumpered to one of four different straps, not fixed to one net. |
| `ONEWIRE_DQ` | The single 1-Wire data line between the DS2482S-100+ and the temperature probe connector. |
| DNP | Do not populate. The part is on the schematic and the layout, but the board ships without it. |

## Pages

| Page | Reference | Part |
|---|---|---|
| [Differential I2C endpoint](pca9615-i2c-endpoint.md) | `U1` | PCA9615DPZ |
| [ADS1115 ADC](ads1115-adc.md) | `U2` | ADS1115IDGSR |
| [DS2482 1-Wire bridge](ds2482-1wire-bridge.md) | `U3` | DS2482S-100+ |
| [Sensor connectors](sensor-connectors.md) | `J2`–`J6` | — |

# Net connection reference

Every planned component on the satellite board and what it connects to, by net — not by
specific pin number. Use this as the wiring checklist when hand-connecting components in
the KiCad schematic editor. Pin *names* (not numbers) are given so you can match them
against each part's own pinLabels/datasheet.

## Sheet 1 — Differential I2C Endpoint (`sheets/i2c_endpoint_v1.kicad_sch`)

| Net | Connects |
|---|---|
| `SAT_3V3` | JP14.pin2, U1.VDDA, U1.EN, U1.VDDB, U4.VBUS, C1.pin1, C2.pin1, C3.pin1, C6.pin1, JP11.pin1, R3.pin1, R6.pin1 |
| `VCC_1` | J1.VCC_1, JP14.pin1 |
| `VCC_2` | J1.VCC_2, JP14.pin3, J7.pin1 |
| `GND` | J1.BLUE_N, JP13.pin2, JP15.pin1, U1.VSS, U4.GND, C1.pin2, C2.pin2, C3.pin2, C6.pin2, R5.pin2, R8.pin2 |
| `GND_2` | J1.GRN_N, JP15.pin2, J7.pin2, J7.pin3, J7.pin4 |
| `SHIELD` | J1.SHIELD1, J1.SHIELD2, JP13.pin1 |
| `SDA_LOCAL` | U1.SDA, R2.pin2 *(continues to Sheet 2: U2.SDA, and Sheet 3: U3.SDA)* |
| `SCL_LOCAL` | U1.SCL, R1.pin2 *(continues to Sheet 2: U2.SCL, and Sheet 3: U3.SCL)* |
| *(Dual Pull-up)* | JP11.pin1 (SAT_3V3) → JP11.pin2 → R1.pin1 (SCL), JP11.pin1 → JP11.pin3 → R2.pin1 (SDA) |
| `DSCL_N` | J1.DSCL_N, U1.DSCLM, U4.IO2, R4.pin2, R5.pin1 |
| `DSCL_P` | J1.DSCL_P, U1.DSCLP, U4.IO1, R3.pin2, R4.pin1 |
| *(DSCL termination)* | SAT_3V3 → R3.pin1, R3.pin2 ↔ R4.pin1 (DSCL_P), R4.pin2 ↔ R5.pin1 (DSCL_N), R5.pin2 → GND |
| `DSDA_N` | J1.DSDA_N, U1.DSDAM, U4.IO4, R7.pin2, R8.pin1 |
| `DSDA_P` | J1.DSDA_P, U1.DSDAP, U4.IO3, R6.pin2, R7.pin1 |
| *(DSDA termination)* | SAT_3V3 → R6.pin1, R6.pin2 ↔ R7.pin1 (DSDA_P), R7.pin2 ↔ R8.pin1 (DSDA_N), R8.pin2 → GND |

Notes:
- `DSCL_N`/`DSCL_P`/`DSDA_N`/`DSDA_P` termination is a resistor divider ladder directly across the differential pairs.
- C1 is the bulk reservoir cap; C2/C3/C6 are 100nF decoupling for U1's two supply pins and U4 respectively.

## Sheet 2 — ADC Soil Moisture Sensors (`sheets/adc_sensors_v1.kicad_sch`)

| Net | Connects |
|---|---|
| `SAT_3V3` | U2.VDD, C4.pin1, J2.pin2, J3.pin2, J4.pin2, J5.pin2, JP1.pin3 |
| `GND` | U2.GND, C4.pin2, J2.pin1, J3.pin1, J4.pin1, J5.pin1, JP1.pin2 |
| `SDA_LOCAL` | U2.SDA, JP1.pin4 *(continues from Sheet 1: U1.SDA)* |
| `SCL_LOCAL` | U2.SCL, JP1.pin5 *(continues from Sheet 1: U1.SCL)* |
| `ADDR_SEL` | U2.ADDR, JP1.pin1 |
| `MOIST1` | U2.AIN0, J2.pin3 |
| `MOIST2` | U2.AIN1, J3.pin3 |
| `MOIST3` | U2.AIN2, J4.pin3 |
| `MOIST4` | U2.AIN3, J5.pin3 |
| — (not connected) | U2.ALERT (NC) |

Notes:
- `SDA_LOCAL`/`SCL_LOCAL` are the *same* nets as on Sheet 1 and Sheet 3 — one shared I2C bus across
  the satellite board, tying together U1, U2, and U3.
- Address-select jumper: `JP1` is a unified 4-way solder jumper (`project:SolderJumper_4_Bridged12`).
  Pin 1 (`ADDR`) is bridged to Pin 2 (`GND`, address `0x48`) by default. Cut trace 1-2 and bridge
  1-3 for `0x49`, 1-4 for `0x4A`, or 1-5 for `0x4B`. See [ads1115-adc.md](ads1115-adc.md).

## Sheet 3 — 1-Wire Temperature Interface (`sheets/onewire_v1.kicad_sch`)

| Net | Connects |
|---|---|
| `SAT_3V3` | U3.VCC, C5.pin1, R9.pin1, J6.pin1, JP16.pin3, JP17.pin3 |
| `GND` | U3.GND, C5.pin2, J6.pin2, JP16.pin1, JP17.pin1 |
| `SDA_LOCAL` | U3.SDA *(continues from Sheet 1: U1.SDA)* |
| `SCL_LOCAL` | U3.SCL *(continues from Sheet 1: U1.SCL)* |
| `AD0_SEL` | U3.AD0, JP16.pin2 |
| `AD1_SEL` | U3.AD1, JP17.pin2 |
| `ONEWIRE_DQ` | U3.IO, J6.pin3, R9.pin2 |
| — (not connected) | U3.~PCTLZ (pin 6, NC) |

Notes:
- `JP16` (AD0) and `JP17` (AD1) are 3-pad solder jumpers bridged 1-2 to `GND` by default, setting the DS2482S-100+ address to `0x18`.
- `R9` is a DNP (Do Not Populate) 4.7kΩ 0603 passive pull-up footprint on `ONEWIRE_DQ` to `SAT_3V3`. It is unpopulated by default because DS2482S-100+ contains an internal active pull-up.

## All components, by reference

| Ref | Part | Description | Sheet |
|---|---|---|---|
| J1 | RJHSE5380 | 8P8C jack | 1 |
| U1 | PCA9615DPZ | Diff-I2C buffer | 1 |
| U4 | USBLC6-4SC6 | ESD protection | 1 |
| C1 | 22µF | Bulk cap | 1 |
| C2, C3, C6 | 100nF | Decoupling | 1 |
| R1, R2 | 4.7kΩ | I2C pull-ups | 1 |
| R3, R5, R6, R8 | 390Ω | Termination bias resistors | 1 |
| R4, R7 | 100Ω | Termination line matching resistors | 1 |
| JP11 | SolderJumper_3_DualPullUp_Bridged | Single-cut dual I2C pull-up jumper (bridged) | 1 |
| JP13 | SolderJumper_2_Bridged | Cable shield to GND cut jumper (bridged) | 1 |
| JP14 | SolderJumper_3_Bridged12 | Power source select solder jumper (3-way, 1-2 bridged) | 1 |
| JP15 | SolderJumper_2_Bridged | Cable GND_2 to GND bridge jumper (bridged) | 1 |
| J7 | Conn_01x04 | Auxiliary 2.54mm pin header (VCC_2, GND_2 x3) | 1 |
| U2 | ADS1115IDGS | 16-bit 4-ch ADC | 2 |
| C4 | 100nF | ADS1115 Decoupling | 2 |
| J2–J5 | Conn_01x03 | Moisture sensor connectors (JST PH) | 2 |
| JP1 | SolderJumper_4_Bridged12 | 4-way address-select jumper block (bridged 1-2 default) | 2 |
| U3 | DS2482S-100+ | I2C to 1-Wire bridge (SOIC-8) | 3 |
| C5 | 100nF | DS2482S-100+ Decoupling | 3 |
| R9 | 4.7kΩ | 1-Wire pull-up (DNP) | 3 |
| J6 | Conn_01x03 | 1-Wire probe connector (JST PA) | 3 |
| JP16, JP17 | SolderJumper_3_Bridged12 | DS2482S-100+ address-select jumpers (1-2 bridged to GND) | 3 |

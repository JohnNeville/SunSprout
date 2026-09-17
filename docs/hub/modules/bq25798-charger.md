# Battery charger — BQ25798

| Item | Value |
|---|---|
| Reference | `U8` |
| Part | Texas Instruments BQ25798RQMR |
| Package | QFN-29, 4 x 4 mm, 0.4 mm pitch |
| Schematic sheet | `sheets/bq25798_charger_v2.kicad_sch` |

## Function

The BQ25798 is a buck-boost battery charger. It accepts two power inputs. It charges one
lithium cell. It also supplies the SYS rail that feeds the rest of the board.

## Why this part

The board must accept USB-C power and a solar or DC source at the same time. It must also
charge the battery from either source.

The BQ25798 has an integrated dual-input multiplexer. The `VAC1` and `VAC2` pins select the
input. This removes the need for a separate OR-ing IC and its support parts. A separate OR-ing
stage was the earlier approach. The integrated multiplexer is simpler and uses less board area.

The part also gives an internal ADC. The ADC measures the input voltage, the input current, the
battery voltage and the battery current. These measurements replaced a separate power monitor
IC that an earlier design used.

## Input multiplexer FETs — Q301 to Q304

| Reference | Part | Function |
|---|---|---|
| `Q301`, `Q302` | AO3400A | USB input path. The `ACDRV1` pin drives both gates. |
| `Q303`, `Q304` | AO3400A | Solar and DC input path. The `ACDRV2` pin drives both gates. |

Each input uses two N-channel MOSFETs in a back-to-back pair. The two sources connect together.
This arrangement blocks current in both directions when the charger turns the input off. A
single FET cannot do this, because its body diode conducts in one direction.

The charger controls the input selection completely. An earlier version of this circuit also had
clamp diodes on the two inputs. The datasheet confirms that source selection is FET-based only.
The clamp diodes did nothing, so the design removed them.

## Ship FET — Q3

| Item | Value |
|---|---|
| Reference | `Q3` |
| Part | AO3400A, N-channel, SOT-23 |
| Gate | `SDRV_NODE`, from the `SDRV` pin |
| Source | `VBAT`, the system side |
| Drain | `VBAT_PROTECTED`, the pack side |

`Q3` is the ship FET. It sits in series in the battery path, between the reverse-polarity FET
`Q1` and the charger `BAT` pins. The charger opens `Q3` to disconnect the pack from the board.
The battery path is therefore `VBAT_RAW` → `Q1` → `VBAT_PROTECTED` → `Q3` → `VBAT`.

The `SDRV` pin is a gate-driver output. An internal charge pump drives the gate to about 5 V
above the battery voltage. The absolute maximum voltage from `SDRV` to `BAT` is 6 V. The AO3400A
is rated at ±12 V gate-to-source, so it keeps a large margin.

Read the on-resistance from the 4.5 V gate-voltage column of the AO3400A datasheet. That value
is about 32 mΩ. Do not read the 10 V column. The charge pump never reaches 10 V above the
battery.

`Q3` uses the same AO3400A part as the four input-multiplexer FETs. This adds no new part number
to the bill of materials.

### Why the design added a ship FET

An earlier revision had no ship FET. It fitted `C319`, a 1 nF capacitor, from `SDRV` to ground.
That is the no-ship-FET variant in the datasheet. Ship mode, shutdown mode and the system power
reset were all unavailable in that revision. The design deleted `C319` and fitted `Q3`. See
[Ship mode, shutdown mode and the system power reset](#ship-mode-shutdown-mode-and-the-system-power-reset).

## Configuration resistors

| Reference | Value | Pin | Function |
|---|---|---|---|
| `R301` | 3.0 kΩ | `PROG` | Sets the power-on default cell count to 1S. Also selects the 1.5 MHz switching frequency. The IC reads this resistor only at power-on reset. |
| `R302` | 110 kΩ | `ILIM_HIZ` | Upper leg of the input-current-limit divider from `REGN`. |
| `R303` | 130 kΩ | `ILIM_HIZ` | Lower leg of the same divider to ground. |
| `R304` | 100 Ω | `BATP` | Series isolation resistor on the battery-voltage sense input. The datasheet pin description requires it. |
| `R305` | 5.1 kΩ | `TS` | Upper leg of the thermistor bias divider from `REGN`. |
| `R306` | 30 kΩ | `TS` | Lower leg of the thermistor bias divider to ground. |

### The hardware input-current limit

`R302` and `R303` set a hardware limit on the input current. The charger enforces it as an
analog ceiling. Firmware cannot exceed it through the I2C registers.

The limit is not one fixed number. The charger derives it from the `ILIM_HIZ` pin voltage as

```
V(ILIM_HIZ) = 1 V + 800 mOhm * I
```

and the divider sets that voltage as a fraction of `REGN`: 130 k / (110 k + 130 k) = 0.542.
`REGN` is not fixed either. Its typical value is 4.8 V with a 5 V input and 5.0 V with a 15 V
input, specified over 4.6 V to 5.2 V.

| Input | `REGN`, typical | `V(ILIM_HIZ)` | Limit |
|---|---|---|---|
| USB-C at 5 V | 4.8 V | 2.600 V | 2.00 A |
| Solar or DC at 15 V | 5.0 V | 2.708 V | 2.14 A |
| Full `REGN` spec | 4.6 V to 5.2 V | 2.49 V to 2.82 V | 1.87 A to 2.27 A |

The divider was sized for the 5 V case. A high-voltage input therefore raises the ceiling about
7% above 2 A, and worst-case silicon reaches 2.27 A.

The board copper for the `PMID`, `SYS`, `SW1`, `SW2` and `BAT` nets carries 2 A. The IC itself
allows up to 5 A. The divider brings the hardware close to the copper rating, but not below it
in every case — size the copper against 2.27 A, not against 2.00 A.

The charger reads this pin with its ADC once, at power-on, before the converter starts
switching. Whichever source is present at power-up therefore fixes the clamp for that session.

### Firmware constraint on the charge current

The charge current has no equivalent hardware limit. Register `REG03` sets it over I2C. The
range is 50 mA to 5000 mA. The register resets to the `PROG` resistor default of 1 A at
power-on reset, at a watchdog timeout and at a register reset.

**Firmware must not set the charge current above 2000 mA.** In buck mode the charge current can
be larger than the input current. A higher setting can therefore drive the charge-side copper
above its rating, even with the input current limit in place.

### Battery temperature sensing

`R305` and `R306` bias the `TS` pin from the `REGN` rail. The divider suits a 103AT-type 10 kΩ
NTC thermistor at 25 °C. The thermistor is not on the board. It connects through `J302`, a JST
PA 2-pin side-entry header (`S02B-PASK-2`). See
[extra-components.md](../extra-components.md).

The charger uses the `TS` reading for JEITA temperature qualification.

**Without a thermistor the charger does not charge at all.** With `J302` open, the divider sits
at 30 / (5.1 + 30) = 85.5% of `REGN`. Every cold threshold is below that: the 0 °C
threshold `VT1_RISE` is 73.3% of `REGN`, and even the -20 °C OTG threshold is 80%. The charger
therefore reads a cell colder than its cold cutoff and suspends charging.

The divider is right once a thermistor is present. A 103AT-type 10 kOhm NTC at 25 °C parallels
`R306` down to 7.50 kOhm and puts the pin at 59.5% of `REGN`, in the middle of the charging
window. Fit a thermistor. The datasheet gives no guidance for an unused `TS` pin, and recommends
a 103AT-2 part where it describes the pin at all. This board specifies the **103AT-11**: the
same 10 kΩ / B25/85 = 3435 K element, but supplied on 600 mm of insulated lead instead of the
103AT-2's 17 mm bare 42-alloy leads, which cannot be crimped. See
[extra-components.md](../extra-components.md).

Firmware can override the check with `TS_IGNORE`, bit 0 of `REG18`. That bit defaults to 0. The
datasheet lists it as reset by the watchdog and by a register reset; this board's firmware
disables the watchdog, so only a register reset clears it in practice. Setting it gives up
temperature qualification altogether.

The design does not fit a fixed resistor in place of the thermistor. Such a resistor would put
the pin at a constant voltage, and the charger would report a steady 25 °C that no sensor
measured. A reading that is wrong and convincing is worse than a reading that is absent.

## Power inductor — L1

`L1` is 1 µH. Its saturation current is 4 A. Its DC resistance is 48 mΩ.

The datasheet requires a saturation current of 2 A or more for this design. The 1.5 MHz
switching mode requires an inductance of exactly 1 µH.

An earlier revision used a small-signal multilayer inductor rated at 50 mA. That part was 40
times too small for the current in this circuit. The design replaced it with a true power
inductor from the manufacturer's own recommended-inductor table.

## Capacitors

The capacitor values come from the datasheet. The placement priorities come from section 8.4.1
of the datasheet. Each capacitor carries its own placement note in the schematic.

| Net | References | Value | Notes |
|---|---|---|---|
| `PMID` | `C304`, `C305`, `C306` | 10 µF each | Input side of the converter. |
| `PMID` | `C307` | 100 nF | Highest placement priority. `C304` pairs in parallel with it. |
| `SYS` | `C308`–`C312` | 10 µF each | Converter output. |
| `SYS` | `C313` | 100 nF | Highest placement priority. `C308` pairs in parallel with it. |
| `VBUS` | `C301`, `C302` | 10 µF each | Bulk capacitors. The datasheet allows them further from the pin. |
| `VBUS` | `C303` | 100 nF | Must sit close to the pin. |
| `BAT` | `C314`, `C315` | 10 µF each | Both sit close to the `BAT` and ground pins. |
| `REGN` | `C316` | 4.7 µF | Decouples the internal LDO. `REGN` drives the gate drivers and biases the `ILIM_HIZ`, `TS` and `STAT` pins. |
| `BTST1` | `C317` | 47 nF | Bootstrap capacitor for the buck-side high-side FET driver. |
| `BTST2` | `C318` | 47 nF | Bootstrap capacitor for the boost-side high-side FET driver. |
| `QON` | `C320` | 100 nF | Filters the wake-button node. |

The `SDRV` pin has no capacitor. It drives the gate of the ship FET `Q3` directly.

### Why the 100 nF capacitor pairs with one bulk capacitor

The datasheet gives the `PMID` and `SYS` nets the highest placement priority. For each of these
nets it requires the 100 nF capacitor and one bulk capacitor to sit together, on the same layer
as the IC, with short tracks. The other bulk capacitors on the same net need only a
low-impedance path back to the pin.

This pairing pushes the `SW1` and `SW2` tracks to a different layer, because the capacitors take
the space next to the IC.

### Why the capacitor packages differ

The 10 µF capacitors on the charger use both 0603 and 0805 packages. The package follows the
voltage rating, not the capacitance. Ceramic capacitors lose capacitance as the DC bias rises. A
larger package holds its value better at a given voltage.

Two decisions shaped these choices:

- The design corrected one 3.3 V rail capacitor from a 10 V part to a 25 V part. The 10 V part
  did not give enough derating margin.
- Several 4.7 µF capacitors moved to one common 25 V 0805 part. JLCPCB charges a feeder-loading
  fee for each unique component. One shared part costs less than two similar parts.

## Ship mode, shutdown mode and the system power reset

The ship FET `Q3` gives the board three low-power or reset states. The `SDRV_CTRL[1:0]` bits
select the state. These bits are bits 2 and 1 of register `REG11` (Charger Control 2).

| Value | Mode | Ship FET | Behaviour |
|---|---|---|---|
| `00` | Idle | On | Normal operation. This is the power-on-reset default. |
| `01` | Shutdown | Off | The I2C interface stops. Only an adapter wakes the charger. |
| `10` | Ship mode | Off | The I2C interface stays alive. The charger clock slows down. |
| `11` | System power reset | Off for about 350 ms | The charger then turns the FET on again. |

The charger enters shutdown mode and ship mode only when no adapter is present. If firmware
writes these values while an adapter supplies the board, the charger ignores the write.

Three events end ship mode: firmware writes `SDRV_CTRL[1:0]` back to `00`, the user plugs in an
adapter, or the `QON` pin goes low for the exit time. The charger then turns `Q3` on and resets
`SDRV_CTRL[1:0]` to `00`.

### The system power reset

The system power reset turns `Q3` off for about 350 ms. If `VBUS` is high, the charger also puts
the converter into HIZ mode. The charger applies a 30 mA sink current on `SYS` during this time.
This current pulls the `SYS` rail down actively. The charger then turns `Q3` on again.

The reset removes power from everything that the `SYS` rail supplies:

- `U4`, the buck-boost regulator, and therefore the 3V3_SYS rail
- `U1`, the MCU
- `R20` and `R21`, the internal I2C pull-up resistors
- `J6`, the STEMMA QT port
- `U5`, the load switch, and therefore the 3V3_USER rail and everything on it

The reset does **not** remove power from two parts. `U8` performs the reset itself, so `U8` stays
powered. `U3`, the fuel gauge, sits on the `VBAT_PROTECTED` net on the pack side of `Q3`, so `U3`
also stays powered. See [Fuel gauge](bq34z100-fuel-gauge.md).

The system power reset therefore cannot clear a stuck I2C slave. The charger and the gauge both
keep their bus state through the reset. To release a stuck bus, firmware must send the standard
nine-clock recovery sequence on `SCL`.

### Firmware requirement

**Firmware must set bit 7 `SFET_PRESENT` in register `REG14` (Charger Control 5) to 1.** The
power-on-reset value of this bit is 0. While the bit is 0, the charger locks `SDRV_CTRL[1:0]` at
`00` and locks `EN_BATOC` at 0. Ship mode, shutdown mode and the system power reset are then all
unavailable, and the board behaves as if no ship FET is fitted.

Setting the bit to 1 also unlocks `EN_BATOC`. With `EN_BATOC` set, the charger turns `Q3` off
when the discharge current exceeds its battery over-current threshold.

## The wake button — SW3

`SW3` is the wake button. It connects the `QON` pin to ground.

The `QON` pin has an internal pull-up of about 200 kΩ. No external pull-up is needed. A low level
on `QON` acts on the charger directly. `SW3` does not connect to the MCU.

The hold time selects the action:

| Hold time | Action |
|---|---|
| About 1 second | The charger exits ship mode. A register bit can shorten this time to 15 ms. |
| About 10 seconds | The charger runs the system power reset. |

The 10-second hold works whether the board runs on the battery alone or on an adapter. It also
works when the MCU firmware has stopped. The user can therefore power-cycle the board by hand.

`C320` is 100 nF. It filters ESD and noise on this track. It is not a debounce capacitor, because
`QON` responds to the level and not to the edge. The value is smaller than the 1 µF used on the
reset and boot buttons. The weak internal pull-up means that 100 nF already gives a release time
constant of about 20 ms.

## USB data-line isolation

The charger reads the USB D+ and D- lines for BC1.2 charger detection. The MCU also uses these
lines for its native USB port.

`R9` and `R11` are 10 kΩ. They sit between the shared data lines and the charger pins. They
isolate the charger's detection input from the live USB signals. Without them the charger loads
the data lines directly.

## Charge enable

The `CE` pin connects to ground. Charging is therefore enabled in hardware. Firmware still sets
the charge current over I2C. The charge current defaults to 1 A after a reset.

## Status LED

The `STAT` pin drives `LED2`. `R10` is 120 Ω. It connects the LED anode to the 3V3_SYS rail. The
charger sinks the current through the `STAT` pin.

## Interrupt

The `INT` pin drives the `CHG_INT` net. `R24` is a 10 kΩ pull-up. The net connects to GPIO8 on
the MCU. The pulse is short. Firmware can also read the fault registers over I2C if it misses
the pulse.

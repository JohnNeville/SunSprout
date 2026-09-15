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

## Configuration resistors

| Reference | Value | Pin | Function |
|---|---|---|---|
| `R301` | 3.0 kΩ | `PROG` | Sets the power-on default cell count to 1S. Also selects the 1.5 MHz switching frequency. The IC reads this resistor only at power-on reset. |
| `R302` | 110 kΩ | `ILIM_HIZ` | Upper leg of the input-current-limit divider from `REGN`. |
| `R303` | 130 kΩ | `ILIM_HIZ` | Lower leg of the same divider to ground. |
| `R304` | 100 Ω | `BATP` | Series isolation resistor on the battery-voltage sense input. The datasheet pin description requires it. |
| `R305` | 5.23 kΩ | `TS` | Upper leg of the thermistor bias divider from `REGN`. |
| `R306` | 30.1 kΩ | `TS` | Lower leg of the thermistor bias divider to ground. |

### The 2.00 A hardware input-current limit

`R302` and `R303` set a hardware limit on the input current. The limit is 2.00 A. The charger
enforces this limit as an analog ceiling. Firmware cannot exceed it through the I2C registers.

The board copper for the `PMID`, `SYS`, `SW1`, `SW2` and `BAT` nets carries 2 A. The IC itself
allows up to 5 A. The resistor divider makes the hardware match the copper. A firmware fault
cannot then drive the copper above its rating.

### Firmware constraint on the charge current

The charge current has no equivalent hardware limit. Register `REG03` sets it over I2C. The
range is 50 mA to 5000 mA. The register resets to the `PROG` resistor default of 1 A at
power-on reset, at a watchdog timeout and at a register reset.

**Firmware must not set the charge current above 2000 mA.** In buck mode the charge current can
be larger than the input current. A higher setting can therefore drive the charge-side copper
above its rating, even with the 2.00 A input limit in place.

### Battery temperature sensing

`R305` and `R306` bias the `TS` pin from the `REGN` rail. The divider suits a 103AT-type 10 kΩ
NTC thermistor at 25 °C. The thermistor is not on the board. It connects through `J302`. See
[extra-components.md](../extra-components.md).

The charger uses the `TS` reading for JEITA temperature qualification. Without a thermistor the
charger still works, but it cannot qualify fast charge against the cell temperature.

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
| `SDRV` | `C319` | 1 nF | Gate-driver pin decoupling. |
| `QON` | `C320` | 100 nF | Filters the wake-button node. |

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

## Ship mode and the wake button

`SW3` is the wake button. It connects the `QON` pin to ground.

The `QON` pin has an internal pull-up of about 200 kΩ. No external pull-up is needed. A low
level on `QON` wakes the charger from ship mode or from shutdown mode.

`C320` is 100 nF. It filters ESD and noise on this track. It is not a debounce capacitor,
because `QON` responds to the level and not to the edge. The value is smaller than the 1 µF used
on the reset and boot buttons. The weak internal pull-up means that 100 nF already gives a
release time constant of about 20 ms.

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

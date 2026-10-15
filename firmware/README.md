# Firmware

ESPHome configuration for the SunSprout hub.

| File | What it is |
|---|---|
| `sunsprout-hub.yaml` | The board package. Hardware only: MCU, both I2C buses, charger, fuel gauge, alert inputs, user rail, status LED. |
| `sunsprout-common.yaml` | Logging over USB and diagnostics every device wants. No networking, no name. |
| `sunsprout-deep-sleep.yaml` | Optional deep sleep for battery or solar hubs. Leave it out while setting a board up. |
| `example-device.yaml` | A complete device: the three packages above plus a name, WiFi, the Home Assistant API and OTA, all from `secrets.yaml`. Copy this to make your own. |
| `sunsprout-factory.yaml` | A factory image with no credentials. It starts in setup mode so the end user supplies the WiFi. |

The two chip drivers live in a separate repository,
[esphome-bq-drivers](https://github.com/JohnNeville/esphome-bq-drivers), because they are
drivers for stock TI parts rather than anything specific to this board. The board package
pulls them in through `external_components`.

## Flash a board

```bash
pip install esphome
```

Create `secrets.yaml` next to the config with `wifi_ssid`, `wifi_password`,
`fallback_password` and `api_encryption_key`, then:

```bash
esphome run firmware/example-device.yaml
```

Hold `SW2` (boot) while pressing `SW1` (reset) to enter download mode for the first flash.
After that, OTA works.

A device file needs its own `esphome:` block with a `name`, plus whatever networking you want.
The packages deliberately contain neither, so the same hardware description serves a
fully configured device and a factory image:

```yaml
substitutions:
  name: sunsprout
  friendly_name: Sunsprout

packages:
  hub: !include sunsprout-hub.yaml
  common: !include sunsprout-common.yaml
  # deep_sleep: !include sunsprout-deep-sleep.yaml   # once the board is set up

esphome:
  name: "${name}"
  friendly_name: "${friendly_name}"

api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    encryption:      # reuses the API key; a separate OTA password is deprecated

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  fast_connect: true
```

Logs come out of the USB-C port, not UART0: `sunsprout-common.yaml` sets
`logger: hardware_uart: USB_SERIAL_JTAG`. The port resets and re-enumerates on every reboot,
so use a terminal that reconnects, such as `tio /dev/ttyACM0` or `esphome logs`.

## Factory image and setup mode

`sunsprout-factory.yaml` is for shipping a board whose owner is not you. It has no WiFi
credentials, no API encryption key and no OTA password, and it leaves deep sleep out so an
unconfigured board stays awake. On first boot the board starts its own access point
(`Sunsprout Setup`) and offers three ways to join a network:

- **Improv over USB.** Flash from a browser with ESP Web Tools and it asks for the SSID and
  password straight away (`improv_serial`).
- **Captive portal.** Join the access point and the portal opens a WiFi picker.
- **Adopt in the ESPHome dashboard.** The `dashboard_import` entry makes the board appear as
  discovered. Adopting it writes a normal device file that pulls the factory file in as a
  package and adds secrets, so the owner can then add `sunsprout-deep-sleep.yaml`, change the
  substitutions, or anything else, without editing the factory file.

Build the image with `esphome compile firmware/sunsprout-factory.yaml` and flash the
`.factory.bin` at offset `0x0`.

## Using a standard lithium-ion cell

The defaults describe a 6000 mAh LiFePO4 cell. For a standard 3.7 V lithium-ion or LiPo
cell, override these substitutions in your device file:

| Substitution | LiFePO4 default | Standard Li-ion | Why |
|---|---|---|---|
| `cell_chemistry` | `lifepo4` | `li_ion` | Charge limit: 3.65 V becomes 4.20 V. |
| `battery_capacity` | `6000` | your cell, in mAh | Sets C/10 charge termination and the gauge's design capacity. |
| `battery_energy_mwh` | `19200` | capacity × 3.7 | The gauge's design energy; the default is capacity × 3.2 V. |
| `lifepo4_relax` | `true` | `false` | Only applies once a LiFePO4 chemistry is in the gauge. |
| `charge_current` | `1000` | at most your cell's rating | The ceiling stays 2000 mA whatever you set. |

```yaml
substitutions:
  cell_chemistry: "li_ion"
  battery_capacity: "3000"        # mAh
  battery_energy_mwh: "11100"     # 3000 mAh x 3.7 V
  lifepo4_relax: "false"
  charge_current: "1000"
```

The gauge ships with a lithium-ion chemistry profile, so a standard 4.2 V cell needs none of
the bqStudio work described under *Fuel gauge setup* below. Set `apply_configuration: true`
once with the cell attached to write the capacity and energy, then run the two offset
calibrations. Check the **Gauge Chemistry ID** entity afterwards to confirm the profile.

`li_ion_4_35` and `li_ion_4_40` raise the charge limit for high-voltage cells, but the gauge
profile does not follow automatically; those cells need a matching chemistry loaded.

The battery thermistor requirement is unchanged: fit a 103AT-type 10 kΩ NTC at `J302`, or the
charger will not charge.

## Pin map

| GPIO | Net | Use |
|---|---|---|
| GPIO2 | `SDA_INT` | Internal I2C data (`LP_I2C_SDA`) |
| GPIO3 | `SCL_INT` | Internal I2C clock (`LP_I2C_SCL`) |
| GPIO4 | `FG_ALERT` | Fuel gauge alert, active low |
| GPIO6 | `LED1_CTRL` | Status LED |
| GPIO8 | `CHG_INT` | Charger interrupt, active low |
| GPIO9 | `SDA_USER` | User I2C data |
| GPIO10 | `SCL_USER` | User I2C clock |
| GPIO23 | `EN_3V3_USER` | Enables the switched user rail |

| Device | Bus | Address |
|---|---|---|
| BQ25798 charger | internal | `0x6B` |
| BQ34Z100 fuel gauge | internal | `0x55` |

See [ESP32-C5 module](../docs/hub/modules/esp32-c5-mcu.md) for the full pin assignment.

## The two I2C buses

The ESP32-C5 has one general-purpose I2C controller and one low-power controller. The
low-power controller is hard-wired to **GPIO2 for SDA and GPIO3 for SCL**, and that is
exactly how `SDA_INT` and `SCL_INT` are routed. The internal bus takes the low-power
controller (`low_power_mode: true`), the user bus takes the general-purpose one, and both
run at the same time.

**Do not move either internal-bus pin.** The low-power controller works on no other pair.
Put `SCL_INT` anywhere else and both buses end up competing for the single general-purpose
controller, which ESPHome refuses to build.

GPIO3 is also `MTDI`, a strapping pin that selects the SDIO sampling edge alongside GPIO25.
It defaults to floating and the bus pull-up latches it to 1 at reset. This board does not
use SDIO, so that has no effect — and GPIO2 (`SDA_INT`) is the `MTMS` strapping pin under
the same pull-up, so the design already carries this condition.

## Things the firmware must get right

**The charge voltage.** The charger reads the `PROG` resistor at power-on and comes up
configured for a 1S **4.2 V** cell. A LiFePO4 cell charges to 3.65 V.

The board package declares `chemistry: lifepo4`, and the driver derives the charge voltage
limit from that, writes it during setup, and rewrites it after any register reset. There is
deliberately **no charge-voltage slider** — a limit that protects the cell should not be
something anyone can drag in Home Assistant.

If you fit a different cell, change `cell_chemistry` in the substitutions. The accepted
values are `lifepo4`, `li_ion`, `li_ion_4_35` and `li_ion_4_40`.

**The charge current ceiling.** `R302` and `R303` cap the *input* current at roughly 2 A in
hardware — nearer 2.0 A on USB-C and 2.14 A on a high-voltage solar input, because the
divider is referenced to the input-dependent `REGN` rail. There is no equivalent hardware
limit on the charge current, and in buck mode the charge current can exceed the input
current, so `max_charge_current: 2000` in the board package is what keeps the 2 A copper
safe. Do not raise it.

**The watchdog stays off.** The charger's I2C watchdog reverts the charge voltage and
current to the `PROG` defaults when it expires — which for the voltage means 4.2 V. The
board package disables it.

**`ship_fet_present: true` is what makes the reboot button work.** `Q3` is the ship FET on
`SDRV`. The charger locks `SDRV_CTRL` — and `EN_BATOC` — at 0 until `SFET_PRESENT` is set,
so without this flag the ship-mode and power-cycle controls exist but do nothing. The
driver rejects the config outright rather than let that happen quietly.

## Rebooting the board

**Power Cycle Board** opens `Q3` for about 350 ms and closes it again. Everything on the
`SYS` rail loses power — the regulator, the MCU, the internal I2C pull-ups, both STEMMA QT
ports and the user rail — so the board reboots. The board package sets
`ship_fet_action_delay: false`, otherwise the charger waits ~10 s before acting.

Two parts stay powered: the charger performs the reset itself, and the fuel gauge sits on
`VBAT_PROTECTED`, on the pack side of `Q3`, so it keeps counting coulombs through it. That
is deliberate — a gauge that loses its supply has to relearn the pack — but it means **a
power cycle cannot clear a stuck I2C slave**, because neither I2C device actually loses
power. For a wedged bus, send the nine-clock recovery sequence on `SCL` instead.

Holding `SW3` for about 10 seconds does the same thing in hardware, with no firmware
involved, which is the one that still works when the MCU is hung.

**Charger Ship Mode** and **Charger Shutdown** cut power until an adapter arrives or `SW3`
pulls `QON` low. Both are hidden by default; the charger ignores either while an adapter is
connected. Neither stops the fuel gauge's standing draw, so neither gives true zero-draw
storage — unplug the pack at `J4` for that.

## Fuel gauge setup, once per board

The gauge ships with a lithium-ion chemistry profile (`Device Chemistry` defaults to
`LION`). A LiFePO4 cell needs a 400-series one, and until it is loaded the state of charge
is wrong no matter what else is configured.

**There is no I2C command that sets the chemistry** — `CHEM_ID` only reports it, and the
only selection path TI documents is the BQChem feature in bqStudio (datasheet §8.1.2.1.6).
But the chemistry lives in ordinary data flash, which §7.2.3.1 says is reachable through
bqStudio *or* through data flash block transfers — the same protocol this driver already
uses for capacity and calibration. The datasheet calls the captured result a Golden Image
File that "can then be written to multiple battery packs".

So: **bqStudio once, to obtain the values; not once per board.** After that the bytes can
be replayed over I2C. What bqStudio supplies is the table contents, not exclusive write
access — the datasheet does not publish them.

Everything else the gauge needs *can* be written from firmware. The `bq34z100` block lives
in the board package, so reach it from your device file with its `fuel_gauge` id and set
`apply_configuration: true` with a cell attached, then reflash:

```yaml
sensor:
  - id: !extend fuel_gauge
    apply_configuration: true
```

The driver writes Design Capacity, Design Energy, cell count, the Pack Configuration bits and
the `R404` sense-resistor calibration, comparing each value first so it does not wear the
flash, and reading each one back to confirm. Then, with the pack at rest and no current
flowing, press **Calibrate Gauge Current Offset** and **Calibrate Gauge Board Offset**.

Set `expected_chem_id` to the chemistry you loaded and the driver will log an error at
boot if the gauge is running something else.

### The alert pin

The gauge's `ALERT` output is wired to `FG_ALERT` on GPIO4, but the gauge ships with its Alert
Configuration register at 0, so the pin never goes low. Choose which gauge flags drive it with
`alert_configuration`, in the same `!extend` block (it is only written when
`apply_configuration: true`):

```yaml
sensor:
  - id: !extend fuel_gauge
    apply_configuration: true
    alert_configuration: [low_charge, critical_charge]
```

The flag names are listed in the
[driver README](https://github.com/JohnNeville/esphome-bq-drivers#alert-pin). The board package
leaves the **Fuel Gauge Alert** input disabled by default; enable it in Home Assistant to see the
pin. The driver clears a pending alert whenever it reads the gauge's flags, so the pin can go
high again at the next poll.

## Choosing which input powers the board

**Input Selection** is a drop-down with Auto, Force USB, Force Solar and Off. It replaces the
old per-port switches, which only decided whether an input could turn on and did nothing to an
input that was already live. **Active Input** shows which port is feeding the board.

- **Off** forces both input drivers off. The board runs from the battery and does not charge,
  and with no battery fitted it loses power.
- **Force USB** and **Force Solar** are preferences, not locks. The charger turns an input on by
  itself when it sees a valid one, and nothing can make it refuse one, so with USB plugged in
  Force Solar cannot hold. The drop-down then falls back to Auto and the log says so.
- Changing the selection can briefly cut the supply, because the input has to be opened and
  the charger has to wait for `VBUS` to fall before the drivers come back. A change that keeps
  the port already feeding the board does not.
- The choice is not remembered over a restart. The charger starts in Auto.

## Solar tracking

The BQ25798 tracks the panel's maximum power point itself. It stops switching every couple
of minutes, measures the open-circuit input voltage, and sets `VINDPM` to a fraction of it.
Turn it on with the **Enable MPPT** switch — the board package enables it by default.

This is why there is no separate power monitor on the board and no VINDPM-chasing script
in the configuration.

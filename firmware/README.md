# Firmware

ESPHome configuration for the SunSprout hub.

| File | What it is |
|---|---|
| `sunsprout-hub.yaml` | The board package. Hardware only: MCU, both I2C buses, charger, fuel gauge, alert inputs, user rail, status LED. |
| `example-device.yaml` | A complete device built on that package, with WiFi, the Home Assistant API, OTA and deep sleep. |

The two chip drivers live in a separate repository,
[esphome-bq-drivers](https://github.com/JohnNeville/esphome-bq-drivers), because they are
drivers for stock TI parts rather than anything specific to this board. The board package
pulls them in through `external_components`.

## Flash a board

```bash
pip install esphome
```

Create `secrets.yaml` next to the config with `wifi_ssid`, `wifi_password`,
`fallback_password`, `api_encryption_key` and `ota_password`, then:

```bash
esphome run firmware/example-device.yaml
```

Hold `SW2` (boot) while pressing `SW1` (reset) to enter download mode for the first flash.
After that, OTA works.

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

**The charge current ceiling.** `R302` and `R303` cap the *input* current at 2.00 A in
hardware. There is no equivalent hardware limit on the charge current, and in buck mode
the charge current can exceed the input current, so `max_charge_current: 2000` in the
board package is what keeps the 2 A copper safe. Do not raise it.

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

The gauge ships with a lithium-ion chemistry profile. A LiFePO4 cell needs a 400-series
chemistry, and **that cannot be loaded over I2C** — it takes TI's bqStudio with an EV2400
and a `.bqz` chemistry file, once, at the bench. Until that is done the state of charge
will be wrong no matter what else is configured.

Everything else the gauge needs *can* be written from firmware. Set
`apply_configuration: true` in the `bq34z100` block with a cell attached and reflash; the
driver writes Design Capacity, Design Energy, cell count, the Pack Configuration bits and
the `R60` sense-resistor calibration, comparing each value first so it does not wear the
flash, and reading each one back to confirm. Then, with the pack at rest and no current
flowing, press **Calibrate Gauge Current Offset** and **Calibrate Gauge Board Offset**.

Set `expected_chem_id` to the chemistry you loaded and the driver will log an error at
boot if the gauge is running something else.

## Solar tracking

The BQ25798 tracks the panel's maximum power point itself. It stops switching every couple
of minutes, measures the open-circuit input voltage, and sets `VINDPM` to a fraction of it.
Turn it on with the **Enable MPPT** switch — the board package enables it by default.

This is why there is no separate power monitor on the board and no VINDPM-chasing script
in the configuration.

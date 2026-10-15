# Bench tests

Small scripts that drive a SunSprout hub over the ESPHome API: set a control, then read what
the charger and the fuel gauge report. They were used to produce the results on the testing
status page, and they are the quickest way to repeat a test on a new board.

They need Python with `aioesphomeapi`, which comes with ESPHome (`pip install esphome`). Each
script takes the board's address and your `secrets.yaml`, and reads only the API key from it
(`esphome_encryption_key` or `api_encryption_key`). The key is never printed. The board must run
the firmware from [SunSprout-firmware](https://github.com/JohnNeville/SunSprout-firmware).

Run them with `python -I tools/bench-tests/<script>.py <host> <secrets.yaml> ...`.

| Script | What it does |
|---|---|
| `device_info.py <host> <secrets> [plaintext]` | Name, MAC, ESPHome version and entity count. Add a third argument for a board that is not yet using an encrypted API. |
| `list_entities.py <host> <secrets> <regex>` | Lists the entities whose names match, and whether they are disabled by default. |
| `states.py <host> <secrets> <name> [<name> ...]` | Prints the current state of the named entities. |
| `charger_tests.py <host> <secrets> interrupt` | Cycles Input Selection Off and Auto and watches the charger interrupt input. The pulse is too short for the input to catch, so this is inconclusive without a logic analyser. |
| `charger_tests.py <host> <secrets> reset` | Presses Reset Charger Registers and compares the readings before and after. |
| `charger_tests.py <host> <secrets> ramp <csv>` | Steps the charge current limit from 500 to 2000 mA, four minutes each, logging temperatures and currents. It stops on a fault, a die temperature over 85 C or sustained thermal regulation, and always restores the original limit. |
| `charger_tests.py <host> <secrets> log <csv>` | Logs a charge every 30 s until the charger reports it has terminated. |
| `solar_tests.py <host> <secrets> <phase> <seconds> [csv]` | Samples the solar input. Phases: `watch`, `solar` (turn Enable Solar Input on), `hiz` (cycle HIZ to restart input qualification), `mppt`, `ratio:<option>` and `ichg:<mA>`. `ichg` does **not** restore the charge current afterwards. |
| `select_sequence.py <host> <secrets> <wait> <option> ...` | Drives the Input Selection drop-down through a list of options, logging the selection, Active Input and charger state. |
| `usb_switch_test.py <host> <secrets> <seconds>` | Turns the old Enable USB Input switch off for a while and logs whether the input stays live. It always restores the switch. |
| `press_and_watch.py <host> <secrets> <button> <marker> <out> [timeout]` | Presses a button and saves the log lines up to a marker. A button name of `-` just prints a few states. |

These scripts change settings on the board and some of them interrupt charging. Run them on a
bench board, not one that is powering something.

## PCB net helpers

`tools/pcb-nets/` has three read-only scripts that read a KiCad `.kicad_pcb` file as text, to
find which pads sit on which net and where they are, for example to decide where to put a
meter probe: `pcb_nets.py <pcb> <ref> ...` (pad nets of a part), `pcb_members.py <pcb> <net>
...` (every pad on a net) and `pcb_abs.py <pcb> <ref>[:pad,pad] ...` (board coordinates of pads).

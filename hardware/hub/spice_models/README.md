# SPICE verification decks

Small ngspice decks used to check MOSFET threshold and on-state behaviour against real
manufacturer models, rather than against a generic symbol's assumed characteristics.

These decks drove the reverse-polarity FET selection documented in
[docs/hub/modules/input-protection.md](../../../docs/hub/modules/input-protection.md).

## Why the models themselves aren't committed

The `.cir` decks here are original work and are tracked. The vendor model files they
`.include` are **not** tracked — `.gitignore` excludes them. Three reasons:

1. **No redistribution grant.** The Diodes Inc model carries a warranty disclaimer and nothing
   else; the AOS models carry no terms at all. Silence is not permission. The TI PSpice models
   come from a click-through download, and the TPS631000 one is explicitly encrypted.
2. **This repository is licensed CERN-OHL-S v2.** Vendoring third-party files under a
   repo-wide reciprocal license statement implies they are offered under that license too.
   They aren't, and they can't be.
3. **Nothing is lost.** A SPICE model is a design-verification aid. It is not needed to build
   the board, so it is an "Available Component" at most — the license obligation is to say
   where to get it, which is what this file does.

This matches how the repository already treats no-redistribution vendor CAD models.

## Getting the models

Download each model and drop it in this directory under the filename shown. Then the decks run
as-is.

| Filename | Part | Source |
|---|---|---|
| `AO3400.mod` | AO3400A (`Q301`–`Q304`) | Alpha & Omega Semiconductor product page for AO3400A |
| `AO3415.mod` | AO3415 | Alpha & Omega Semiconductor product page for AO3415 |
| `DMP3098L.spice.txt` | DMP3098L-7 (`Q2`) | Diodes Incorporated product page for DMP3098L-7 |

`AO3415_clean.mod` was a locally-edited copy of `AO3415.mod`, trimmed so ngspice would parse
it. Recreate it if needed rather than expecting it in the repository.

`AO3415` stands in for `Q1`'s actual part, MDD3415, which has no published SPICE model.
Treat that result as indicative, not authoritative.

## Decks

| Deck | Checks |
|---|---|
| `test_Q301_real.cir` | `Q301` (AO3400A), gate swept 0–5 V against the USB rail. |
| `test_Q2_real.cir` | `Q2` (DMP3098L-7), the solar/DC reverse-polarity FET. |
| `test_Q1_AO3415.cir`, `test_Q1_AO3415_v2.cir` | `Q1`'s battery-side FET, using the AO3415 stand-in. The `_v2` deck uses a coarser sweep. |

Each deck measures the gate threshold at 1 mA of drain current and the on-state current at full
gate drive.

## Running

```bash
ngspice -b test_Q301_real.cir
```

Run from inside this directory, because the decks use relative `.include` paths. Log and output
files are ignored by git — they regenerate on every run.

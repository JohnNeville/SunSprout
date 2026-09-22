# SunSprout Project TODOs

## Satellite PCB (`hardware/satellite/`)

See the detailed action items in [hardware/satellite/TODO.md](hardware/satellite/TODO.md):

- [ ] **Reference Plane on `In2.Cu`:** Add a copper plane (GND or SAT_3V3) to eliminate impedance discontinuity on `B.Cu` differential and I2C traces.
- [ ] **ESD Diode (`U4`) Flow-Through Routing:** Eliminate 1.5mm–2.5mm stubs on `DSCL` and `DSDA` differential lines to ensure full ESD clamping before `U1`.
- [ ] **RJ45 Shield Trace Width:** Widen the 0.2mm `SHIELD` trace between `J1` tabs and `JP13` to ≥ 1.5mm–2.0mm.
- [ ] **Decoupling Capacitor Ground Inductance:** Move vias adjacent to `C1`–`C6` ground pads and widen connections from 0.2mm to 0.5mm+.
- [ ] **PCA9615 Ground Pin:** Widen `U1.pin5` ground trace from 0.2mm to 0.4mm–0.5mm.
- [ ] **Differential Pair Coupling:** Tighten and match spacing between `DSCL_P/N` and `DSDA_P/N` pairs and align transition vias.
- [ ] **Ground Stitching Vias:** Add ground return vias beside signal vias where `DSCL`, `DSDA`, and I2C lines change layers.
- [ ] **Analog Crosstalk:** Increase spacing between `MOIST3` and `MOIST4` from 0.2mm to ≥ 0.6mm.
- [ ] **Acid Traps:** Eliminate 45° acute corners and trace hairpins on `F.Cu` and `In2.Cu`.
- [ ] **J7 Footprint Metadata:** Update pinout description to match `VCC_2, GND_2, GND, SAT_3V3`.
- [ ] **DFM Test Points & Fiducials:** Add 1.0mm test pads on `B.Cu` for power, GND, and I2C/differential pairs, plus 3 standard SMT optical fiducials.

---

## Hub PCB (`hardware/hub/`)

See the detailed action items in [hardware/hub/TODO.md](hardware/hub/TODO.md):

- [x] **BQ25798 Charger Switching Nodes (`SW1_NODE` & `SW2_NODE`):** Enhanced with 0.3mm pad escape necking into a 3-via parallel cluster on `F.Cu`, wide polygon pours on `B.Cu`, and 2 parallel vias connecting into inductor `L1` pads.
- [x] **High-Frequency Loop Necking (`PMID_NET` & `SYS_RAIL`):** Expanded `U8` pin 29 (`PMID`) and pin 25 (`SYS`) connections into solid polygon pours directly to their high-frequency decoupling capacitors, minimizing loop inductance and ripple.
- [x] **Bootstrap Capacitor Loops (`C317` & `C318`):** Kept on `F.Cu` to preserve single-sided SMT assembly, routed with via transitions per TI BQ25798 datasheet Section 8.4.1 (which explicitly validates vias on both sides of BTST caps).
- [x] **Battery Path Trace Widths (`VBAT`, `VBAT_RAW`, `VBAT_PROTECTED`):** Covered `U8` pins 22/23 entry with a 0.8mm polygon pour, and widened `VBAT_RAW` / `VBAT_PROTECTED` tracks with filled pin connections to minimize IR drop and localized resistance at 2A.
- [x] **Fuel Gauge Shunt (`R60`) Kelvin Sensing & Filtering:** Re-routed `FG_SRN` and `BATT_RTN` as an ultra-short (2.78 mm), tightly coupled parallel pair from the inner edges of `R60` pads directly to `U3` pins 9/10 (matched to within 0.007 mm), eliminating solder/pad IR drop errors.
- [x] **ESP32-C5 Boot Button Rewiring:** Re-routed `SW2` / `C21` (`BTN1_NODE`) to `GPIO28` instead of `GPIO0`, and exposed `GPIO0` on header `J7 pin 3`.
- [x] **Mass Programming Pogo-Pin Test Points:** Added `TP16` (`U0RXD`), `TP17` (`U0TXD`), `TP18` (`BTN1_NODE` / `GPIO28`), and `TP19` (`RESET_NODE`) on `B.Cu` to enable automated single-sided bed-of-nails flashing.
- [x] **Inner Layer Copper Balance (`In2.Cu` & `In3.Cu`):** Added full-board GND fill zone (`"Inner GND fills"`) across `In2.Cu` and `In3.Cu` with filled copper polygons to balance layer density and mitigate board warpage during reflow.
- [x] **Acid Traps:** Cleaned up acute corners and trace reversals across the board; verified with KiCad custom DRC rule (0 violations).
- [x] **Firmware Sleep Leakage Prevention:** Float `GPIO9`/`GPIO10` (to stop 1.40 mA into `R201`/`R202` on unpowered `3V3_USER`) and clear BQ25798/BQ34Z100 interrupts before sleep (to stop 660 uA on `R24`/`R401`).



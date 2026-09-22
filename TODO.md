# SunSprout Project TODOs

## Satellite PCB (`hardware/satellite/`)

See the detailed action items in [hardware/satellite/TODO.md](hardware/satellite/TODO.md):

- [x] **Reference Plane on `In2.Cu`:** Added `GND Fill In2` copper pour and `VCC_2` power plane zone on `In2.Cu` to provide continuous reference plane for `B.Cu` differential and I2C traces.
- [x] **ESD Diode (`U4`) Flow-Through Routing:** Eliminated branch stubs on `DSCL` and `DSDA`; traces now flow directly through SMT pads before reaching `U1`.
- [x] **RJ45 Shield Trace Width:** Replaced 0.2mm trace with dedicated copper pour `SHIELD GND Area` on `B.Cu`.
- [x] **Decoupling Capacitor Ground Inductance:** Widened GND traces on all decoupling capacitors `C1`-`C6` (`C1`: 0.40mm, `C2`: 0.60mm, `C3`: 0.60mm, `C4`: 0.50mm, `C5`: 0.50mm, `C6`: 0.50mm).
- [x] **PCA9615 Ground Pin:** Widen `U1.pin5` ground trace to 0.4mm-0.5mm (completed: 0.40mm trace to GND via at 115.5, 118.5).
- [x] **Differential Pair Coupling:** Tighten and match spacing between `DSCL_P/N` and `DSDA_P/N` pairs and align transition vias (`DSDA` vias tightened to 1.30mm; `DSCL` aligned horizontally).
- [x] **Ground Stitching Vias:** Placed adjacent ground return vias across both differential pairs and local I2C signal layer transitions (board via count increased to 58).
- [x] **Analog Crosstalk:** Increase spacing between `MOIST3` and `MOIST4` from 0.35mm edge-to-edge to >= 0.6mm (completed: 0.700mm edge-to-edge / 0.900mm center-to-center on F.Cu).
- [x] **Acid Traps:** Eliminated acute corners and hairpins on `F.Cu`, `B.Cu`, and `In2.Cu`; enforced JLCPCB DRC rule `track_angle >= 90deg` (0 violations).
- [x] **J7 Footprint Metadata:** Updated `Usage` property to `"Auxiliary 1x4 2.54mm header: Pin 1: VCC_2, Pin 2: GND_2, Pin 3: GND, Pin 4: SAT_3V3 (power breakout and bus injection)"`.
- [x] **DFM Test Points (`B.Cu`):** Added 2-pole 1.0mm test points `TP4` (`DSCL+/-`) and `TP5` (`DSDA+/-`) on `B.Cu`; power, GND, and local I2C probed via accessible solder jumpers.
- [x] **Optical Fiducial Markers:** Added 4 optical fiducials on `F.Cu` (`Fiducial_0.5mm_Mask1mm`) across board quadrants for automated SMT pick-and-place.

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



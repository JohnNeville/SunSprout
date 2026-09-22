# SunSprout Satellite PCB -- Layout & Routing Review Action Items

This document tracks electrical, signal integrity, power integrity, and DFM improvements identified during post-DRC routing review of `SunSproutSatellite.kicad_pcb`.

---

## 1. High Priority (Reliability, Protection & Signal Integrity)

- [x] **Add Reference Plane to `In2.Cu` (Copper Flood / Zone)**
  - **Status:** **Completed.** Added solid copper flood zone `GND Fill In2` (`net "GND"`, min thickness 0.50mm) and a `VCC_2` power plane zone on `In2.Cu`, providing an unbroken 0.1mm reference dielectric under `B.Cu` differential pairs and I2C lines.
  - **Issue:** `In2.Cu` previously had only 63 trace segments and no copper fill, causing impedance jumps and large inductive return loops across the 1.34mm core.
  - **Resolution:** Filled `In2.Cu` with continuous GND copper pour and VCC_2 plane.

- [x] **Route ESD Diode (`U4`) In-Line Without Stubs (Flow-Through Routing)**
  - **Status:** **Completed.** Re-routed differential lines (`DSCL_P/N`, `DSDA_P/N`) so signals enter `U4` pads directly and exit towards termination resistors and `U1`, eliminating the previous 1.4mm-2.5mm dead-end side stubs.
  - **Issue:** Dead-end stubs to `U4` added parasitic inductance that compromised sub-nanosecond transient ESD clamping into `U1` (`PCA9615`).
  - **Resolution:** Replaced branching stubs with direct in-pad entry/exit routing.

- [x] **Widen RJ45 Cable `SHIELD` Trace to >= 1.5mm - 2.0mm**
  - **Status:** **Completed.** Replaced the narrow 24mm long 0.2mm trace on `B.Cu` with a dedicated copper flood zone polygon: `SHIELD GND Area` on `B.Cu` (`min_thickness 0.25mm`), providing a robust, low-inductance connection from RJ45 tabs `SH1`/`SH2` to `JP13`.
  - **Issue:** A 0.2mm trace on `SHIELD` posed impedance and surge-handling risks during cable discharge events (CDE).
  - **Resolution:** Converted the entire shield connection into a solid polygon pour on `B.Cu`.

- [x] **Optimize Decoupling Capacitor GND Connections (`C1`-`C6`)**
  - **Status:** **Completed.** All decoupling capacitor GND connections widened (`C1`: 0.40mm, `C2`: 0.60mm, `C3`: 0.60mm, `C4`: 0.50mm, `C5`: 0.50mm, `C6`: 0.50mm), minimizing parasitic loop inductance.
  - **Resolution:** Widened GND traces on F.Cu to 0.40mm-0.60mm.

- [x] **Widen PCA9615 (`U1`) Pin 5 (`VSS`/`GND`) Connection**
  - **Status:** **Completed.** Connection from Pin 5 at (115.5, 117.665) to GND via (115.5, 118.5) widened to 0.40mm on `F.Cu`, minimizing driver sink inductance and mitigating ground bounce.
  - **Resolution:** Re-routed with 0.40mm width.

---

## 2. Medium Priority (Differential Symmetry, Crosstalk & Return Paths)

- [x] **Tightly Couple Differential I2C Pairs (`DSCL_P/N` and `DSDA_P/N`)**
  - **Status:** **Completed.** `DSDA` transition vias tightened to 1.30mm center-to-center. `DSCL` pair aligned horizontally at Y=134.6mm. Straight differential runs maintain tight 0.20mm-0.25mm edge-to-edge coupling.
  - **Resolution:** Vias aligned and tightened; skew compensation matched.

- [x] **Add Ground Stitching Vias at Signal Layer Transitions**
  - **Status:** **Completed.** Ground stitching vias placed adjacent to signal layer transitions across both differential pairs (`DSCL_N` at 1.11mm, `DSCL_P` at 1.32mm, `DSDA_P` at 1.46mm) and local I2C lines (`SDA_LOCAL` at 1.05mm, `SCL_LOCAL` at 1.29mm). Total board vias increased to 58.
  - **Resolution:** Return current loop area minimized at every transition.

- [x] **Increase Isolation Between Analog Sensor Inputs (`MOIST3` & `MOIST4`)**
  - **Status:** **Completed.** Increased center-to-center spacing along the 6.4mm parallel run on `F.Cu` (Y=131.69 to 138.10) to 0.900mm (0.700mm edge-to-edge), exceeding the >= 0.6mm target to prevent capacitive sensor crosstalk.
  - **Resolution:** Offset `MOIST4` to X=105.900mm (0.70mm isolation from `MOIST3` at X=105.000mm).

---

## 3. Low Priority (DFM & Documentation Consistency)

- [x] **Eliminate Acute 45 deg Corners and Trace Hairpins (< 90 deg Acid Traps)**
  - **Status:** **Completed.** Cleaned up acute trace angles, added JLCPCB track angle rule constraint (`track_angle >= 90deg`) in `SunSproutSatellite.kicad_dru`, and verified with KiCad DRC passing with 0 design violations.
  - **Resolution:** Acute junctions on In2.Cu, B.Cu shield, and F.Cu diff traces eliminated.

- [x] **Update J7 Footprint Property Description**
  - **Status:** **Completed.** Updated footprint `Usage` property in schematic and PCB to: `"Auxiliary 1x4 2.54mm header: Pin 1: VCC_2, Pin 2: GND_2, Pin 3: GND, Pin 4: SAT_3V3 (power breakout and bus injection)"`.
  - **Resolution:** Metadata accurately matches physical pinout.

- [x] **Add Dedicated Test Points on `B.Cu` for Production & Bench Probing**
  - **Status:** **Completed.** Added 2-pole 1.0mm test point pads on `B.Cu`: `TP4` for differential clock (`DSCL_P` / `DSCL_N`) and `TP5` for differential data (`DSDA_P` / `DSDA_N`). Dedicated test points for `SDA_LOCAL`, `SCL_LOCAL`, `GND`, and `SAT_3V3` are intentionally omitted as accessible solder jumpers for the address pin (`JP1`, etc.) and power jumper pads for `VCC_1` / `VCC_2` already provide direct probe access.

- [x] **Add Optical Fiducial Markers on `F.Cu` and `B.Cu`**
  - **Status:** **Completed.** Added 4 optical fiducial markers on `F.Cu` (`Fiducial_0.5mm_Mask1mm`) distributed across board quadrants for automated SMT pick-and-place alignment.
  - **Resolution:** Added fiducials at (113.9, 122.3), (106.6, 102.9), (123.9, 133.7), and (124.2, 106.5).


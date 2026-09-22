# SunSprout Satellite PCB — Layout & Routing Review Action Items

This document tracks electrical, signal integrity, power integrity, and DFM improvements identified during post-DRC routing review of `SunSproutSatellite.kicad_pcb`.

---

## 1. High Priority (Reliability, Protection & Signal Integrity)

- [ ] **Add Reference Plane to `In2.Cu` (Copper Flood / Zone)**
  - **Issue:** `In2.Cu` currently has only 63 trace segments and no copper fill. Bottom-layer (`B.Cu`) traces—including ~50% of the differential I2C pairs (`DSCL_P/N`, `DSDA_P/N`), `SCL_LOCAL`, `SDA_LOCAL`, and `SHIELD`—have no adjacent reference plane (distance to `In1.Cu` GND is 1.34mm across the core vs 0.1mm on `F.Cu`). This causes an impedance jump from ~55 Ω to >130 Ω and large inductive return loops.
  - **Action:** Fill `In2.Cu` with a `GND` copper pour (standard Sig-GND-GND-Sig stackup) or a `SAT_3V3` power plane so that `B.Cu` signals have an unbroken 0.1mm reference dielectric.

- [ ] **Route ESD Diode (`U4`) In-Line Without Stubs (Flow-Through Routing)**
  - **Issue:** Signals from `J1` (`DSCL_P/N`, `DSDA_P/N`) come up from `B.Cu` through vias at Y ≈ 132–136mm and T-branch off to `U4` (`USBLC6-4SC6`) pads as 1.4mm–2.5mm dead-end stubs before heading north to `U1` and termination resistors. Under fast sub-nanosecond ESD strikes, stub inductance blocks transient clamping, directing energy straight into `U1` (`PCA9615`).
  - **Action:** Re-route traces so that incoming lines from `J1` enter `U4` pads directly, and exit the same pad towards the termination ladder and `U1` with zero stubs.

- [ ] **Widen RJ45 Cable `SHIELD` Trace to ≥ 1.5mm – 2.0mm**
  - **Issue:** Net `SHIELD` connects the RJ45 shield tabs (`SH1`, `SH2`) to `JP13` via a 24.0mm long, 0.2mm wide trace on `B.Cu`. A 0.2mm trace has ~20 nH inductance and risks high voltage bounce or fusing during cable discharge events (CDE) or surge currents.
  - **Action:** Widen the trace connecting `SH1`, `SH2`, and `JP13.pin1` to at least 1.5mm–2.0mm, or use a local copper pour polygon.

- [ ] **Optimize Decoupling Capacitor GND Connections (`C1`–`C6`)**
  - **Issue:**
    - Bulk reservoir cap `C1` (22µF, 0805) connects its GND pin (122.95, 115.85) to its ground via with a 0.2mm trace over 1.32mm.
    - `C2` (100nF, VDDA) and `C3` (100nF, VDDB) connect their GND pins to vias using 0.2mm traces over 0.73mm and 1.29mm.
    - `C4` (100nF, ADS1115), `C5` (100nF, DS2482), and `C6` (100nF, USBLC6) similarly use 0.2mm GND necking.
  - **Action:** Move ground vias directly adjacent to the GND pads of `C1`–`C6` and widen the connecting trace to 0.5mm–0.6mm to minimize parasitic loop inductance ($L \approx 1\,\text{nH/mm}$).

- [ ] **Widen PCA9615 (`U1`) Pin 5 (`VSS`/`GND`) Connection**
  - **Issue:** Pin 5 connects to via (115.5, 118.5) through an 0.84mm long, 0.2mm trace. As a differential bus driver sinking fast edges, ground bounce can occur.
  - **Action:** Widen the connection from Pin 5 to the GND via to 0.4mm–0.5mm.

---

## 2. Medium Priority (Differential Symmetry, Crosstalk & Return Paths)

- [ ] **Tightly Couple Differential I2C Pairs (`DSCL_P/N` and `DSDA_P/N`)**
  - **Issue:** Spacing between P and N pairs varies widely between 0.45mm and 2.36mm along the route. Vias transitioning between `F.Cu` and `B.Cu` are staggered up to 2.2mm apart.
  - **Action:** Route `DSCL_P`/`DSCL_N` and `DSDA_P`/`DSDA_N` as matched pairs with uniform edge-to-edge spacing (~0.2mm–0.25mm) and place their layer-transition vias side-by-side.

- [ ] **Add Ground Stitching Vias at Signal Layer Transitions**
  - **Issue:** When `DSCL`, `DSDA`, `SCL_LOCAL`, and `SDA_LOCAL` switch between `F.Cu` and `B.Cu`, the nearest ground return vias are 1.25mm to 4.4mm away, forcing return currents through long ground plane loops.
  - **Action:** Place a ground stitching via directly adjacent to signal vias where differential or I2C clock traces change layers.

- [ ] **Increase Isolation Between Analog Sensor Inputs (`MOIST3` & `MOIST4`)**
  - **Issue:** `MOIST3` and `MOIST4` run parallel on `F.Cu` with only 0.20mm edge-to-edge spacing across ~6mm (X ≈ 105.15 to 105.55). External capacitive probes produce unfiltered analog voltages with oscillator ripple that can cross-couple between channels.
  - **Action:** Increase spacing between `MOIST3` and `MOIST4` to ≥ 0.6mm, or insert a grounded copper fill/guard trace between them. (Consider adding footprints for an RC low-pass filter, e.g., 100 Ω + 10 nF, near `U2` pins).

---

## 3. Low Priority (DFM & Documentation Consistency)

- [ ] **Eliminate Acute 45° Corners and Trace Hairpins (< 90° Acid Traps)**
  - **Issue:** Several 45° acute corners and 0° overlap reversals exist, which can trap chemical etchant during PCB manufacturing:
    - (118.75, 129.5) on `F.Cu` (`SAT_3V3` at `C6` pad)
    - (115.33, 127.58) on `F.Cu` (`DSCL_P` at `R4`)
    - (119.00, 136.10) on `F.Cu` (`DSCL_N` via branch)
    - (124.28, 141.77) on `B.Cu` (`SHIELD` at RJ45 tab)
    - Reversals/hairpins at (106.05, 128.0) and (119.85, 120.81) on `In2.Cu` (`SAT_3V3`)
  - **Action:** Convert acute corners to 45° chamfers (internal angles ≥ 135°) and ensure all T-junctions meet at 90°.

- [ ] **Update J7 Footprint Property Description**
  - **Issue:** `J7` pins are wired as Pin 1: `VCC_2`, Pin 2: `GND_2`, Pin 3: `GND`, Pin 4: `SAT_3V3`. However, the footprint's built-in `Usage` text still states: *"Auxiliary 2.54mm pin header exposing VCC_2 (Pin 1) and multiple GND_2 (Pins 2-4)"*.
  - **Action:** Update the footprint description property in the PCB/schematic to reflect the actual pinout to avoid confusion during assembly and test.

- [ ] **Add Dedicated Test Points on `B.Cu` for Production & Bench Probing**
  - **Issue:** The Satellite board currently has zero test points. Probing `SAT_3V3`, `GND`, local I2C, or differential pairs requires directly contacting fine-pitch IC pins or connector leads.
  - **Action:** Add 1.0mm test pads on `B.Cu` for `SAT_3V3`, `GND`, `SDA_LOCAL`, `SCL_LOCAL`, `DSCL+`, `DSCL-`, `DSDA+`, and `DSDA-` to facilitate automated bed-of-nails or bench multimeter/oscilloscope probing.

- [ ] **Add Optical Fiducial Markers on `F.Cu` and `B.Cu`**
  - **Issue:** The board lacks fiducials for automated SMT pick-and-place optical vision systems.
  - **Action:** Add 3 standard circular fiducials (`Fiducial_1mm_Mask2mm`, Level A) on both outer layers near the board corners.


# SunSprout Hub PCB — Layout & Routing Review Action Items

This document tracks electrical, power integrity, thermal, signal integrity, and DFM improvements identified during post-DRC routing review of `SunSproutHub.kicad_pcb`.

---

## 1. High Priority (Critical Power, Thermal & SMPS Reliability)

- [x] **Strengthen Charger Switching Nodes (`SW1_NODE` & `SW2_NODE`) Via Transitions and Fanout**
  - **Status:** **Completed.** Implemented 0.30mm pad fanouts into parallel 3-via clusters at `U8` pins 26/28, wide low-inductance polygon fills on `B.Cu`, and parallel 2-via clusters at `L1` pads.
  - **Context & Design Ceiling:** The system input current ceiling is limited to 2A and firmware limits charging current to 2A. Section 8.4.2 of the BQ25798 datasheet demonstrates routing switching nodes through vias to the bottom layer (`B.Cu`), which validates the layer-hopping topology.
  - **Issue:**
    - Pins 28 (`SW1`) and 26 (`SW2`) originally exited their QFN pads with narrow **0.20mm (8 mil) traces** over ~0.8mm–1.3mm before reaching a single via.
    - Transitioning through only a single 0.3mm drill via added ~1.2 nH parasitic inductance to the fast switching loop.
  - **Resolution:**
    - Kept the `F.Cu` pad escape necking at 0.30mm over the short ~0.8mm exit to comfortably satisfy DRC clearances.
    - Expanded into 3 parallel vias on `F.Cu` / `B.Cu` under the IC and 2 parallel vias at `L1`, cutting transition inductance by >60% and dividing current to <0.7A/via.
    - Replaced the single 0.8mm trace with wide polygon fills on `B.Cu` for low AC impedance.

- [x] **Widen High-Frequency Loop Connections on `PMID_NET` and `SYS_RAIL`**
  - **Status:** **Completed.** Fanned out `U8` pins 29 (`PMID`) and 25 (`SYS`) into solid polygon pours directly bridging into their respective decoupling capacitors on `F.Cu`, eliminating 0.20mm bottlenecks and minimizing switching ripple and loop inductance.
  - **Issue:**
    - Pin 29 (`PMID`) of `U8` carries high-frequency discontinuous input current and was necked down to a **0.20mm trace for 0.82mm** (from 50.57, 73.01 to 50.57, 72.19) before reaching its capacitor.
    - Pin 25 (`SYS_RAIL`) was necked down to a **0.20mm trace for 1.57mm** (from 52.37, 73.04 to 52.88, 71.67) before fanning out.
  - **Impact:** Choked high-frequency decoupling capacitor charge delivery, increased input/output voltage ripple, and caused unnecessary $I^2R$ power loss.
  - **Resolution:** Replaced narrow traces with wide polygon pours on `F.Cu` directly connecting IC pins to capacitor pads, passing full DRC.

- [x] **Bootstrap Capacitor Loops (`C317` / `C318`) Placement and Routing**
  - **Status:** **Completed / Closed as Designed.** Retained `C317` and `C318` on `F.Cu` connected via layer transitions.
  - **Rationale & Datasheet Reference:** TI BQ25798 datasheet Section 8.4.1 (Priority 2) explicitly states: *"The BTST capacitors can be connected with vias on both sides."* Unlike the continuous high-frequency multi-amp current loops on `PMID` and `SYS`, bootstrap capacitors only provide pulsed gate drive charge to the high-side FETs and recharge from `REGN`.
  - **DFM Advantage:** Keeping `C317` and `C318` on `F.Cu` alongside all other passives preserves single-sided SMT assembly, eliminating the costs, stencils, and yield risks of a double-sided SMT process.

- [x] **Widen Battery & High-Current Power Paths (`VBAT`, `VBAT_RAW`, `VBAT_PROTECTED`)**
  - **Status:** **Completed.** Entry into `U8` pins 22/23 is covered with a 0.8mm polygon pour, eliminating the 0.30mm neck, and `VBAT_RAW` / `VBAT_PROTECTED` high-current battery paths have wide tracks with solid filled pin connections.
  - **Issue:**
    - Battery net `VBAT` previously dropped to **0.30mm** at `U8` pins 22/23 over ~2.9mm of segments.
    - Battery lines required solid wide copper connections to handle the 2A charge/discharge current with minimal IR drop.
  - **Resolution:** Upgraded the `U8` pins 22/23 entry to a 0.8mm polygon pour and ensured wide tracks with solid pad connections across the battery path.

---

## 2. Medium Priority (Precision Sensing, Crosstalk & RF)

- [x] **Correct Kelvin Sense Routing on Fuel Gauge Shunt Resistor (`R60`)**
  - **Status:** **Completed.** Re-routed `FG_SRN` and `BATT_RTN` as an ultra-short (2.78 mm), tightly coupled parallel pair from the inner corners of `R60` pads directly to `U3` pins 9/10, matched to within 0.007 mm.
  - **Issue:**
    - `R60` is a 10 mOhm 1206 current sense resistor. Previously, sense traces connected to the outer edges of the pads where high-current traces entered, including solder fillet and copper pad resistance in the measurement.
    - Sense lines originally diverged with a large open loop area.
  - **Resolution:**
    - Connected both sense traces directly to the inside edges of `R60` pads (under the component body), bypassing all power return current and eliminating the 10%-20% measurement offset.
    - Routed as a matched parallel pair (2.7804 mm vs 2.7876 mm) with minimal loop area for high common-mode noise rejection.

- [x] **Balance Copper on Inner Signal Layers (`In2.Cu` & `In3.Cu`)**
  - **Status:** **Completed.** Added full-board GND fill zone (`"Inner GND fills"`) across `In2.Cu` and `In3.Cu` (Priority 1, 0.5mm clearance, 0.25mm min thickness), ensuring balanced copper distribution across the 6-layer stackup to eliminate reflow warpage.

- [x] **Rewire Hardware Boot Button (`SW2`) to `GPIO28` Instead of `GPIO0`**
  - **Status:** **Completed.** `U1` Pin 15 (`GPIO28`) is now connected to `BTN1_NODE` (`SW2` and debounce cap `C21`), and `GPIO0` is cleanly routed out to header `J7` pin 3 as an expansion LP I/O.
- [x] **Add Mass-Programming & Flashing Test Points to `B.Cu` (Bed-of-Nails Jig)**
  - **Status:** **Completed.** Added dedicated test points on `B.Cu`: `TP16` (`U0RXD`), `TP17` (`U0TXD`), `TP18` (`BTN1_NODE` / `GPIO28`), and `TP19` (`RESET_NODE` / `EN`), enabling automated single-sided bed-of-nails flashing.

---

## 3. Low Priority (DFM & Cleanup)

- [ ] **Fix 52 Acute Angle Corners (< 90°) and Trace Reversals (Acid Traps)**
  - **Issue:** 52 acute 45° corners and 0° trace hairpins/reversals were identified across the board, notably:
    - Overlapping 0° reversals and 45° junctions on `F.Cu` at the SW1 via (50.86, 73.96)
    - 45° T-junctions on `SYS_RAIL` at (55.96, 61.51) and (49.83, 57.92)
    - 45° T-junctions on `3V3_SYS` at (42.36, 30.34) and (45.12, 54.11)
    - Multiple 45° junctions on `GND`
  - **Action:** Bevel acute corners to 45° chamfers (internal angles ≥ 135°) and ensure all trace tees enter orthogonally at 90°.

---

## 4. Firmware & Power Architecture Checklist (Battery Sleep Optimization)

- [ ] **Float `GPIO9` and `GPIO10` Before Entering Deep Sleep (1.40 mA Leakage Fix)**
  - **Issue:** When the `TPS22918` load switch turns off `3V3_USER`, its quick output discharge (QOD) pulls the rail to 0V. Pull-ups `R201` and `R202` (4.7kΩ) connect `SDA_USER` and `SCL_USER` to `3V3_USER`. If the ESP32 enters deep sleep with `GPIO9` or `GPIO10` driving HIGH or internal pull-ups enabled, up to 1.40 mA continuously leaks into ground through the QOD.
  - **Action:** In firmware sleep routines, explicitly configure `GPIO9` and `GPIO10` as High-Z inputs with internal pull-ups and RTC pad hold disabled prior to cutting `EN_3V3_USER`.

- [ ] **Clear BQ25798 and BQ34Z100 Interrupts Prior to Deep Sleep (660 µA Leakage Fix)**
  - **Issue:** `CHG_INT` and `FG_ALERT` have 10kΩ pull-up resistors (`R24`, `R401`) to `3V3_SYS`. If an uncleared fault, charge state change, or fuel gauge alert holds either open-drain line low during sleep, each asserted line continuously drains 330 µA ($3.3\text{V} / 10\text{k}\Omega$).
  - **Action:** In firmware sleep routines, read the BQ25798 fault/status registers and BQ34Z100 flags over `LP_I2C` to clear all pending interrupts so both pins release high.


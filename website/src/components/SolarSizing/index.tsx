import React, { useState } from 'react';
import { CHEM, Chemistry, FIRMWARE_DEFAULTS as FW, MEASURED_SLEEP_MA, averageMa, size } from './model';
import styles from './styles.module.css';

function Num({ label, hint, value, set, step = 1, min = 0 }: {
  label: string;
  hint?: string;
  value: number;
  set: (v: number) => void;
  step?: number;
  min?: number;
}) {
  return (
    <label className={styles.field}>
      <span>{label}</span>
      <input type="number" value={value} step={step} min={min}
        onChange={(e) => set(parseFloat(e.target.value) || 0)} />
      {hint && <small>{hint}</small>}
    </label>
  );
}

const f = (n: number, d = 1) => (Number.isFinite(n) ? n.toFixed(d) : '∞');

export default function SolarSizing(): React.ReactElement {
  const [mode, setMode] = useState<'measured' | 'estimated'>('estimated');
  const [measuredMa, setMeasuredMa] = useState(10);
  const [sleepMa, setSleepMa] = useState(MEASURED_SLEEP_MA);
  const [activeMa, setActiveMa] = useState(80);
  const [activeS, setActiveS] = useState(FW.awakeS);
  const [sleepMin, setSleepMin] = useState(FW.sleepMin);
  const [chemistry, setChemistry] = useState<Chemistry>(FW.chemistry);
  const [batteryMah, setBatteryMah] = useState(FW.batteryMah);
  const [autonomyDays, setAutonomyDays] = useState(7);
  const [recoveryDays, setRecoveryDays] = useState(5);
  const [normalPsh, setNormalPsh] = useState(3);
  const [cloudyFraction, setCloudyFraction] = useState(0.2);
  const [efficiency, setEfficiency] = useState(0.6);
  const [chargeLimitMa, setChargeLimitMa] = useState(FW.chargeLimitMa);

  const avgMa = mode === 'measured' ? measuredMa : averageMa(sleepMa, activeMa, activeS, sleepMin);
  const inputs = (cloudy: number) => ({
    avgMa,
    chemistry,
    batteryMah,
    autonomyDays: Math.max(1, autonomyDays),
    recoveryDays: Math.max(1, recoveryDays),
    cloudyPsh: Math.max(0.01, cloudy),
    normalPsh: Math.max(0.01, normalPsh),
    efficiency: Math.min(1, Math.max(0.05, efficiency)),
    chargeLimitMa,
  });
  const r = size(inputs(normalPsh * cloudyFraction));

  return (
    <div className={styles.wrap}>
      <h3>1. Your load</h3>
      <div className={styles.tabs}>
        <button className={mode === 'measured' ? styles.on : ''} onClick={() => setMode('measured')}>
          I measured it
        </button>
        <button className={mode === 'estimated' ? styles.on : ''} onClick={() => setMode('estimated')}>
          Estimate from duty cycle
        </button>
      </div>
      {mode === 'measured' ? (
        <Num label="Average battery current (mA)" value={measuredMa} set={setMeasuredMa} step={0.1}
          hint="Mean over at least 24 h, from the gauge's average current or an energy log." />
      ) : (
        <div className={styles.grid}>
          <Num label="Sleep current (mA)" value={sleepMa} set={setSleepMa} step={0.01}
            hint="Bench-measured on one hub with no sensors. Yours will be higher with sensors fitted." />
          <Num label="Awake current (mA)" value={activeMa} set={setActiveMa}
            hint="Placeholder, not measured. Replace it with your own reading." />
          <Num label="Awake time per wake (s)" value={activeS} set={setActiveS}
            hint="Firmware default: run_duration 120 s." />
          <Num label="Sleep time between wakes (min)" value={sleepMin} set={setSleepMin}
            hint="Firmware default: sleep_duration 15 min." />
        </div>
      )}

      <h3>2. Battery</h3>
      <div className={styles.grid}>
        <label className={styles.field}>
          <span>Chemistry</span>
          <select value={chemistry} onChange={(e) => setChemistry(e.target.value as Chemistry)}>
            {Object.entries(CHEM).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
          </select>
        </label>
        <Num label="Capacity (mAh)" value={batteryMah} set={setBatteryMah} step={100}
          hint="Firmware default: battery_capacity 6000, LiFePO4." />
        <Num label="Charge current limit (mA)" value={chargeLimitMa} set={setChargeLimitMa} step={100}
          hint="Firmware default: charge_current 1000. Never above 2000." />
      </div>

      <h3>3. Weather and site</h3>
      <div className={styles.grid}>
        <Num label="Cloudy days to survive" value={autonomyDays} set={setAutonomyDays} />
        <Num label="Days allowed to recover" value={recoveryDays} set={setRecoveryDays} />
        <Num label="Normal sun hours/day" value={normalPsh} set={setNormalPsh} step={0.1}
          hint="Worst month you need to run, at the panel angle as installed." />
        <Num label="Cloudy-day fraction of normal" value={cloudyFraction} set={setCloudyFraction} step={0.05}
          hint="0.1 heavy overcast, 0.2 typical cloudy, 0.3 thin cloud." />
        <Num label="System efficiency" value={efficiency} set={setEfficiency} step={0.05}
          hint="Panel loss, MPPT, charger, dirt, heat. 0.5 to 0.7." />
      </div>

      <h3>Result</h3>
      <div className={styles.result}>
        <div><strong>{f(r.panelW)} W</strong> rated panel (at standard test conditions)</div>
        <ul>
          <li>Daily load: {f(r.dailyWh, 2)} Wh ({f(avgMa, 2)} mA average).</li>
          <li>
            Your battery holds {f(r.usableWh)} Wh usable, which is {f(r.autonomyNoSunDays)} days with no sun at all.
          </li>
          <li>
            Riding out {autonomyDays} dark days on battery alone needs {f(r.batteryNeededWh)} Wh
            ({f((r.batteryNeededWh / CHEM[chemistry].nominalV) * 1000, 0)} mAh).
          </li>
          <li>
            Set by the {r.limitedBy === 'cloudy' ? 'cloudy stretch' : 'recovery time'}:{' '}
            {f(r.panelForCloudyW)} W to ride out the cloud, {f(r.panelForRecoveryW)} W to refill in {recoveryDays} days.
          </li>
        </ul>
        {r.panelW > r.maxUsefulPanelW && (
          <p className={styles.warn}>
            The charge current limit caps useful panel power near {f(r.maxUsefulPanelW)} W. A bigger panel only helps
            in weak light. Raise the limit (never above 2000 mA) or add battery instead.
          </p>
        )}
      </div>

      <h3>How much the answer moves</h3>
      <table>
        <thead>
          <tr><th>If cloudy days are really...</th><th>Cloudy-day fraction</th><th>Panel</th></tr>
        </thead>
        <tbody>
          {[0.5, 1, 1.5].map((m) => (
            <tr key={m}>
              <td>{m === 1 ? 'as entered' : m < 1 ? 'darker' : 'brighter'}</td>
              <td>{f(cloudyFraction * m, 2)}</td>
              <td>{f(size(inputs(normalPsh * cloudyFraction * m)).panelW)} W</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

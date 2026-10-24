export type Chemistry = 'liion' | 'lifepo4';

export interface Inputs {
  avgMa: number; // mean battery-side current over a full wake cycle, mA
  chemistry: Chemistry;
  batteryMah: number;
  autonomyDays: number; // cloudy days to ride through
  recoveryDays: number; // days of normal sun allowed to refill the battery
  cloudyPsh: number; // peak-sun-hours per day during the cloudy stretch
  normalPsh: number; // peak-sun-hours per day in normal weather, same month
  efficiency: number; // panel Wh at STC to Wh into the battery, 0..1
  chargeLimitMa: number; // firmware charge current limit
}

export const CHEM = {
  liion: { label: 'Li-ion / Li-Po', nominalV: 3.7, fullV: 4.2, usable: 0.8 },
  lifepo4: { label: 'LiFePO4', nominalV: 3.2, fullV: 3.65, usable: 0.9 },
} as const;

export interface Result {
  dailyWh: number;
  batteryWh: number;
  usableWh: number;
  batteryNeededWh: number; // for the whole cloudy stretch with no sun at all
  autonomyNoSunDays: number;
  panelForCloudyW: number;
  panelForRecoveryW: number;
  panelW: number;
  limitedBy: 'cloudy' | 'recovery';
  maxUsefulPanelW: number;
}

export function size(i: Inputs): Result {
  const c = CHEM[i.chemistry];
  const dailyWh = (i.avgMa * c.nominalV * 24) / 1000;
  const batteryWh = (i.batteryMah * c.nominalV) / 1000;
  const usableWh = batteryWh * c.usable;
  // Each cloudy day the panel covers some of the load; the battery covers the rest.
  const panelForCloudyW = Math.max(0, dailyWh - usableWh / i.autonomyDays) / (i.cloudyPsh * i.efficiency);
  // After the stretch the panel has to carry the load and refill the reserve.
  const panelForRecoveryW = (dailyWh + usableWh / i.recoveryDays) / (i.normalPsh * i.efficiency);
  const panelW = Math.max(panelForCloudyW, panelForRecoveryW);
  return {
    dailyWh,
    batteryWh,
    usableWh,
    batteryNeededWh: (dailyWh * i.autonomyDays) / c.usable,
    autonomyNoSunDays: dailyWh > 0 ? usableWh / dailyWh : Infinity,
    panelForCloudyW,
    panelForRecoveryW,
    panelW,
    limitedBy: panelForCloudyW >= panelForRecoveryW ? 'cloudy' : 'recovery',
    // The charge current limit caps what a panel can deliver at full sun.
    maxUsefulPanelW: ((i.chargeLimitMa / 1000) * c.fullV) / i.efficiency,
  };
}

export function averageMa(sleepMa: number, activeMa: number, activeS: number, intervalMin: number): number {
  const cycle = intervalMin * 60;
  return (sleepMa * Math.max(0, cycle - activeS) + activeMa * activeS) / cycle;
}

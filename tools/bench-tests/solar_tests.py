"""Solar tests driven over the ESPHome API.

Usage: python -I solar_tests.py <host> <secrets.yaml> <phase> <seconds> [csv_out]
  phase = watch   (no changes, just sample)
        = solar   (turn 'Enable Solar Input' on, then sample)
        = mppt    (turn 'Enable MPPT' on, then sample)
        = ratio:<option>  (set 'MPPT Voltage Ratio' to <option>, then sample)
"""
import asyncio
import csv
import re
import sys
import time

import aioesphomeapi

host, secrets_path, phase, seconds = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
csv_out = sys.argv[5] if len(sys.argv) > 5 else None
key = next(re.match(r'\s*(?:esphome|api)_encryption_key:\s*"?([^"\s]+)"?', l).group(1)
           for l in open(secrets_path, encoding="utf-8") if re.match(r'\s*(?:esphome|api)_encryption_key:', l))

COLS = ("Solar Input Voltage", "Solar Input Present", "USB Input Present", "Input Present", "Input Source",
        "Input Voltage", "Input Current", "Input Voltage Limit", "Charging", "Charge Status", "Battery Current",
        "Battery Voltage", "Enable Solar Input", "Enable MPPT", "MPPT Voltage Ratio", "Charger Temperature",
        "Charger Fault", "Charger Thermal Regulation")


async def main():
    api = aioesphomeapi.APIClient(host, 6053, None, noise_psk=key)
    await api.connect(login=True)
    ents, _ = await api.list_entities_services()
    by = {e.name: e for e in ents}
    keys = {e.key: e.name for e in ents if e.name in COLS}
    st = {}
    api.subscribe_states(lambda s: st.__setitem__(keys[s.key], (round(getattr(s, "state", None), 3)
                         if isinstance(getattr(s, "state", None), float) else getattr(s, "state", None)))
                         if s.key in keys else None)
    api.subscribe_logs(lambda m: print("   LOG", re.sub(r"\x1b\[[0-9;]*m", "", m.message.decode() if isinstance(m.message, bytes) else m.message), flush=True)
                       if "bq25798" in (m.message.decode() if isinstance(m.message, bytes) else m.message) and
                       "[D]" not in (m.message.decode() if isinstance(m.message, bytes) else m.message)[:6] else None,
                       log_level=aioesphomeapi.LogLevel.LOG_LEVEL_DEBUG)
    await asyncio.sleep(5)
    t0 = time.time()
    rows = []

    def sample():
        r = {c: st.get(c) for c in COLS}
        r["t_s"] = round(time.time() - t0)
        vin, iin = r["Input Voltage"], r["Input Current"]
        r["Pin_W"] = round(vin * iin / 1000, 2) if isinstance(vin, (int, float)) and isinstance(iin, (int, float)) else None
        rows.append(r)
        print(f"{r['t_s']:5d}s Vsol={r['Solar Input Voltage']} Vin={vin} Iin={iin}mA Pin={r['Pin_W']}W VINDPM={r['Input Voltage Limit']} "
              f"src={r['Input Source']} chg={r['Charging']}/{r['Charge Status']} Ibat={r['Battery Current']} Vbat={r['Battery Voltage']} "
              f"EN_solar={r['Enable Solar Input']} MPPT={r['Enable MPPT']} die={r['Charger Temperature']}C therm={r['Charger Thermal Regulation']}", flush=True)

    sample()
    if phase == "solar":
        print(">>> Enable Solar Input -> ON", flush=True)
        api.switch_command(by["Enable Solar Input"].key, True)
    elif phase == "hiz":
        print(">>> Charger HIZ Mode -> ON for 4 s, then OFF (restarts input qualification)", flush=True)
        api.switch_command(by["Charger HIZ Mode"].key, True)
        await asyncio.sleep(4)
        api.switch_command(by["Charger HIZ Mode"].key, False)
    elif phase.startswith("ichg:"):
        target = float(phase.split(":", 1)[1])
        print(f">>> Charge Current Limit -> {target:.0f} mA", flush=True)
        api.number_command(by["Charge Current Limit"].key, target)
    elif phase == "mppt":
        print(">>> Enable MPPT -> ON", flush=True)
        api.switch_command(by["Enable MPPT"].key, True)
    elif phase.startswith("ratio:"):
        opt = phase.split(":", 1)[1]
        print(f">>> MPPT Voltage Ratio -> {opt}", flush=True)
        api.select_command(by["MPPT Voltage Ratio"].key, opt)
    end = time.time() + seconds
    while time.time() < end:
        await asyncio.sleep(15)
        sample()
    if csv_out:
        new = not __import__("os").path.exists(csv_out)
        with open(csv_out, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            if new:
                w.writeheader()
            w.writerows(rows)
    await api.disconnect()


asyncio.run(main())

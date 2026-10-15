"""API-driven charger tests for a SunSprout board.

Usage: python -I charger_tests.py <host> <secrets.yaml> <test> [csv_out]
  test = interrupt | reset | ramp | log
"""
import asyncio
import csv
import re
import sys
import time

import aioesphomeapi

host, secrets_path, test = sys.argv[1], sys.argv[2], sys.argv[3]
csv_out = sys.argv[4] if len(sys.argv) > 4 else None
key = next(re.match(r'\s*(?:esphome|api)_encryption_key:\s*"?([^"\s]+)"?', l).group(1)
           for l in open(secrets_path, encoding="utf-8") if re.match(r'\s*(?:esphome|api)_encryption_key:', l))

SAMPLE = ("Charge Current Limit", "Charge Status", "Charger Fault", "Charger Temperature", "Battery Temperature",
          "Input Current", "Input Voltage", "Battery Current", "Battery Voltage", "System Voltage", "Charging",
          "Charger Thermal Regulation", "Battery Fully Charged", "Input Selection", "Active Input", "Charger Interrupt",
          "Battery Level")


async def connect():
    api = aioesphomeapi.APIClient(host, 6053, None, noise_psk=key)
    await api.connect(login=True)
    ents, _ = await api.list_entities_services()
    by_name = {e.name: e for e in ents}
    keys = {e.key: e.name for e in ents if e.name in SAMPLE}
    state, events = {}, []
    t0 = time.time()

    def on_state(s):
        n = keys.get(s.key)
        if n is None:
            return
        v = getattr(s, "state", None)
        v = round(v, 3) if isinstance(v, float) else v
        if state.get(n) != v:
            events.append((time.time() - t0, n, v))
        state[n] = v

    logs = []

    def on_log(m):
        t = m.message.decode("utf-8", "replace") if isinstance(m.message, bytes) else m.message
        t = re.sub(r"\x1b\[[0-9;]*m", "", t)
        if "bq25798" in t and not t.startswith("[D]"):
            logs.append((time.time() - t0, t))
            print(f"{time.time() - t0:7.1f}s  LOG {t}", flush=True)

    api.subscribe_states(on_state)
    api.subscribe_logs(on_log, log_level=aioesphomeapi.LogLevel.LOG_LEVEL_DEBUG)
    await asyncio.sleep(5)
    return api, by_name, state, events, logs, t0


def snap(state):
    return {n: state.get(n) for n in SAMPLE}


async def t_interrupt():
    api, ents, state, events, logs, t0 = await connect()
    sel = ents["Input Selection"]
    print("start:", {k: state.get(k) for k in ("Input Selection", "Active Input", "Charging", "Charger Interrupt")}, flush=True)
    for cycle in (1, 2):
        for opt, wait in (("Off", 12), ("Auto", 30)):
            mark = len(events)
            print(f"{time.time() - t0:7.1f}s  >>> select {opt} (cycle {cycle})", flush=True)
            api.select_command(sel.key, opt)
            await asyncio.sleep(wait)
            ints = [(round(t, 1), v) for t, n, v in events[mark:] if n == "Charger Interrupt"]
            print(f"{time.time() - t0:7.1f}s  after {opt}: Charger Interrupt edges = {ints}  "
                  f"active={state.get('Active Input')} charging={state.get('Charging')}", flush=True)
    await api.disconnect()


async def t_reset():
    api, ents, state, events, logs, t0 = await connect()
    before = snap(state)
    print("BEFORE:", before, flush=True)
    api.button_command(ents["Reset Charger Registers"].key)
    print(f"{time.time() - t0:7.1f}s  >>> pressed Reset Charger Registers", flush=True)
    await asyncio.sleep(60)
    after = snap(state)
    print("AFTER :", after, flush=True)
    changed = {k: (before[k], after[k]) for k in SAMPLE if before[k] != after[k]}
    print("changed:", changed, flush=True)
    await api.disconnect()


async def t_ramp():
    api, ents, state, events, logs, t0 = await connect()
    num = ents["Charge Current Limit"]
    original = state.get("Charge Current Limit") or 500.0
    rows = []
    abort = None
    hot = 0
    try:
        for target in (500.0, 1000.0, 1500.0, 2000.0):
            print(f"{time.time() - t0:7.1f}s  >>> charge current limit {target:.0f} mA", flush=True)
            api.number_command(num.key, target)
            end = time.time() + 240
            while time.time() < end and abort is None:
                await asyncio.sleep(30)
                s = snap(state)
                s["t"] = round(time.time() - t0)
                s["target_mA"] = target
                rows.append(s)
                print(f"{s['t']:5d}s target={target:.0f} ichg={s['Battery Current']} iin={s['Input Current']} "
                      f"vbat={s['Battery Voltage']} die={s['Charger Temperature']}C ts={s['Battery Temperature']}C "
                      f"status={s['Charge Status']} therm={s['Charger Thermal Regulation']} fault={s['Charger Fault']}", flush=True)
                temp = s["Charger Temperature"]
                if s["Charger Fault"] not in (None, "OK", "No fault"):
                    abort = f"charger fault: {s['Charger Fault']}"
                elif isinstance(temp, (int, float)) and temp > 85:
                    abort = f"charger temperature {temp} C"
                hot = hot + 1 if s["Charger Thermal Regulation"] else 0
                if hot >= 2:
                    abort = "thermal regulation active for two samples"
            if abort:
                break
    finally:
        print(f"--- restoring charge current to {original:.0f} mA" + (f" (aborted: {abort})" if abort else ""), flush=True)
        api.number_command(num.key, float(original))
        await asyncio.sleep(5)
        if csv_out and rows:
            with open(csv_out, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)
        await api.disconnect()


async def t_log():
    api, ents, state, events, logs, t0 = await connect()
    rows = []
    done_reason = None
    deadline = time.time() + 10 * 3600
    with open(csv_out, "w", newline="", encoding="utf-8") as f:
        w = None
        while time.time() < deadline:
            s = snap(state)
            s["t_s"] = round(time.time() - t0)
            if w is None:
                w = csv.DictWriter(f, fieldnames=list(s.keys()))
                w.writeheader()
            w.writerow(s)
            f.flush()
            print(f"{s['t_s']:6d}s vbat={s['Battery Voltage']} ichg={s['Battery Current']} status={s['Charge Status']} "
                  f"full={s['Battery Fully Charged']} lvl={s['Battery Level']}", flush=True)
            # The gauge's own "fully charged" flag is unreliable until it has learned the cell, so only the charger counts.
            if isinstance(s["Charge Status"], str) and "terminat" in s["Charge Status"].lower():
                done_reason = f"charge ended: {s['Charge Status']}"
                break
            await asyncio.sleep(30)
    print("DONE:", done_reason or "time limit", flush=True)
    await api.disconnect()


asyncio.run({"interrupt": t_interrupt, "reset": t_reset, "ramp": t_ramp, "log": t_log}[test]())

"""Drive the 'Input Selection' drop-down through a sequence and log what the board reports.

Usage: python -I select_sequence.py <host> <secrets.yaml> <wait_s> <option> [<option> ...]
"""
import asyncio
import re
import sys
import time

import aioesphomeapi

host, secrets_path, wait_s = sys.argv[1], sys.argv[2], float(sys.argv[3])
steps = sys.argv[4:]
key = next(re.match(r'\s*(?:esphome|api)_encryption_key:\s*"?([^"\s]+)"?', l).group(1)
           for l in open(secrets_path, encoding="utf-8") if re.match(r'\s*(?:esphome|api)_encryption_key:', l))
WATCH = ("Input Selection", "Active Input", "Input Present", "USB Input Present", "Solar Input Present",
         "Input Current", "Charging", "Battery Current", "Enable USB Input", "Enable Solar Input",
         "Input Voltage", "USB Input Voltage", "Solar Input Voltage")


async def main():
    api = aioesphomeapi.APIClient(host, 6053, None, noise_psk=key)
    await api.connect(login=True)
    ents, _ = await api.list_entities_services()
    names = {e.key: e.name for e in ents if e.name in WATCH}
    sel = next(e for e in ents if e.name == "Input Selection")
    t0 = time.time()
    state = {}

    def stamp():
        return f"{time.time() - t0:6.1f}s"

    def on_state(s):
        n = names.get(s.key)
        if n is None:
            return
        v = getattr(s, "state", None)
        v = round(v, 3) if isinstance(v, float) else v
        if state.get(n) != v:
            print(f"{stamp()}  {n}: {v}", flush=True)
        state[n] = v

    def on_log(m):
        t = m.message.decode("utf-8", "replace") if isinstance(m.message, bytes) else m.message
        t = re.sub(r"\x1b\[[0-9;]*m", "", t)
        if "bq25798" in t and any(w in t for w in ("overrode", "selection", "VBUS still", "Watchdog")):
            print(f"{stamp()}  LOG {t}", flush=True)

    api.subscribe_states(on_state)
    api.subscribe_logs(on_log, log_level=aioesphomeapi.LogLevel.LOG_LEVEL_DEBUG)
    await asyncio.sleep(5)
    print(f"{stamp()}  --- start: selection={state.get('Input Selection')} active={state.get('Active Input')}", flush=True)
    for opt in steps:
        print(f"{stamp()}  >>> select '{opt}'", flush=True)
        api.select_command(sel.key, opt)
        await asyncio.sleep(wait_s)
        print(f"{stamp()}  --- after '{opt}': selection={state.get('Input Selection')} active={state.get('Active Input')} "
              f"Vbus={state.get('Input Voltage')} Vusb={state.get('USB Input Voltage')} Vsolar={state.get('Solar Input Voltage')} Iin={state.get('Input Current')} charging={state.get('Charging')}", flush=True)
    await api.disconnect()


asyncio.run(main())

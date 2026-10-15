"""Toggle 'Enable USB Input' on a board and log the charger's readings over time.

Usage: python -I usb_switch_test.py <host> <secrets.yaml> <off_seconds>
Always turns the switch back to its original state at the end.
"""
import asyncio
import re
import sys
import time

import aioesphomeapi

host, secrets_path, off_seconds = sys.argv[1], sys.argv[2], float(sys.argv[3])
key = next(re.match(r'\s*(?:esphome|api)_encryption_key:\s*"?([^"\s]+)"?', l).group(1)
           for l in open(secrets_path, encoding="utf-8") if re.match(r'\s*(?:esphome|api)_encryption_key:', l))

WATCH = ("Enable USB Input", "USB Input Present", "Input Present", "USB Input Voltage", "Input Voltage",
         "Input Current", "Charging", "Charge Status", "Battery Current", "Input Source", "Power Good")


async def main():
    api = aioesphomeapi.APIClient(host, 6053, None, noise_psk=key)
    await api.connect(login=True)
    entities, _ = await api.list_entities_services()
    names = {e.key: e.name for e in entities if e.name in WATCH}
    sw = next(e for e in entities if e.name == "Enable USB Input")
    state = {}
    log = []
    t0 = time.time()

    def on_state(s):
        n = names.get(s.key)
        if n is None:
            return
        v = getattr(s, "state", None)
        if isinstance(v, float):
            v = round(v, 3)
        if state.get(n) != v:
            log.append((time.time() - t0, n, v))
            print(f"{time.time() - t0:6.1f}s  {n}: {v}", flush=True)
        state[n] = v

    api.subscribe_states(on_state)
    await asyncio.sleep(4)
    original = state.get("Enable USB Input")
    print(f"--- original 'Enable USB Input' = {original}; turning it OFF ---", flush=True)
    api.switch_command(sw.key, False)
    await asyncio.sleep(off_seconds)
    print("--- restoring ---", flush=True)
    api.switch_command(sw.key, bool(original))
    await asyncio.sleep(40)
    print("--- final ---", flush=True)
    for n in WATCH:
        print(f"{n}: {state.get(n)}")
    await api.disconnect()


asyncio.run(main())

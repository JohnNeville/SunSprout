"""Press a button on the board and print/save the matching log lines.

Usage: python -I press_and_watch.py <host> <secrets.yaml> <button name> <end marker> <out file> [timeout s]
With button name "-" it only prints a few sensor states and exits.
"""
import asyncio
import re
import sys

import aioesphomeapi

host, secrets_path, button_name, end_marker, out_path = sys.argv[1:6]
timeout = float(sys.argv[6]) if len(sys.argv) > 6 else 90
key = None
for line in open(secrets_path, encoding="utf-8"):
    m = re.match(r'\s*(?:esphome|api)_encryption_key:\s*"?([^"\s]+)"?', line)
    if m:
        key = m.group(1)

lines = []
done = asyncio.Event()


def on_log(msg):
    text = msg.message
    if isinstance(text, bytes):
        text = text.decode("utf-8", "replace")
    text = re.sub(r"\x1b\[[0-9;]*m", "", text)
    if "bq34z100" in text:
        lines.append(text)
        print(text, flush=True)
        if end_marker in text:
            done.set()


async def main():
    api = aioesphomeapi.APIClient(host, 6053, None, noise_psk=key)
    await api.connect(login=True)
    entities, _ = await api.list_entities_services()
    if button_name == "-":
        want = ("Battery Voltage", "Battery Current", "Charging", "Charge Status", "Gauge Chemistry ID",
                "Input Present", "Fuel Gauge Alert", "Battery Level")
        keys = {e.key: e.name for e in entities if e.name in want}
        got = {}
        api.subscribe_states(lambda s: got.__setitem__(keys.get(s.key), getattr(s, "state", None))
                             if s.key in keys else None)
        await asyncio.sleep(4)
        for n in want:
            print(f"{n}: {got.get(n)}")
        await api.disconnect()
        return
    btn = next(e for e in entities if e.name == button_name)
    api.subscribe_logs(on_log, log_level=aioesphomeapi.LogLevel.LOG_LEVEL_DEBUG)
    await asyncio.sleep(1)
    api.button_command(btn.key)
    print(f"--- pressed '{button_name}' ---", flush=True)
    try:
        await asyncio.wait_for(done.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        print("--- TIMED OUT waiting for the end marker ---")
    await asyncio.sleep(1)
    await api.disconnect()
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


asyncio.run(main())

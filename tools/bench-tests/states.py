import asyncio, re, sys
import aioesphomeapi
host, secrets = sys.argv[1:3]
names = sys.argv[3:]
key = next(re.match(r'\s*(?:esphome|api)_encryption_key:\s*"?([^"\s]+)"?', l).group(1) for l in open(secrets, encoding="utf-8") if re.match(r'\s*(?:esphome|api)_encryption_key:', l))
async def main():
    api = aioesphomeapi.APIClient(host, 6053, None, noise_psk=key)
    await api.connect(login=True)
    ents, _ = await api.list_entities_services()
    keys = {e.key: e.name for e in ents if e.name in names}
    got = {}
    api.subscribe_states(lambda s: got.__setitem__(keys[s.key], getattr(s, "state", None)) if s.key in keys else None)
    await asyncio.sleep(4)
    for n in names:
        v = got.get(n, "(not found)" if n not in keys.values() else None)
        print(f"{n}: {round(v,3) if isinstance(v,float) else v}")
    await api.disconnect()
asyncio.run(main())

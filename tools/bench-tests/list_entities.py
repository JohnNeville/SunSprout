import asyncio, re, sys
import aioesphomeapi
host, secrets = sys.argv[1:3]
key = next(re.match(r'\s*(?:esphome|api)_encryption_key:\s*"?([^"\s]+)"?', l).group(1) for l in open(secrets, encoding="utf-8") if re.match(r'\s*(?:esphome|api)_encryption_key:', l))
async def main():
    api = aioesphomeapi.APIClient(host, 6053, None, noise_psk=key)
    await api.connect(login=True)
    ents, _ = await api.list_entities_services()
    pat = re.compile(sys.argv[3], re.I)
    for e in sorted(ents, key=lambda e: e.name):
        if pat.search(e.name):
            print(f"{type(e).__name__.replace('Info',''):14s} {e.name}  (disabled_by_default={getattr(e,'disabled_by_default',None)})")
    await api.disconnect()
asyncio.run(main())

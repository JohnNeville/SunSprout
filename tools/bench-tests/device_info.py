import asyncio, re, sys
import aioesphomeapi
host, secrets_path = sys.argv[1:3]
key = next(re.match(r'\s*(?:esphome|api)_encryption_key:\s*"?([^"\s]+)"?', l).group(1) for l in open(secrets_path, encoding="utf-8") if re.match(r'\s*(?:esphome|api)_encryption_key:', l))
async def main():
    api = aioesphomeapi.APIClient(host, 6053, None, noise_psk=(None if len(sys.argv) > 3 else key))
    await api.connect(login=True)
    i = await api.device_info()
    print("name:", i.name, "| mac:", i.mac_address, "| esphome:", i.esphome_version, "| compiled:", i.compilation_time)
    ents, _ = await api.list_entities_services()
    names = sorted(e.name for e in ents)
    print(len(names), "entities")
    await api.disconnect()
asyncio.run(main())

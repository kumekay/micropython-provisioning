import network
import uasyncio as asyncio


class Provisioning:
    def __init__(self, store, transport, debug=False):
        self.store = store
        self.transport = transport
        self.debug = debug

    async def connect(self):
        debug = self.debug
        try:
            creds = await self.store.read()
            debug and print("Loaded previously saved credentials", dict(creds))
        except ValueError:
            debug and print("Await credentials")
            creds = await self.transport()
            await self.store.write(**creds)
            debug and print("Got credentials", dict(creds))

        return await self.connect_sta(creds["ssid"], creds["pw"])

    async def connect_sta(self, ssid, pw):
        sleep_ms = asyncio.sleep_ms
        debug = self.debug
        wlan = network.WLAN(network.STA_IF)

        wlan.active(True)
        await sleep_ms(0)

        if not wlan.isconnected():
            wlan.connect(ssid, pw)
            debug and print("Connecting to", ssid)
            while not wlan.isconnected():
                await sleep_ms(50)
        return wlan

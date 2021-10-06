import network
import uasyncio as asyncio


class Provisioning:
    def __init__(self, store, transport, debug=False):
        self.store = store
        self.transport = transport
        self.debug = debug

    async def connect(self):
        try:
            creds = await self.store.read()
            self.debug and print("Loaded previously saved credentials", dict(creds))
        except ValueError:
            self.debug and print("Await credentials")
            creds = await self.transport()
            await self.store.write(**creds)
            self.debug and print("Got credentials", dict(creds))

        return await self.connect_sta(creds["ssid"], creds["pw"])

    async def connect_sta(self, ssid, pw):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        await asyncio.sleep_ms(0)

        if not wlan.isconnected():
            wlan.connect(ssid, pw)
            self.debug and print("Connecting to", ssid)
            while not wlan.isconnected():
                await asyncio.sleep_ms(50)
        return wlan

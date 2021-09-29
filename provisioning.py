import network
import uasyncio as asyncio
from esp32 import NVS


class CredStore:
    def __init__(self, nvs_ns="wifi"):
        self.nvs_ns = nvs_ns
        self.nvs = NVS(self.nvs_ns)
        self._ssid = bytearray()
        self._pw = bytearray()

    def reset(self):
        self.nvs.erase_key("ssid")
        self.nvs.erase_key("pw")
        self.nvs.commit()

    def save(self, ssid, pw):
        self.nvs.set_blob("ssid", ssid)
        self.nvs.set_blob("pw", pw)
        self.nvs.commit()

    def read(self):
        try:
            self.nvs.get_blob("ssid", self._ssid)
            self.nvs.get_blob("pw", self._pw)
            return self._ssid, self._pw
        except OSError:
            return None


class Provisioning:
    def __init__(self, credStore=None):
        if not credStore:
            credStore = CredStore()
        self.credStore = credStore

    async def connect(self):
        creds = self.credStore.read()
        if creds:
            await self.connect_sta(*creds)
        else:
            # Start provisioning
            pass

    async def connect_sta(self, ssid, pw):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        await asyncio.sleep_ms(0)

        if not wlan.isconnected():
            wlan.connect(ssid, pw)
            while not wlan.isconnected():
                await asyncio.sleep_ms(50)
        return wlan

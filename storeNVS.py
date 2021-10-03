from esp32 import NVS

SIZES = {"ssid": 32, "pw": 63}

DEFAULT_SIZE = 64


class StoreNVS:
    def __init__(self, nvs_ns="prov", required_keys=("ssid", "pw"), extra_keys=None, debug=False):
        self.nvs_ns = nvs_ns
        self.nvs = NVS(self.nvs_ns)
        self.required_keys = required_keys
        self.keys = required_keys
        self.debug = debug

        if extra_keys:
            self.keys = list(self.keys).extend(extra_keys)

    async def reset(self):
        for k in self.keys:
            try:
                self.nvs.erase_key(k)
            except OSError:
                pass
        self.nvs.commit()

    async def write(self, **kwargs):
        self.debug and print("Saving credentials to NVS", kwargs)
        for k, v in kwargs.items():
            self.nvs.set_blob(k, v)
        self.nvs.commit()

    async def read(self):
        data = {}
        for k in self.keys:
            try:
                v = bytearray(SIZES.get(k, DEFAULT_SIZE))
                l = self.nvs.get_blob(k, v)
                data[k] = v[:l].decode()
            except OSError:
                if k in self.required_keys:
                    raise ValueError('Required key "{}" not found'.format(k))

        return data

from binascii import hexlify

import network
from machine import unique_id
from microdot_asyncio import Microdot, Response

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio


class TransportSoftAP:
    def __init__(self, ssid=None, pw=None, port=80, required_keys=("ssid", "pw"), extra_keys=None, debug=False):
        if ssid is None:
            ssid = "esp_{}".format(hexlify(unique_id())[:8].decode("ascii"))
        self.ssid = ssid
        self.pw = pw
        self.port = port
        self.required_keys = required_keys
        self.all_keys = required_keys
        if extra_keys:
            self.all_keys = extra_keys.extend(required_keys)
        self.creds = None
        self.debug = debug

        app = Microdot()
        self.app = app
        self.provisioned = asyncio.Event()

        @app.route("/")
        async def show_ui(request):
            return Response.send_file("provision.html")

        @app.route("/networks")
        async def list_networks(request):
            wlan = network.WLAN(network.STA_IF)
            await asyncio.sleep(0)
            wlan.active(True)
            await asyncio.sleep(0)
            networks = wlan.scan()
            print(networks)
            return Response(networks)

        @app.route("/", methods=["POST"])
        async def save_creds(request):
            self.debug and print("Credentials in HTTP request:", request.json)
            # Validate
            try:
                for k, v in request.json.items():
                    if not k in self.all_keys:
                        return Response('Key "{}" is unknown'.format(k), status_code=400)
                    if not isinstance(k, str) or not isinstance(v, str):
                        raise TypeError()
            except (AttributeError, TypeError):
                return Response("Credentials must be a JSON object with string keys and values", status_code=400)

            for k in self.required_keys:
                if k not in request.json:
                    Response('Required key "{}" is missing'.format(k), status_code=400)

            self.creds = request.json
            self.provisioned.set()
            return Response(status_code=204)

    async def __call__(self):
        # Init AP
        ap = network.WLAN(network.AP_IF)
        ap.config(essid=self.ssid)
        ap.config(max_clients=2)
        if self.pw:
            ap.config(password=self.pw)

        ap.active(True)
        while ap.active() == False:
            await asyncio.sleep(0.1)

        asyncio.create_task(self.app.start_server(port=self.port, debug=self.debug))
        await self.provisioned.wait()
        asyncio.create_task(self._shutdown(ap))
        return self.creds

    async def _shutdown(self, ap):
        # Let current requrests to finish
        await asyncio.sleep(3)
        ap.active(False)
        self.app.shutdown()

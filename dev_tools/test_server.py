#! /usr/bin/env python3

import asyncio

from pathlib import Path
from microdot_asyncio import Microdot, Response
from binascii import hexlify


class TestServer:
    def __init__(self, port=8080, required_keys=("ssid", "pw"), extra_keys=None, debug=False):
        self.port = port
        self.required_keys = required_keys
        self.all_keys = required_keys
        if extra_keys:
            self.all_keys = extra_keys.extend(required_keys)
        self.creds = None
        self.debug = debug

        app = Microdot()
        self.app = app

        @app.route("/")
        async def show_ui(request):
            return Response.send_file((Path(__file__).parent / ".." / "src" / "provision.html").as_posix())

        @app.route("/networks")
        async def list_networks(request):
            # Mock wlan.scan() output
            raw_net_data = [
                (b"fnusa-guest", b"\xa0\xec\xf9Z\xfb6", 1, -76, 5, False),
                (b"fnusa-priv", b"\xa0\xec\xf9Z\xfb5", 1, -76, 5, False),
                (b"fnusa-free", b"\xa0\xec\xf9Z\xfb8", 1, -76, 0, False),
                (b"kumph", b"\xa6\xe3\xbd\x94`\x89", 10, -76, 3, False),
                (b"eduroam", b"\xa0\xec\xf9Z\xfb9", 1, -77, 5, False),
            ]
            nets = [
                {
                    "ssid": i[0].decode(),
                    "bssid": hexlify(i[1]).decode(),
                    "channel": i[2],
                    "rssi": i[3],
                    "auth": i[4],
                    "hidden": bool(i[5]),
                }
                for i in raw_net_data
            ]
            return Response(nets)

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

            return Response(status_code=204)

    async def __call__(self):
        await self.app.start_server(port=self.port, debug=self.debug)


if __name__ == "__main__":
    asyncio.run(TestServer(port=8080, debug=True)())

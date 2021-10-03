import sys

import neopixel
import uasyncio as asyncio
from machine import Pin
from provisioning import Provisioning
from storeNVS import StoreNVS
from transportSoftAP import TransportSoftAP

led_pin = Pin(8, Pin.OUT)
led = neopixel.NeoPixel(led_pin, 1)


async def blink():
    b = 10
    while True:
        led[0] = (0, b, 0)
        b = b ^ 10
        led.write()
        await asyncio.sleep_ms(20)


async def main():
    asyncio.create_task(blink())
    transport = TransportSoftAP(debug=True)
    store = StoreNVS(debug=True)
    wlan = await Provisioning(store, transport, debug=True).connect()
    print(wlan.ifconfig())
    for i in range(100, 0, -1):
        print("resetting in", i)
        await asyncio.sleep(1)
    await store.reset()


try:
    asyncio.run(main())
except (KeyboardInterrupt, Exception) as e:
    sys.print_exception(e)
finally:
    asyncio.new_event_loop()

import sys

from micropython import const
import neopixel
import uasyncio as asyncio
from machine import Pin, mem32
from provisioning import Provisioning
from storeNVS import StoreNVS
from transportSoftAP import TransportSoftAP


def invert_pin(n, invert=True):
    # https://www.espressif.com/sites/default/files/documentation/esp32_technical_reference_manual_en.pdf
    # page 70
    pin_reg = 0x3FF44530 + 0x4 * n
    mem32[pin_reg] |= int(invert) << 9


class Button:
    def __init__(self, pin, on_press=None, on_release=None, debounce_ms=50, off_state=None):
        self.pin = pin
        self.on_press = on_press
        self.on_release = on_release
        self.debounce_ms = debounce_ms

        if off_state is None:
            off_state = pin.value()
        self.off_state = off_state

        self.state = self.raw_state()

        asyncio.create_task(self.update_state())

    def raw_state(self):
        return bool(self.pin.value() ^ self.off_state)

    async def update_state(self):
        while True:
            current_state = self.raw_state()

            if self.state != current_state:
                if current_state:
                    self.on_press and asyncio.create_task(self.on_press())
                else:
                    self.on_release and asyncio.create_task(self.on_release())

                self.state = current_state

            await asyncio.sleep_ms(self.debounce_ms)


async def blink():
    LED_PIN = const(25)
    BRIGHTNESS = const(3)

    led_pin = Pin(LED_PIN, Pin.OUT)
    led = neopixel.NeoPixel(led_pin, 1)
    invert_pin(LED_PIN)

    b = 0
    while True:
        b = b ^ BRIGHTNESS
        led[0] = (b, 0, 0)
        led.write()
        await asyncio.sleep_ms(500)


async def main():
    RESET_BUTTON_PIN = const(32)
    asyncio.create_task(blink())
    transport = TransportSoftAP(debug=True)
    store = StoreNVS(debug=True)

    async def on_reset():
        print("Reset settings")
        await store.reset()

    Button(Pin(RESET_BUTTON_PIN, Pin.IN, Pin.PULL_UP), on_release=on_reset, off_state=True)
    wlan = await Provisioning(store, transport, debug=True).connect()
    print(wlan.ifconfig())

    while True:
        await asyncio.sleep(1)


try:
    asyncio.run(main())
except (KeyboardInterrupt, Exception) as e:
    sys.print_exception(e)
finally:
    asyncio.new_event_loop()

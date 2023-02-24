from rpi_ws281x import Adafruit_NeoPixel, Color

LED_COUNT = 30
LED_PIN = 18
LED_BRIGHTNESS = 255
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_INVERT = False


def led_setup():
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
    strip.begin()
    return strip


def set_led_mode(strip, mode: int):
    mode_list = [(0, 0, 0),  # light off
                 (255, 51, 0),   # k1000
                 (255, 137, 18),  # k2000
                 (255, 180, 107),  # k3000
                 (255, 209, 163),  # k4000  阅读
                 (255, 247, 245)]  # 6300k 办公
    for i in range(0, strip.numPixels()):
        strip.setPixelColor(i, Color(mode_list[mode][0], mode_list[mode][1], mode_list[mode][2]))
    strip.show()

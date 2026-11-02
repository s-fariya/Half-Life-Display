import time
import board
import displayio
import terminalio
import rotaryio
import digitalio
import i2cdisplaybus
import adafruit_displayio_ssd1306
from adafruit_display_text import label
from adafruit_bme280 import basic as adafruit_bme280

displayio.release_displays()

# I2C: D4 = SDA, D5 = SCL on the XIAO RP2040
i2c = board.I2C()

# OLED at address 0x3C
bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(bus, width=128, height=64)

# BME280 is usually at 0x76, sometimes 0x77
try:
    bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
except ValueError:
    bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x77)

# Encoder turns change the page, pressing it resets min/max
encoder = rotaryio.IncrementalEncoder(board.D0, board.D1)
button = digitalio.DigitalInOut(board.D2)
button.switch_to_input(pull=digitalio.Pull.UP)

# Three lines of text on screen
screen = displayio.Group()
display.root_group = screen
lines = []
for i in range(4):
    t = label.Label(terminalio.FONT, text="", x=0, y=6 + i * 16)
    screen.append(t)
    lines.append(t)

temp_min = temp_max = bme.temperature
hum_min = hum_max = bme.relative_humidity

while True:
    temp = bme.temperature
    hum = bme.relative_humidity
    pres = bme.pressure

    temp_min = min(temp_min, temp)
    temp_max = max(temp_max, temp)
    hum_min = min(hum_min, hum)
    hum_max = max(hum_max, hum)

    if not button.value:  # pressed = reset min/max
        temp_min = temp_max = temp
        hum_min = hum_max = hum

    page = (encoder.position // 2) % 2  # change the 2 if it skips

    if page == 0:
        lines[0].text = "LIVE"
        lines[1].text = f"Temp: {temp:.1f} C"
        lines[2].text = f"Hum:  {hum:.0f} %"
        lines[3].text = f"Pres: {pres:.0f} hPa"
    else:
        lines[0].text = "MIN / MAX"
        lines[1].text = f"T: {temp_min:.1f} / {temp_max:.1f}"
        lines[2].text = f"H: {hum_min:.0f} / {hum_max:.0f}"
        lines[3].text = "press = reset"

    time.sleep(0.2)

# its 0300 damn straight this shii is vibe coded
import board
import busio
import displayio
import digitalio
import terminalio
import wifi
import time
from adafruit_st7735r import ST7735R
from adafruit_display_text import label

displayio.release_displays()

# === Pins ===
spi = busio.SPI(clock=board.IO5, MOSI=board.IO10)
tft_cs = board.IO6
tft_dc = board.IO8
tft_reset = board.IO7

tft_led = digitalio.DigitalInOut(board.IO4)
tft_led.switch_to_output()
tft_led.value = True  # Backlight ON

# === Display ===
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset)
display = ST7735R(display_bus, width=160, height=128, bgr=True, rotation=270)

# === Groups ===
main_group = displayio.Group()
display.root_group = main_group

# === Background ===
bg_bitmap = displayio.Bitmap(160, 128, 1)
bg_palette = displayio.Palette(1)
bg_palette[0] = 0x000000
bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, x=0, y=0)
main_group.append(bg_sprite)

# === Channel Bars ===
bars_group = displayio.Group()
main_group.append(bars_group)

# === Channel Labels ===
labels_group = displayio.Group()
main_group.append(labels_group)

# X position per channel
channel_x = []
for ch in range(1, 14):
    x = 5 + (ch - 1) * 11
    channel_x.append(x)
    l = label.Label(terminalio.FONT, text=str(ch), color=0xFFFFFF, x=x, y=115)
    labels_group.append(l)

# Max bar height for busiest channel
max_height = 80
min_height = 2  # Minimum bar height, even for zero

def draw_bars(channels):
    while len(bars_group) > 0:
        bars_group.pop()

    max_count = max(channels[1:]) if max(channels[1:]) > 0 else 1

    for ch in range(1, 14):
        count = channels[ch]
        height = int((count / max_count) * max_height)
        if height < min_height:
            height = min_height

        bar_bitmap = displayio.Bitmap(8, height, 1)
        bar_palette = displayio.Palette(1)
        bar_palette[0] = 0xFFFFFF  # White
        bar = displayio.TileGrid(bar_bitmap, pixel_shader=bar_palette, x=channel_x[ch - 1], y=110 - height)
        bars_group.append(bar)

# === Main Loop ===
while True:
    print("Scanning Wi-Fi...")
    channels = [0] * 14
    found = wifi.radio.start_scanning_networks()
    for n in found:
        if 1 <= n.channel <= 13:
            channels[n.channel] += 1
    wifi.radio.stop_scanning_networks()

    print("Channels:", channels[1:])
    draw_bars(channels)

    time.sleep(3)


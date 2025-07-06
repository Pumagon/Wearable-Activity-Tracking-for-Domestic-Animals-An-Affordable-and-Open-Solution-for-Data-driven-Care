import sys, time, board, displayio, busio
import fourwire, terminalio, digitalio

from adafruit_st7789 import ST7789
from adafruit_display_text import label

def main():
    myText = "Hello World!"
    fontColor = 0xFFFFFF
    bgColor = 0x0000A0

    display = initDisplay(bgColor)
    showText(myText, fontColor, bgColor, display)

    return 0
    

def initDisplay(bgColor):
    displayio.release_displays()
    
    spi = busio.SPI(board.LCD_CLK, board.LCD_MOSI)
    display_bus = fourwire.FourWire(
        spi, command=board.LCD_DC, chip_select=board.LCD_CS, reset=board.LCD_RST
    )
    
    display = ST7789(
        display_bus,
        width=240,
        height=135,
        rowstart=40,
        colstart=52,
        rotation=90
    )
    
    color_bitmap = displayio.Bitmap(240, 135, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = bgColor
    
    bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
    
    main_group = displayio.Group()
    main_group.append(bg_sprite)
    
    display.root_group = main_group
    
    print("Dispaly Initialized")

    return display


def showText(myText, fontColor, bgColor, display):
    color_bitmap = displayio.Bitmap(240, 135, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = bgColor
    
    bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
    
    text_area = label.Label(
        terminalio.FONT,
        text=myText,
        #color=0xFFFFFF,
        color=fontColor,
        scale=2,
        x=10,
        y=30
    )
    
    # Adjusting the text to the center
    text_area.anchor_point = (0.5, 0.5)
    text_area.anchored_position = (display.width // 2, display.height // 2) 

    splash = displayio.Group()
    splash.append(bg_sprite)
    splash.append(text_area)
    display.root_group = splash

    return 0

def turnOff():
    displayio.release_displays()

    # M5StickC PLUS2 LCD display pin setting
    lcd_bl = board.LCD_BL     # Back Light
    
    backlight = digitalio.DigitalInOut(lcd_bl)
    backlight.direction = digitalio.Direction.OUTPUT
    backlight.value = False

    print("LCD turned off")


def boot(myText, fontColor, bgColor, display):
    showText(myText, fontColor, bgColor, display)
    time.sleep(1)
    turnOff()


if __name__ == '__main__':
    sys.exit(main())





import os
import board
import displayio
import time
from adafruit_bitmap_font import bitmap_font
from adafruit_button import Button
import adafruit_touchscreen
import busio
import digitalio
import storage
import adafruit_sdcard
import supervisor
import json
# See if a card is present
card_detect_pin = digitalio.DigitalInOut(board.SD_CARD_DETECT)
card_detect_pin.direction = digitalio.Direction.INPUT
card_detect_pin.pull = digitalio.Pull.UP
print('SD card present: %s' % card_detect_pin.value)

# Try to connect to the SD card
sdcard = adafruit_sdcard.SDCard(
    busio.SPI(board.SCK, board.MOSI, board.MISO),
    digitalio.DigitalInOut(board.SD_CS)
)

# Mount the card to a directory
virtual_file_system = storage.VfsFat(sdcard)
storage.mount(virtual_file_system, '/sd')
a = {"a":1, "b":2}
f = open('/sd/test.yaml', 'w')
json.dump(a, f)
f.close()

def save_settings(values):
    with open('/sd/DAC.txt','w') as output_file:
        for i in range(8):
            output_file.write('%f\n'%values[i])

try:
    with open('/sd/DAC.txt', 'r') as input_file:
        values = []
        for i in range(8):
            values.append(float(input_file.readline()))
except Exception as e:
    print(e)
    # assume because file doesn't exist
    values = [0, 0, 0, 0, 0, 0, 0, 0]
    save_settings(values)

print('values',values)

# These pins are used as both analog and digital! XL, XR and YU must be analog
# and digital capable. YD just need to be digital
ts = adafruit_touchscreen.Touchscreen(board.TOUCH_XL, board.TOUCH_XR,
                                      board.TOUCH_YD, board.TOUCH_YU,
                                      calibration=((5200, 59000), (5800, 57000)),
                                      z_threshhold = 25000,
                                      samples = 1,
                                      size=(480, 320))

# the current working directory (where this file is)
cwd = ("/"+__file__).rsplit('/', 1)[0]
fonts = [file for file in os.listdir(cwd+"/fonts/")
         if (file.endswith(".bdf") and not file.startswith("._"))]
for i, filename in enumerate(fonts):
    fonts[i] = cwd+"/fonts/"+filename
print(fonts)
# THE_FONT = "/fonts/Arial-12.bdf"
# THE_FONT = "/fonts/Helvetica-bold-16.bdf"
# THE_FONT = "/fonts/Arial-ItalicMT-23.bdf"
THE_FONT = "/fonts/Ubuntu-Medium-24.bdf"
DISPLAY_STRING = "Button Text"

# Make the display context
splash = displayio.Group(max_size=20)
board.DISPLAY.show(splash)
BUTTON_WIDTH = 140
BUTTON_HEIGHT = 60
BUTTON_MARGIN = 15

##########################################################################
# Make a background color fill

color_bitmap = displayio.Bitmap(480, 320, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x404040
bg_sprite = displayio.TileGrid(color_bitmap,
                               pixel_shader=color_palette,
                               x=0, y=0)
print(bg_sprite.x, bg_sprite.y)
splash.append(bg_sprite)

##########################################################################

# Load the font
font = bitmap_font.load_font(THE_FONT)

buttons = []

for i in range(8):
    button = Button(x=BUTTON_MARGIN*(i//4+1)+BUTTON_WIDTH*(i//4),
                    y=BUTTON_MARGIN*(i%4+1)+BUTTON_HEIGHT*(i%4),
                      width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                    label_color = 0x00FF00, selected_label = 0x00FF00,
                      label="%f"%values[i], label_font=font, style=Button.SHADOWROUNDRECT)
    buttons.append(button)
button = Button(x=BUTTON_MARGIN*(3)+BUTTON_WIDTH*(2),
                y=BUTTON_MARGIN*(1)+BUTTON_HEIGHT*(0),
                  width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                  label="<<<", label_font=font, style=Button.SHADOWROUNDRECT)
buttons.append(button)
button = Button(x=BUTTON_MARGIN*(3)+BUTTON_WIDTH*(2),
                y=BUTTON_MARGIN*(2)+BUTTON_HEIGHT*(1),
                  width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                  label="+", label_font=font, style=Button.SHADOWROUNDRECT)
buttons.append(button)
button = Button(x=BUTTON_MARGIN*(3)+BUTTON_WIDTH*(2),
                y=BUTTON_MARGIN*(3)+BUTTON_HEIGHT*(2),
                  width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                  label="-", label_font=font, style=Button.SHADOWROUNDRECT)
buttons.append(button)
button = Button(x=BUTTON_MARGIN*(3)+BUTTON_WIDTH*(2),
                y=BUTTON_MARGIN*(4)+BUTTON_HEIGHT*(3),
                  width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                  label=">>>", label_font=font, style=Button.SHADOWROUNDRECT)
buttons.append(button)


for b in buttons:
    splash.append(b.group)

def set_dac(index, value):
    # print('set_dac')
    # update hardware

    # update display
    values[index] = value
    buttons[index].label = '%8.6f' % value

last_selected = -1
last_op = -1
last_op_time = 0
step = 0.001
while True:
    if supervisor.runtime.serial_bytes_available:
        msg = input()
        msg = msg.strip()
        msg = msg.split()
        if len(msg)<=2 and len(msg)>0:
            command = msg[0]
            if len(msg)==1:
                if command.endswith('?'):
                    #  Need to really check if integer
                    index = int(command[:-1])
                    #  Check if index is in range
                    print('%d %f' % (index, values[index]))
                if command.upper() == 'S':
                    save_settings(values);
                    print('saved values');
            else:  # len(msg)==2
                index = int(command[:-1])
                new_value = float(msg[1])
                set_dac(index, new_value)

    p = ts.touch_point
    if p:
        print(p)
        for i, b in enumerate(buttons):
            if b.contains(p):
                # print("Button %d pressed" % i)
                if i<8 :
                    b.selected = True
                    if (last_selected >= 0) and (i != last_selected):
                        buttons[last_selected].selected = False
                    last_selected = i
                else:
                    b.selected = True
                    if (last_op >= 0) and (last_op != i):
                        buttons[last_op].selected = False
                    last_op = i
                    now = time.time()
                    #  Do operation
                    if i==8:
                        step = step * 10
                        if step>0.1:
                            step = 0.1
                    elif i==11:
                        step = step / 10
                        if step<0.0001:
                            step = 0.0001
                    elif i==9:
                        if last_selected>=0:
                            values[last_selected] += step
                            values[last_selected] = round(values[last_selected],6)

                            set_dac(last_selected, values[last_selected])
                    elif i==10:
                        if last_selected>=0:
                            values[last_selected] -= step
                            values[last_selected] = round(values[last_selected],6)
                            set_dac(last_selected, values[last_selected])
                    last_op_time = now

    else:
        now = time.time()
        # print('last_op: %d'%last_op)
        if (now-last_op_time) > 0.001:
            buttons[last_op].selected = False

            # else:
            #     print('no button')
            #     for i in range(8,12):
            #         buttons[i].selected = False
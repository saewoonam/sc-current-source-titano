import os
import board
import time
import busio
import digitalio
import storage
import supervisor
import adafruit_mcp4728
import AD5675
from default_values import default_values

def mcp4728_set(dac_value, index):
    dac_value = int(abs(dac_value) / 3.3 * 65535)
    if index==0:
        mcp4728.channel_a.value = dac_value
    elif index==1:
        mcp4728.channel_b.value = dac_value
    elif index==2:
        mcp4728.channel_c.value = dac_value
    elif index==3:
        mcp4728.channel_d.value = dac_value

class fake:
    def __init__(self):
        return
    def set(self, dac_value, index):
        return

try:
    i2c = busio.I2C(board.SCL, board.SDA)
    i2c.try_lock()
    addresses = i2c.scan()
    i2c.unlock()
except Exception as e:
    print("problem with i2c", e)
    addresses = []
print(addresses)
if 96 in addresses:
    dac = adafruit_mcp4728.MCP4728(i2c)
    dac.set = mcp4728_set
elif 12 in addresses:
    dac = AD5675.AD5675(i2c, offset=1.25)
else:
    dac = fake();

_SETTINGS_FILENAME = '/DAC.json'
def to_json(array):
    json_string = '%s' % array
    json_string = json_string.replace("'", '"').replace('False', 'false').replace('True','true')
    return json_string
def from_json(string_in):
    return eval(string_in.replace('false', 'False').replace('true', 'True'))

def save_settings_json(values):
    with open(_SETTINGS_FILENAME,'w') as output_file:
        json.dump(values, output_file)

def read_settings_json():
    with open(_SETTINGS_FILENAME,'r') as input_file:
        raw = input_file.read(1000);
    values = from_json(raw)
    print('found these', values)
    return values
try:
    values = read_settings_json()
except Exception as e:
    print(e)
    # values = default_values
    # save_settings_json(values)

def set_dac(index, value):
    if type(value)==int:
        values[index][1] = value
        value = values[index]
    else:
        values[index] = value
    # print('set_dac', value)
    # update hardware
    # check if not 'zeroed'
    if values[index][2]:
        print("bias device", index, value)
        dac_value = (values[index][1] / 100)
    else:
        print('zero device', index, value)
        dac_value = 0 # or midscale...
    dac.set(dac_value, index)
    # update display

def check_int(s):
    s = str(s)
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()

last_selected = -1
last_op = -1
last_op_time = 0
step = 0.001
while True:
    if supervisor.runtime.serial_bytes_available:
        msg = input()
        msg = msg.split(' ', 1);
        if len(msg)==1:
            command = msg[0]
            args = ""
        else:
            [command, args] = msg
        if len(args)==0:
            if command.endswith('?'):
                #  Need to really check if integer
                index = int(command[:-1])
                #  Check if index is in range
                print(index, to_json(values[index]))
            if command.upper()=='S':
                save_settings(values)
            if command.upper()=='J':
                save_settings_json(values)
            if command.upper()=='Z':
                # set all values to zero
                # print("set all to zero")
                for i in range(len(values)):
                    values[i][2] = False
                    set_dac(i, values[i])
            if command.upper()=='R':
                # bias all 
                for i in range(len(values)):
                    values[i][2] = True
                    set_dac(i, values[i]);

        else:  # len(msg)==2
            print('command', command, 'args', args)
            if check_int(command):
                index = int(command)
                # new_value = float(args)
                new_value = from_json(args)
                # print('new_value', new_value)
                set_dac(index, new_value)
            else:
                print("command", command[:-1], args)

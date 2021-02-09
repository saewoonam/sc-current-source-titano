import os
import board
import time
import busio
import digitalio
import storage
import supervisor
import AD5675
import TCA9534A
from default_values import default_values
import set_readonly

_READONLY = True

try:
    i2c = busio.I2C(board.SCL, board.SDA)
    i2c.try_lock()
    addresses = i2c.scan()
    i2c.unlock()
except Exception as e:
    print("problem with i2c", e)
    addresses = []

if 12 in addresses:
    dac = AD5675.AD5675(i2c, offset=1.25)
else:
    dac = AD5675.AD5675(None, offset=1.25);

if 56 in addresses:
    switch = TCA9534A.TCA9534(i2c, 56)
else:
    switch = TCA9534A.TCA9534(None, 56)

_SETTINGS_FILENAME = '/DAC.json'
def to_json(array):
    json_string = '%s' % array
    json_string = json_string.replace("'", '"').replace('False', 'false').replace('True','true')
    return json_string
def from_json(string_in):
    return eval(string_in.replace('false', 'False').replace('true', 'True'))

def save_settings_json(values):
    if not _READONLY:
        with open(_SETTINGS_FILENAME,'w') as output_file:
            output_file.write(to_json(values))
            # json.dump(values, output_file)

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
    # check if value  is a dac_value
    if type(value)==str:
        dac_value = True
        value = int(value[1:])
    else:
        dac_value = False

    if len(values[index])==3:
        values[index].append(32768)
        dac_offset = 32768
    else:
        if type(values[index][3])==str:
            values[index][3] = 32768
        dac_offset = values[index][3]

    # print('set_dac', value)
    # update hardware
    # check if not 'zeroed'
    if values[index][2]:
        # print("bias device", index, value)
        dac_value = (values[index][1] / 100)
        switch.set_bit(index)
    else:
        # print('zero device', index, value)
        # dac_value = 0 # or midscale...
        switch.clear_bit(index)
    dac.set(dac_value, index, use_dac_value=False, dac_offset=dac_offset)
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
_READONLY = set_readonly.get_readonly()
board_name = set_readonly.get_name()
power_status = digitalio.DigitalInOut(board.A0)
power_status.direction = digitalio.Direction.INPUT
# print('power status', power_status.value)
print('power_status', power_status.value, 'i2c addresses',addresses)

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
                if check_int(command[:-1]):
                    index = int(command[:-1])
                    #  Should Check if index is in range
                    print(index, to_json(values[index]))
                else:
                    cmd = command[:-1].upper()
                    if cmd=='N':
                        print('board_name', board_name)
                    if cmd=='R':
                        print('READONLY', _READONLY)
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
            elif command.upper()=='N':
                board_name = args;
                if not _READONLY:
                    set_readonly.set_name(board_name)
                    # print("set name")
            else:
                print("command", command[:-1], args)

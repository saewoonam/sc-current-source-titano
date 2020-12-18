#
#
import time
import board
import busio
from struct import pack_into
from time import sleep
import adafruit_bus_device.i2c_device as i2c_device

_FULL_SCALE = 2.5

class AD5675:
    """Helper library for the Analog Devices AD5675R I2C 12-bit Octal DAC.
        :param ~busio.I2C i2c_bus: The I2C bus the AD5675R is connected to.
        :param address: The I2C slave address of the sensor
    """

    def __init__(self, i2c_bus, offset=0, address=12):
        if i2c_bus is not None:
            self.i2c_device = i2c_device.I2CDevice(i2c_bus, address)
        else:
            self.i2c_device = None
        self.offset = offset

    def _read_registers(self):
        """registers are zero on powerup... Eventhough DAC may be set to
            mid-scale.  Registers are only updated when they are written to
        """
        buf = bytearray(16)

        with self.i2c_device as i2c:
            i2c.write(bytes([0x90, 0, 0]))
            i2c.readinto(buf)

        return buf
    def set(self, value, ch=0, use_dac_value=False, dac_offset=32768):
        if use_dac_value:
            digital = value
        else:
            digital = int((value+self.offset)/_FULL_SCALE *
                          (1<<16))+dac_offset-32768
        print('AD5675 set', digital, ch)
        high = digital >> 8
        low = digital & 0xFF
        command = 0x30  # 0x10 will also work since ~LDAC is held low
        if self.i2c_device is not None:
            with self.i2c_device as i2c:
                i2c.write(bytes([command+ch, high, low]))

import time
import board
import busio
import adafruit_bus_device.i2c_device as i2c_device

class TCA9534:
    """Helper library for the TCA9534 I2C 8-bit bus expander, setup as output only for now
        :param ~busio.I2C i2c_bus: The I2C bus the TCA9534 is connected to.
        :param address: The I2C slave address of the sensor
    """

    def __init__(self, i2c_bus, address=56):
        self.out = 0
        self.i2c_bus = i2c_bus
        if i2c_bus is not None:
            self.i2c_device = i2c_device.I2CDevice(i2c_bus, address,
                                                   probe=False)
            if self.probe_for_device():
                with self.i2c_device as i2c:
                    i2c.write(bytes([1, self.out])) # set all outputs to zero
                    i2c.write(bytes([3, 0])) # set all pins as outputs
        else:
            self.i2c_device = None

    def scan(self):
        i2c = self.i2c_bus
        i2c.unlock()
        i2c.try_lock()
        print(i2c.scan())
        i2c.unlock()
    def set(self, out):
        if self.i2c_device:
            self.out = out
            with self.i2c_device as i2c:
                i2c.write(bytes([1, self.out])) 
                i2c.write(bytes([3, 0])) # set all pins as outputs

    def set_bit(self, bit):
        if self.i2c_device:
            self.out = self.out | (1<<bit)
            self.set(self.out)

    def clear_bit(self, bit):
        if self.i2c_device:
            mask = 255 ^ (1<<bit)
            self.out = self.out & mask;
            self.set(self.out)

    def probe_for_device(self):
        here = True
        try:
            self.i2c_device.__probe_for_device()
        except ValueError:
            here = False
        finally:
            return here


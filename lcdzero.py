# MAUI: Moode Audio User Interface
#
# Copyright (C) 2020-2021   Hedde van der Lugt  <hedde.van.der.lugt@gmail.com>
#
# MAUI is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MAUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with MAUI. If not, see <http://www.gnu.org/licenses/>.

# this software is using and based on
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2016-2019 Dave Jones <dave@waveform.org.uk>


from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
    )
str = type('')

from threading import RLock
from time import sleep
from gpiozero.pins.mock import MockFactory
import gpiozero
import os

from gpiozero import Device, SharedMixin
from gpiozero import OutputDevice

# a LCD class using gpiozero baseclasses and IO functions
class lcdzero(SharedMixin, Device):
    def __init__(self, width, heigth, enable_pin, rw_pin, rs_pin, d4_pin, d5_pin, d6_pin, d7_pin ):
        self.lock = None
        self.enable = None
        self.rw = None
        self.rs = None
        self.d4 = None
        self.d5 = None
        self.d6 = None
        self.d7 = None

        self.width = width
        self.heigth = heigth

        self.lcd_character = True
        self.lcd_command = False
        self.lcd_line = [0x80, 0xC0] # LCD RAM address for the 1st & 2nd line
        # Timing constants
        self.enable_pulse = 0.0005
        self.enable_delay = 0.0005

        self.verbose = False

        super(lcdzero, self).__init__()
        self.lock = RLock()
        try:
            self.enable = OutputDevice(enable_pin )
            if rw_pin is not None:
                self.rw = OutputDevice(rw_pin)
            if rs_pin is not None:
                self.rs = OutputDevice(rs_pin)
            if d4_pin is not None:
                self.d4 = OutputDevice(d4_pin)
            if d5_pin is not None:
                self.d5 = OutputDevice(d5_pin)
            if d6_pin is not None:
                self.d6 = OutputDevice(d6_pin)
            if d7_pin is not None:
                self.d7 = OutputDevice(d7_pin)
        except:
            self.close()
            raise

        self.lcd_init()

    def close(self):
        super(lcdzero, self).close()
        if getattr(self, 'lock', None):
            with self.lock:
                if self.enable is not None:
                    self.enable.close()
                    self.enable = None
                if self.rw is not None:
                    self.rw.close()
                    self.rw = None
                if self.rs is not None:
                    self.rs.close()
                    self.rs = None
                if self.d4 is not None:
                    self.d4.close()
                    self.d4 = None
                if self.d5 is not None:
                    self.d5.close()
                    self.d5 = None
                if self.d6 is not None:
                    self.d6.close()
                    self.d6 = None
                if self.d7 is not None:
                    self.d7.close()
                    self.d7 = None
        self.lock = None

    @property
    def closed(self):
        return self.lock is None

    @classmethod
    def _shared_key(cls, width, height, enable_pin, rw_pin, rs_pin, d4_pin, d5_pin, d6_pin, d7_pin):
        return (width, height, enable_pin, rw_pin, rs_pin, d4_pin, d5_pin, d6_pin, d7_pin)

    def lcd_init( self ):
        # Initialise display
        self.rw.value = False                # low RW port to write to display
        self.lcd_byte(0x33,self.lcd_command) # 110011 Initialise
        self.lcd_byte(0x32,self.lcd_command) # 110010 Initialise
        self.lcd_byte(0x06,self.lcd_command) # 000110 Cursor move direction
        self.lcd_byte(0x0C,self.lcd_command) # 001100 Display On,Cursor Off, Blink Off
        self.lcd_byte(0x28,self.lcd_command) # 101000 Data length, number of lines, font size
        self.lcd_byte(0x01,self.lcd_command) # 000001 Clear display
        sleep(self.enable_delay)

    def lcd_byte(self, bits, mode):
        # Send byte to data pins
        # bits = data
        # mode = True  for character
        #        False for command

        self.rs.value = mode
        
        # High bits
        self.d4.value = bool( bits & 0x10 )
        self.d5.value = bool( bits & 0x20 )
        self.d6.value = bool( bits & 0x40 )
        self.d7.value = bool( bits & 0x80 )
        
        # Toggle 'Enable' pin
        self.lcd_toggle_enable()

        # Low bits
        self.d4.value = bool( bits & 0x01 )
        self.d5.value = bool( bits & 0x02 )
        self.d6.value = bool( bits & 0x04 )
        self.d7.value = bool( bits & 0x08 )

        # Toggle 'Enable' pin
        self.lcd_toggle_enable()

    def lcd_toggle_enable( self ):
        # Toggle enable
        sleep(self.enable_delay)
        self.enable.value = True
        sleep(self.enable_pulse)
        self.enable.value = False
        sleep(self.enable_delay)

    def display(self, message, row):
        # Send string to display
        if not message:
            message = "empty"
        message = message.center(self.width," ")
        
        self.lcd_byte(self.lcd_line[row], self.lcd_command)

        for i in range(self.width):
            self.lcd_byte(ord(message[i]),self.lcd_character)

# if used from commandline, show message
if __name__ == "__main__":
    print("this software is part of maui, to test the lcd display ¨please use maui.py --test lcd")
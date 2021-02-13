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


import gpiozero
from gpiozero.pins.mock import MockFactory
import re
from time import sleep
import signal

# add was_held to button object
gpiozero.Button.was_held = False

# buttons base class, please inherit from this class and implement the perform method
class BUTTONS:
    def __init__( self, button_setup ):
        self.buttons_enabled = False
        self.buttons = {}

        self.verbose = False

        # compiled regular expression to extract GPIO numbers from ini file
        c_regex = re.compile( "GPIO([0-9]{1,2})(HOLD|RELEASE){0,1}" )

        remember = set()
        for gpio,function in button_setup.items():
            print( gpio, function )
            gpio_r = c_regex.search( gpio.upper() )
            if gpio_r:
                # format GPIO
                GPIO = "GPIO"+str( int(gpio_r.group(1) ))
                if not GPIO in remember:        # configure GPIO port as button, add handling
                    if self.verbose:
                        print("add ", GPIO, " function", function.lower() )
                    remember.add( GPIO )        # remember used GPIO ports
                    button = gpiozero.Button( GPIO, pull_up=True, bounce_time=None )
                    button.when_released = self.button_released
                    button.when_held = self.button_held

                # add HOLD or RELEASE to GPIO
                if gpio_r.group(2):
                    GPIO = GPIO + gpio_r.group(2)
                self.buttons[GPIO] = function.lower()
        print( self.buttons )

    # called when button is released but not held
    # this is not a callback routine itself, it is called from button_released callback in case the button is not hold
    def button_pressed( self, button ):
        if self.verbose:
            print("button pressed: io", button.pin )
        if str(button.pin) in self.buttons:
            action = self.buttons[str(button.pin)]
            self.perform( action, str( button.pin) )

    # called when a button is released
    # this is the callback function for ALL gpiozero.button release callback´s
    def button_released( self, button ):
        if self.verbose:
            print("button released: io", button.pin )
        sleep( 0.2 )
        if not button.was_held:
            self.button_pressed( button )
        button.was_held = False
        strButton = str( button.pin ) + "RELEASED"
        if strButton in self.buttons:
            action = self.buttons[strButton]
            self.perform( action, strButton )

    # called when a button is hold
    # this is the callback function for ALL gpiozero.button held callback´s
    def button_held( self, button ):
        button.was_held = True
        if self.verbose:
            print("button hold: io", button.pin )
        sleep( 0.2 )
        strButton = str( button.pin ) + "HOLD"
        if strButton in self.buttons:
            action = self.buttons[strButton]
            self.perform( action, strButton )

    def perform( self, action, button ):
            print("button: ", button, "  pressed,  action:", action )


# if used from commandline, show message
if __name__ == "__main__":
    print("this software is part of maui, to test the buttons ¨please use maui.py --test buttons")
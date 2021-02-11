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


import configparser
import sys
import os
import argparse
import re
from datetime import datetime
import time

import gpiozero
from gpiozero.pins.mock import MockFactory

import signal
from mpd import MPDClient

import socket                           # to get ip address

# private modules
from buttons import BUTTONS
from lcdzero import lcdzero
from mpdi import MPDi

cout_title = "MAUI - MPD Audio User Interface"
cout_test = "started in test mode"
cout_exit_ctrlbreak = "press ctrl-c to end"

cout_button_test = 'press any button, triggered GPIO and configured action is shown on console'
cout_lcd_test = 'LCD test is performed, LCD should display testdata'

def getipaddress():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = str( s.getsockname()[0] )
    s.close()
    return ip

class OS:
    def __init__( self ):
        self.verbose = False

    def shutdown( self ):
        if self.verbose:
            print("os shutdown")
        os.system("sudo shutdown -h now")
        sys.exit()

    def reboot( self ):
        if self.verbose:
            print("os reboot")
        os.system("sudo reboot")
        sys.exit()

    def poweroff( self ):
        if self.verbose:
            print("os poweroff")
        os.system("sudo poweroff")
        sys.exit()


class MAUI( BUTTONS ):
    def __init__( self ):
        self.kill_now = False
        self.lcd = None
        self.mpd = None

        self.os = OS()
        self.mode = 'run'

        self.buttons_enabled = False

        self.config = configparser.ConfigParser()

        self.infoset = 1
        self.infodata = dict()
        self.infolines = ['', '', '', '']

        self.verbose = False

        self.button_dict = dict()
        self.parse_arguments()
        self.os.verbose = self.verbose

        self.read_config()

        super().__init__( self.button_dict )
        #super().verbose = self.verbose

        signal.signal(signal.SIGINT, self.kill)
        signal.signal(signal.SIGTERM, self.kill)

    def parse_arguments( self ):
        parser = argparse.ArgumentParser(description=cout_title)
        parser.add_argument('--verbose', action='store_true', help='show trace output for debugging/testing purposes')
        parser.add_argument('--test', choices=['lcd', 'mpd', 'buttons'], help='test invidual component')

        args = parser.parse_args()
        self.verbose = args.verbose
        if args.test:
            self.mode = args.test

    def read_config(self):
        self.config.read("maui.ini")
        if self.verbose:
            print("configuration")
            print(self.config)

        self.welcome = self.config["DEFAULT"]["WELCOME"]

        # compiled regular expression to extract GPIO numbers from ini file
        c_regex = re.compile( "GPIO([0-9]{1,2})(HOLD|RELEASE){0,1}" )

        self.display = self.config["DEFAULT"]["DISPLAY"]
        if self.display == "LCD":
            self.lcd = lcdzero( int(self.config[self.display]["WIDTH"]), int(self.config[self.display]["HEIGHT"]),
                            self.config[self.display]["E"], self.config[self.display]["RW"], self.config[self.display]["RS"],
                            self.config[self.display]["D4"], self.config[self.display]["D5"],
                            self.config[self.display]["D6"], self.config[self.display]["D7"] )
            self.lcd.verbose = self.verbose
        else:
            self.lcd = None

        self.musicinfo = self.config["DEFAULT"]["MUSICINFO"]
        if self.musicinfo:
            self.mpd = MPDi( self.config[self.musicinfo]["HOST"], self.config[self.musicinfo]["PORT"] )
            self.mpd.verbose = self.verbose

        self.buttons_enabled = self.config["DEFAULT"]["BUTTONS"]
        if self.buttons_enabled:

            for gpio,function in self.config["BUTTONS"].items():
                gpio_r = c_regex.search( gpio.upper() )
                if gpio_r:
                    # format GPIO
                    GPIO = "GPIO"+str( int(gpio_r.group(1)) )
                    if gpio_r.group(2):
                        GPIO = GPIO + gpio_r.group(2)
                    self.button_dict[GPIO] = function.lower()
            if self.verbose:
                print( self.button_dict )

    def kill(self,signum, frame):
        self.kill_now = True

    def perform( self, action, button ):
        if maui.mode=='run':
            if action:
                if self.verbose:
                    print("button: ", button, "  pressed,  action:", action )
                if action=="pause":
                    self.mpd.pause()
                elif action=="toggleplaystop":
                    self.mpd.toggleplaystop()
                elif action=="next":
                    self.mpd.next()
                elif action=="previous":
                    self.mpd.previous()
                elif action=="shutdown":
                    self.lcd.display( self.welcome, 0 )
                    self.lcd.display( action, 1 )
                    self.os.shutdown()
                elif action=="reboot":
                    self.lcd.display( self.welcome, 0 )
                    self.lcd.display( action, 1 )
                    self.os.reboot()
                elif action=="poweroff":
                    self.lcd.display( self.welcome, 0 )
                    self.lcd.display( action, 1 )
                    self.os.poweroff()
                elif action=="info":
                    self.nextinfo()
                elif action=="print":
                    print( button )
                else:
                    print("ERROR: unknown command:", action)
            else:
                print("ERROR: empty command received")
        else:
            print("button: ", button, " ,configured action is: ", action )

    # skips info sets
    def nextinfo( self ):
        self.infoset = self.infoset + 1
        if self.infoset > 2:
            self.infoset = 1
        self.info()

    # shows information on display
    def info( self ):
        lines = ['', '']

        if self.infoset == 1:
            if self.mpd.connected():
                state = self.infodata.get( 'state' )
                if state=='play':
                    lines[0] = self.infodata["artist"]
                    lines[1] = self.infodata["title"]
                else:
                    lines[0] = self.welcome
                    lines[1] = state
            else:
                lines[0] = self.welcome
                lines[1] = "searching MPD"

        if self.infoset == 2:
            lines[0] = self.welcome

            strIP = getipaddress()
            #strCPUtemp = str( int(gpiozero.CPUTemperature().temperature) )
            #strDateTime = datetime.now().strftime(r'%Y-%m-%d %H:%M')
            lines[1] = strIP

        for i in range(2):
            if self.infolines[i] != lines[i]:
                print( lines[i] )
                self.infolines[i] = lines[i]
                self.lcd.display( self.infolines[i], i )

    def task( self ):
        if not self.mpd.connected():
            time.sleep( 0.5 )
            self.mpd.connect()

        if self.mpd.connected():
            self.infodata = self.mpd.getdata()

        self.info()

        time.sleep(0.5)

    def close( self ):
        self.mpd.disconnect()


maui = MAUI()

if maui.mode=='run':
    while maui.kill_now == False:
        maui.task()

    maui.close()

    maui.lcd.display( maui.welcome, 0 )
    maui.lcd.display( "standby",1 )
elif maui.mode=='lcd':
    print(cout_title)
    print(cout_test)
    print(cout_lcd_test)
    print(cout_exit_ctrlbreak)

    while True:
        maui.lcd.display( "performing tests", 0)
        maui.lcd.display( "0123456789ABCDEF", 1)

        time.sleep( 1 )

        maui.lcd.display( "performing tests", 1)
        maui.lcd.display( "0123456789ABCDEF", 0)

        time.sleep( 1 )

    maui.lcd.display( maui.welcome, 0)
    maui.lcd.display( "endof lcd test", 1 )

elif maui.mode=='mpd':

    # connect to MPD
    print("connecting to Music Play Daemon (MPD)")
    print("host: ", maui.mpd.host, "    port: ", maui.mpd.port )

    maui.mpd.connect()
    if maui.mpd.connected():

        data = maui.mpd.getdata()
        print( data )
        if not data:
            print("no data could be retreived from MPD")
        else:
            print("data rereived from MPD")
            if 'state' in data:
                print("state:", data['state'])
            if 'artist' in data:
                print("artist:", data['artist'])
            if 'title' in data:
                print("title:", data['title'])

        print("send mpd play command")
        maui.mpd.play()

        data = maui.mpd.getdata()
        if data:
            if 'state' in data:   
                print("state:", data['state'])
            if 'artist' in data:
                print("artist:", data['artist'])
            if 'title' in data:
                print("title:", data['title'])

        print("wait for 6 seconds")
        time.sleep(6)

        print("send mpd stop command")
        maui.mpd.stop()
        time.sleep(1)

        print("disconnect from mpd")
        maui.mpd.disconnect()

        print("end of mpd test")
    else:
        print("could not connect to Music Player Daemon, is it running?")
        print("Check: sudo systemctl status mpd")

elif maui.mode=='buttons':
    print(cout_title)
    print(cout_test)
    print(cout_button_test)
    print(cout_exit_ctrlbreak)
    signal.pause()

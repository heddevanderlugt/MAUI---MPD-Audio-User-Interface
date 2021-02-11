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

import time
import signal
from mpd import MPDClient, MPDError, CommandError

class MPDi:
    def __init__( self, host, port ):
        
        self.verbose = True
        self.host = host
        self.port = port
        self.data = dict()
        self.client = MPDClient()               # create client object
        self.client.timeout = 1               # network timeout in seconds (floats allowed), default: None

        self.client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
        self.isconnected = False

    def connect(self ):
        if self.verbose:
            print("mpdata connect")

        try:
            self.client.connect( str(self.host), str(self.port) )
            self.isconnected = True
        except (MPDError, IOError):
            self.isconnected = False

        return self.isconnected            

    def disconnect(self):
        if self.verbose:
            print("mpdata disconnect")

        self.isconnected = False
        self.clearerror()

        return self.isconnected

    def connected(self):
        return self.isconnected

    def clearerror(self ):
        self.isconnected = False
        # Try to tell MPD we're closing the connection first
        try:
            self.client.close()
        # If that fails, don't worry, just ignore it and disconnect
        except (MPDError, IOError):
            if self.verbose:
                print("MPD clearerror: error closing connection")
        try:
            self.client.disconnect()
        # Disconnecting failed, so use a new client object instead
        # This should never happen.  If it does, something is seriously broken,
        # and the client object shouldn't be trusted to be re-used.
        except (MPDError, IOError):
            if self.verbose:
                print("MPD clearerror: error disconnect, create new MPD client object")
            self.client = MPDClient()
        if self.verbose:
            print("leaving MPD clearerror")

    def idle( self ):
        if self.isconnected:
            try:
                self.client.idle()
            except (MPDError, IOError):
                self.clearerror()

    def getdata( self ):
        if self.isconnected:
            try:
                self.data = self.client.currentsong()
                self.data.update( self.client.status() )

                if self.data.get('pos'):
                    nextsong = self.client.playlistinfo( int(self.data['pos'])+1 )
                    if nextsong:
                        self.data["nexttitle"] = nextsong[0]["title"]
            except (MPDError, IOError):
                self.clearerror()

        return self.data

    def play( self ):
        if self.isconnected:
            try:
                self.client.play()
            except (MPDError, IOError):
                self.clearerror()

    def stop( self ):
        if self.isconnected:
            try:
                self.client.stop()
            except (MPDError, IOError):
                self.clearerror()
           

    def toggleplaystop( self ):
        if self.isconnected:
            try:
                if self.data["state"]=='play':
                    self.stop()
                else:
                    self.play()
            except (MPDError, IOError):
                self.clearerror()

    def pause( self ):
        if self.isconnected:
            try:
                self.client.pause()
            except (MPDError, IOError):
                self.clearerror()

    def next( self ):
        if self.isconnected:
            try:
                self.client.next()
            except (MPDError, IOError):
                self.clearerror()

    def previous( self ):
        if self.isconnected:
            try:
                self.client.previous()
            except (MPDError, IOError):
                self.clearerror()

    def idle( self ):
        if self.isconnected:
            try:
                self.client.idle()
            except (MPDError, IOError):
                self.clearerror()


# if used from commandline, show message
if __name__ == "__main__":
    print("this software is part of maui, to test the MPD connection ¨please use maui.py --test mpd")
# MAUI - MPD Audio User Interface
This module let you use any MPD based audio player using your own hardware buttons and/or LCD screen. Developed to reuse the buttons and lcd from my audioset to control a Raspberry PI audio setup. I choose Moode Audio but should work with any MPD based audio setup i.e XBMC/Kodi.

Picture below shows my audio setup, top device is a modified tuner which internals are replaced by a Raspberry PI 3B running Moode Audio.

![cambridge audio setup](pics/frontview.jpeg)

It is developed for my own usage. Tested only on my own setup.

## Build your own audio setup
1. Buy a second hand audio component that fits your setup
1. Remove the internals, but keep
	* Display
	* Buttons
	* External connectors
	* Power supply
1. Add Raspberry
1. Add audi DAC (optional, but recommended)
1. Attach buttons to Raspberry PI
1. Attach display to Raspberry PI

* All python code
* Easy configurable using ini file


## Wakeup GPIO3 (PIN5)
GPIO3 is a special IO pin on the Raspberry PI. If the Raspberry PI is shut down by the shutdown command. Connecting this IO to ground wakes up the Raspberry PI. (When the Raspberry PI is power off, you must disconnect power supply and reconnect)

## Single shutdown button
I wanted a single momentary push button to switch on/off the Raspberry Pi. Switch on (wakeup) can be done by pulling GPIO3 to ground. 
GPIO3 is also used by the HifiBerry and other DAC´s so it can´t be used as a shutdown button (its reserved by the DAC).
The best solution for me was this brilliant solution on [stackexchange](https://raspberrypi.stackexchange.com/questions/47832/shutdown-button-for-raspberry-pi-with-hifiberry-amp-hat)
The same physical button is wired to two GPIO´s, GPIO3 for wakeup, and a arbitrary other GPIO to attach the shutdown function to.

## On/Off led
The physical enclosure I used had a led to show if the device is turned on. I connected the Led (using a resistor to limit the current) to GPIO14 (TXD)
To enable this function the following line needs to be added to /boot/config.txt
`enable_uart=1`
The full description can be found on [howchoo](https://howchoo.com/g/ytzjyzy4m2e/build-a-simple-raspberry-pi-led-power-status-indicator).

# Software setup

## External libraries
* gpiozero
* mpd2

## Systemd integration
maui.service


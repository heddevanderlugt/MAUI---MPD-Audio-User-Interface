# MAUI - MPD Audio User Interface
This module let you use any MPD based audio player using your own hardware buttons and/or LCD screen. Developed to reuse the buttons and lcd from my audioset to control a Raspberry PI audio setup. I choose Moode Audio but should work with any MPD based audio setup i.e XBMC/Kodi.

Picture below shows my audio setup, top device is a modified tuner which internals are replaced by a Raspberry PI 3B running Moode Audio.

![cambridge audio setup](pics/frontview.jpeg)

It is developed for my own usage. Tested only on my setup.
Setup:
	Raspberry PI 3B (all versions should work)
	Cambridge Tuner, guts removed, buttons and LCD connected to Raspberry

External libraries:
	gpiozero
	mpd2

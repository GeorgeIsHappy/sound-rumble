import pyaudio
import array
import numpy
import os
import random
import math
import evdev

# Initialize pyaudio

CHANNELS = 1
RATE = 48000
CHUNK = 1024
FORMAT = pyaudio.paFloat32

pa_manager = pyaudio.PyAudio()
stream = pyaudio.Stream(pa_manager, RATE, CHANNELS, FORMAT, input=True, frames_per_buffer=CHUNK)

# Initialize variables

average_samples = 100

volume_list = array.array('f')

first = True

# User select controller

print('\nAvaliable devices:')

device_list = evdev.list_devices()

for i in device_list:
	print(i + ": " + evdev.InputDevice(i).name)

print("\nType device number and press enter")

selected_device_number = input();
selected_device = evdev.InputDevice("/dev/input/event" + selected_device_number)

# Main loop

while True:
	
	# Grab audio string and convert to array
	
	databin = stream.read(CHUNK)
	data = array.array('f')
	data.fromstring(databin)
	
	# Eradicate negatives
	
	for i in range(len(data)):
		data[i] = abs(data[i])
	
	# Find current volume
	
	volume = numpy.mean(data)
	volume = volume ** 2
	
	# Make list of last n volumes
	
	volume_list.insert(0, volume)
	
	if len(volume_list) > average_samples:
		volume_list.pop(average_samples)
	
	# Find average volume
	
	average = numpy.mean(volume_list)
	
	# Increase intensity if volume is above average
	
	if volume > average:
		intensity = volume-average
	else:
		intensity = 0
	
	# Set vibration to intensity
	
	rumble = evdev.ff.Rumble(int(intensity * 65535), int(intensity * 65535))
	
	effect = evdev.ff.Effect(evdev.ecodes.FF_RUMBLE, -1, 0, evdev.ff.Trigger(0, 0), evdev.ff.Replay(int(CHUNK / RATE * 1000), 0), evdev.ff.EffectType(ff_rumble_effect=rumble))
	
	if first:
		first = False
	else:
		selected_device.erase_effect(effect_id)
	
	effect_id = selected_device.upload_effect(effect)
	selected_device.write(evdev.ecodes.EV_FF, effect_id, 1)

"""
Show all HID devices information

HID\VID_0B43&PID_0003&REV_1912&Col01
HID\VID_0B43&PID_0003&REV_1912&Col02

pip install python-uinput
pip install pywinusb


#JOY1
Joy1_16 - Left
Joy1_14 - Right
Joy1_13 - Up
Joy1_15 - Down
Joy1_3  - Up-Left
Joy1_2  - Up-Right
Joy1_10 - Start
Joy1_9  - Select

u'HID\\VID_0B43&PID_0003&COL01\\7&10F50921&4&0000'

"""
"""
Handling raw data inputs example
"""

from msvcrt import kbhit
from time import sleep
import pywinusb.hid as hid
import win32api
import win32com.client
import win32ui
import win32con
import win32gui
import win32process
import re

#A buffer of what keys are being pressed is kept for both ports to manage KeyUp events
keyBuffer = [[],[]]
#Various flags to control debug prints
p1debug = 0
p2debug = 0
statedebug = 0

#Hardcoded keyboard mapping
#TODO: Support for different mappings
#TODO: Full controller support
PAD1_CODE = {'start':0x0D, #'enter'
	   'select':0x08, #'backspace'
	   'left':0x25, #'left_arrow'
	   'up':0x26, #'up arrow'
	   'right':0x27, #right arrow
	   'down':0x28, #down arrow
	   'upleft':0x41, # 'a'
	   'upright':0x42, # 'b'
	   'dnleft':0x43, #'c'
	   'dnright':0x44} #'d'

PAD2_CODE = {'start':0xDB, # '['
		'select':0xDD, #']'
		#'numpad_0':0x60,
		'dnleft':0x61, # 'numpad_1'
		'down':0x62, # 'numpad_2'
		'dnright':0x63, # 'numpad_3'
		'left':0x64, # 'numpad_4'
		#'numpad_5':0x65, # 'numpad_5'
		'right':0x66, # 'numpad_6'
		'upleft':0x67, # 'numpad_7'
		'up':0x68, # 'numpad_8'
		'upright':0x69}  # 'numpad_9'
mapping = [PAD1_CODE, PAD2_CODE]

'''
A comment on how the input signal is handled:
Eight 0-255 values
1 - Controller port, either 1 or 2
2 - Face and shoulder buttons. From right to left, each bit is:
Triangle, Circle, Cross, Square, L2, R2, L1, R1
3 - D-Pad and "control" buttons. From right to left, each bit is:
Select, Start, L3, R3, Up, Right, Down, Left
4 - Left Joystick, X value
5 - Left Joystick, Y value
6 - Right Joystick, X value
7 - Right Joystick, Y value
For joystick values, 0-255 is the full range from left to right and *UP TO DOWN*
8 - Controller state. We've only found three states: 255 is unplugged, 65 is plugged with analog off, and 115 is plugged with analog on

Dance pads control both joysticks and the D-Pad with the directional buttons. The rest of the buttons work as they should.
If opposite directions are pressed, then both D-Pad signals are sent, and the analog signal is set to neutral, 128

Guitars also control the D-Pad and both joysticks simultaneously. The strum bar sends regular up and down signals. 
Supposedly, the whammy bar controls the horizontal signal, going from 0 to 255 the further down it's pressed, 
thus always sending a "left" signal by default. In our testing, we weren't able to produce any signal using the whammy bar.
The rest of the buttons are mapped as such:
Select and Start are mapped to Select and Start
Yellow - Triangle
Red - Circle
Blue - Cross
Orange - Square
Green - R2
'''

#Signals are numbered 1 through 2, arrays go from 0 to 1, hence joy-1
def sample_handler(data):
	signal = data.data
	pressed = []
	joy = signal[0]
	if signal[1] != 0 or signal[2] != 0:
		if signal[1] != 0:
			pressed.extend(angle_dirs(signal[1]))
		if signal[2] != 0:
			pressed.extend(card_dirs(signal[2]))
		button_mapper(joy-1, pressed)
		
	if p1debug and joy==1: print(signal)
	if p2debug and joy==2: print(signal)
	
	button_cleanup(joy-1,pressed)

#TODO: Refurbish how signals are translated using binary flags
def card_dirs(value):
	dirval = {128:'left', 64:'down', 32:'right', 16:'up', 2:'start', 1:'select' }
	pressed = []
	for key in reversed(sorted(dirval.keys())):
		if value >= key:
			pressed.append(dirval[key])
			value -= key
	return pressed

def angle_dirs(value):
	dirval = {8:'dnright', 4:'upleft', 2:'upright', 1:'dnleft' }
	pressed = []
	for key in reversed(sorted(dirval.keys())):
		if value >= key:
			pressed.append(dirval[key])
			value -= key
	return pressed

def button_mapper(joy, pressed):
	for val in pressed:
		if not (val in keyBuffer[joy]):
			if statedebug: print("joy ",joy+1," signal added - ",val)
			keyBuffer[joy].append(val)
			win32api.keybd_event(mapping[joy][val],0,0,0)


def button_cleanup(joy, pressed):
	for val in keyBuffer[joy]:
		if not (val in pressed):
			if statedebug: print("joy ",joy+1," signal removed - ",val," list was ",pressed)
			keyBuffer[joy].remove(val)
			win32api.keybd_event(mapping[joy][val],0 ,win32con.KEYEVENTF_KEYUP ,0)


def detect_device():
	all_hids = hid.find_all_hid_devices()
	pads = []
	for hids in all_hids:
		matchObj = re.match(r'HID\\VID_0B43&PID_0003', hids.instance_id, re.M)
		if matchObj:
			pads.append(hids)
	return pads

#TODO: Sleep is probably unnecessary
def pad_init():
	pads = detect_device()
	if pads:
		#pads[1].open()
		#pads[1].set_raw_data_handler(sample_handler)
		for pad in pads:
			pad.open()
			pad.set_raw_data_handler(sample_handler)
		print("\nWaiting for data...")
		#while not kbhit() and pads[0].is_plugged():
		while True: #not kbhit(): #and device.is_plugged()
			#just keep the device opened to receive events
			#if kbhit():
			#	sleep(0.5)
			#	print ("Pausing...")
			sleep(0.0001)
		return
	else:
		print("No EMS USB2 device detected. Exiting")
		sys.exit(1)

#Legacy code? Not used anywhere else
'''
def get_inner_windows(whndl):
	def callback(hwnd, hwnds):
		if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
			hwnds[win32gui.GetClassName(hwnd)] = hwnd
		return True
	hwnds = {}
	win32gui.EnumChildWindows(whndl, callback, hwnds)
	return hwnds
'''

#Legacy test code
'''
def raw_test():
	detect_device()
	all_hids = hid.find_all_hid_devices()
	if all_hids:
		while True:
			print("Choose a device to monitor raw input reports:\n")
			print("0 => Exit")
			for index, device in enumerate(all_hids):
				device_name = unicode("{0.vendor_name} {0.product_name}" \
						"(vID=0x{1:04x}, pID=0x{2:04x})"\
						"".format(device, device.vendor_id, device.product_id))
				print("{0} => {1}".format(index+1, device_name))
			print("\n\tDevice ('0' to '%d', '0' to exit?) " \
					"[press enter after number]:" % len(all_hids))
			index_option = raw_input()
			if index_option.isdigit() and int(index_option) <= len(all_hids):
				# invalid
				break;
		int_option = int(index_option)
		if int_option:
			device = all_hids[int_option-1]
			try:
				device.open()

				#set custom raw data handler
				device.set_raw_data_handler(sample_handler)

				print("\nWaiting for data...\nPress any (system keyboard) key to stop...")
				while not kbhit() and device.is_plugged():
					#just keep the device opened to receive events
					sleep(0.5)
				return
			finally:
				device.close()
	else:
		print("There's not any non system HID class device available")
'''

if __name__ == '__main__':
	# first be kind with local encodings
	import sys
	if sys.version_info >= (3,):
		# as is, don't handle unicodes
		unicode = str
		raw_input = input
	else:
		# allow to show encoded strings
		import codecs
		sys.stdout = codecs.getwriter('mbcs')(sys.stdout)
	
	#Provisional debug options
	for arg in sys.argv	:
		if arg=="-h" or arg=="--help": 
			print("Options:")
			print("-p1/p2\t: Constantly displays the received signal from the specified port")
			print("-s\t: Displays signal changes for both players")
			print("")
			exit()
		if arg=="-p1": p1debug = 1
		if arg=="-p2": p2debug = 1
		if arg=="-s": statedebug = 1
		
	#Actual start of code
	pad_init()
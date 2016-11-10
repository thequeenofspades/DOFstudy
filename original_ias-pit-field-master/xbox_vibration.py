'''
 For use with Xbox controllers
 Uses XInput to activate rumbling
 Why? vizjoy uses DirectInput which doesn't support force feedback on Xbox controllers
 More info on the support forum: http://forum.worldviz.com/showthread.php?t=5143
'''

import ctypes, time
from threading import Timer

# Define necessary structures
class XINPUT_VIBRATION(ctypes.Structure):
    _fields_ = [("wLeftMotorSpeed", ctypes.c_ushort),
                ("wRightMotorSpeed", ctypes.c_ushort)]

xinput = ctypes.windll.xinput9_1_0  # Load Xinput.dll
# xinput = ctypes.windll.xinput1_4  # for Windows 8

# Set up function argument types and return type
XInputSetState = xinput.XInputSetState
XInputSetState.argtypes = [ctypes.c_uint, ctypes.POINTER(XINPUT_VIBRATION)]
XInputSetState.restype = ctypes.c_uint

# The helper function with 3 input arguments:
#   controller id ( 0 for the first controller )
#   left motor vibration scaled from 0 (off) to 1.0 (full on)
#   right motor vibration (also 0 - 1.0)
def set_vibration(controller, left_motor, right_motor):
    vibration = XINPUT_VIBRATION(int(left_motor * 65535), int(right_motor * 65535))
    XInputSetState(controller, ctypes.byref(vibration))

# Vibrate controller for [duration] seconds
#	see set_vibration() for args
def vibrate_for(controller, left_motor, right_motor, duration):
	set_vibration(controller, left_motor, right_motor)
	t = Timer(duration, stop_vibration, [controller])
	t.start() # multithreading

# Start vibration, lasts for indefinite number of seconds 
#	or until stop_vibration() is called
#	see set_vibration() for args
def start_vibration(controller, left_motor, right_motor):
	set_vibration(controller, left_motor, right_motor)

# Stop vibration on [controller]
def stop_vibration(controller):
	set_vibration(controller, 0, 0)

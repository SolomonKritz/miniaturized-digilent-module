from ctypes import *
from dwfconstants import *
import math
import time
import sys
import numpy

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

#declare ctype variables
hdwf = c_int()
sts = c_byte()
rgdSamples = (c_double*1)()
rgdSamples2 = (c_double*1)()

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

#open device
print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == hdwfNone.value:
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(szerr.value)
    print("failed to open device")
    quit()

#set up acquisition
dwf.FDwfAnalogInFrequencySet(hdwf, c_double(20000000.0))
dwf.FDwfAnalogInBufferSizeSet(hdwf, c_int(10))
dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(0), c_bool(True))
dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(0), c_double(5))

#wait at least 2 seconds for the offset to stabilize
time.sleep(2)

print("Starting oscilloscope")
dwf.FDwfAnalogInConfigure(hdwf, c_bool(False), c_bool(True))

while True:
    dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
    if sts.value == DwfStateDone.value :
        break
    time.sleep(0.1)
print("Acquisition starting")

csvfile = open("Data.txt","w+")
#csvfile.write("Data collection CSV\n")
csvfile.write("Time(s) , Analog_1(V) , Analog_2(V)\n")

#for i in range(1,1000):
while (1):
    try:
        dwf.FDwfAnalogInStatusData(hdwf, 0, rgdSamples, 1) # get channel 1 data
    	dwf.FDwfAnalogInStatusData(hdwf, 1, rgdSamples2, 1) # get channel 2 data
    	#print(rgdSamples)
    	#print(numpy.fromiter(rgdSamples, dtype = numpy.float))
    	AnalogValues = numpy.fromiter(rgdSamples, dtype = numpy.float)
    	DigitalValues = numpy.fromiter(rgdSamples2, dtype = numpy.float)
    	values = str(time.time()) +"," + str(AnalogValues[0]) + "," + str(DigitalValues[0]) + "\n"
    	#i = i + 1
    	#csvfile.write(numpy.fromiter(rgdSamples, dtype = numpy.float))
    	csvfile.write(str(values))
    	time.sleep(0.05)
    except (KeyboardInterrupt):
	print("Stopping")
	break

print("Acquisition Complete")
dwf.FDwfDeviceCloseAll()
csvfile.close()

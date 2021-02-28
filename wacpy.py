#!/usr/bin/env python3
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software 
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import sys
import libevdev
from libevdev import InputEvent
import time
import subprocess
import serial
# needs libevdev pip libevdev pip serial
# Get all features of those great Wacom Digitizer II models working again in a portable way, including tilt and strip buttons. May work with other Protocol4 devices. Graphire PenPartner Cintiq Since this needs to register a HID device, it must be run as root. If someone wants to test with a graphire
#unlike linuxwacom doesn't send reset, since the supported devices have few useful settings that deviate from defaults at poweron Only non default is the tilt seting. If this causes problems for anyone contact or submit a patch

# Should work on any playform that supports Python3 (3.5 required, only tested on 3.7) and libevdev python serial and libevdev
# pip install libevdev e, linux  FreeBSD, probably mac (untested). Only tested on linux and FreeBSD. You will need to install libevdev if trying to make this work on a mac, 
#recommended way of configuring the driver is to det defaults in this file to your liking, and use the strip buttons to change them.



threshold=4 #necessary if using non-wacom stylus #about the level that the old windows wacom drivers used to set by default. This is stylus units  If using an original wacom stylus this may be set as low as 2, it using an spen /vaio stylus going much less is likely to cause a lot of spurious clicks
tablet_is_tilt_capable='Y' #needs a v1.4 rom to work 


serial_port='/dev/ttyU0'



# 4 button puck numbers its buttons like this
Puck1=libevdev.EV_KEY.BTN_LEFT
Puck0=libevdev.EV_KEY.BTN_MIDDLE
Puck2=libevdev.EV_KEY.BTN_RIGHT

# 4th button not implemented yet

stylus_lower=libevdev.EV_KEY.BTN_STYLUS
stylus_upper=libevdev.EV_KEY.BTN_STYLUS2
use_puck_4_as_scroll_drag="Y"  #risk of false detection if left and middle pressed within 5ms

# get screen resolution. Set height and Width explicitly if this doesn't work
result=subprocess.run(['xwininfo','-root'], stdout=subprocess.PIPE)
restok=result.stdout.split()
ScreenHeight=int(restok[restok.index(b'Height:')+1])
ScreenWidth=int(restok[restok.index(b'Width:')+1])

print("screen ",ScreenWidth,"x",ScreenHeight)

dev = libevdev.Device()
devr = libevdev.Device()
deva = libevdev.Device()
ser = serial.Serial(serial_port,9600) #only 9600 baud supported on tablets we're trying to implement
print(ser.name)
print(dev)
Xmax=0
Ymax=0
#get device model
found="false"
for i in range(1,300) :

	ser.write(b"~#\r")

	s=[]
	for i in range (1,10000) :
		x=ser.read(1)
		s.append(x)
		if x==b'\r' :
			break
	if  s[0:2]==[b'~',b'#'] :
		resp= d=str(b''.join(s[2:]).decode('utf-8'))
		print("found a " , resp)
		dev.name=resp.split()[0]
		devr.name=resp.split()[0]+" Mouse"
		deva.name=resp.split()[0]+" Cursor"
		found="true"
		break
if found=="false" :
	print("fatal got garbage back from model query")
	sys.exit(1)



#get max coordinates
ser.write(b"~C\r")
s=[]
for i in range (1,10000) :
	x=ser.read(1)
	s.append(x)
	if x==b'\r' :
		break
if  s[0:2]==[b'~',b'C'] :	
	resp= d=str(b''.join(s[2:]).decode('utf-8'))
	Xmax=int(resp.split(',')[0])
	Ymax=int(resp.split(',')[1])

	print("coord range ",Xmax , " " , Ymax)
else :
	print("fatal got garbage back from max coordinate query. TODO deal with graphire")
	sys.exit()

dev.enable(libevdev.EV_REL.REL_X )
dev.enable(libevdev.EV_REL.REL_Y )
dev.enable(libevdev.INPUT_PROP_DIRECT)
dev.enable(libevdev.INPUT_PROP_POINTER)
dev.enable(libevdev.EV_KEY.BTN_TOOL_PEN)
dev.enable(libevdev.EV_KEY.BTN_TOOL_RUBBER)
dev.enable(libevdev.EV_KEY.BTN_STYLUS)
dev.enable(libevdev.EV_KEY.BTN_STYLUS2)
dev.enable(libevdev.EV_ABS.ABS_X,libevdev.InputAbsInfo(minimum=0, maximum=Xmax*10,resolution=1270))
dev.enable(libevdev.EV_ABS.ABS_Y,libevdev.InputAbsInfo(minimum=0, maximum=Ymax*10,resolution=1270))
dev.enable(libevdev.EV_ABS.ABS_PRESSURE,libevdev.InputAbsInfo(0,254))
dev.enable(libevdev.EV_ABS.ABS_TILT_X,libevdev.InputAbsInfo(minimum=-64, maximum=64))
dev.enable(libevdev.EV_ABS.ABS_TILT_Y,libevdev.InputAbsInfo(minimum=-64, maximum=64))
dev.enable(libevdev.EV_KEY.BTN_LEFT)
dev.enable(libevdev.EV_KEY.BTN_RIGHT)
dev.enable(libevdev.EV_KEY.BTN_MIDDLE)


devr.enable(libevdev.EV_REL.REL_X )
devr.enable(libevdev.EV_REL.REL_Y )
devr.enable(libevdev.INPUT_PROP_DIRECT)
devr.enable(libevdev.INPUT_PROP_POINTER)
devr.enable(libevdev.EV_KEY.BTN_TOOL_PEN)
devr.enable(libevdev.EV_KEY.BTN_TOOL_LENS)
devr.enable(Puck0)
devr.enable(Puck1)
devr.enable(Puck2)


deva.enable(libevdev.EV_REL.REL_X )
deva.enable(libevdev.EV_REL.REL_Y )
deva.enable(libevdev.INPUT_PROP_DIRECT)
deva.enable(libevdev.INPUT_PROP_POINTER)
deva.enable(libevdev.EV_KEY.BTN_TOOL_PEN)
deva.enable(libevdev.EV_KEY.BTN_TOOL_LENS)
deva.enable(libevdev.EV_ABS.ABS_X,libevdev.InputAbsInfo(minimum=0, maximum=Xmax*10,resolution=1270))
deva.enable(libevdev.EV_ABS.ABS_Y,libevdev.InputAbsInfo(minimum=0, maximum=Ymax*10,resolution=1270))
deva.enable(Puck0)
deva.enable(Puck1)
deva.enable(Puck2)


uinputr = devr.create_uinput_device()
uinputa = deva.create_uinput_device()
uinput = dev.create_uinput_device()
print("New device at {} ({})".format(uinputr.devnode, uinput.syspath))
print("New device at {} ({})".format(uinputa.devnode, uinput.syspath))

print("New device at {} ({})".format(uinput.devnode, uinput.syspath))
tablet_proved_tilt_capable='N'

#request tilt
if tablet_is_tilt_capable=='Y' :
	ser.write(b"FM1\r")
tabaspectratio=Xmax/Ymax
screenaspect=ScreenWidth/ScreenHeight
ymul=10
xmul=ymul*tabaspectratio/screenaspect
Xmul_1_1_full_y_height=xmul 
Ymul_1_1_full_y_height=ymul
xoffset=0
yoffset=0
touchon=0
tool="none"
PuckState0=0
PuckState1=0
PuckState2=0
stylusstate=0
puckmode="abs"
n=[]
lastx=0 
lasty=0
while 1==1 :
	x=ser.read(1)
	if x[0]&b'\x80'[0] !=0 :
		l=len(n)
		if l==9:
			tablet_proved_tilt_capable='Y'
		if (l==7) and (tablet_proved_tilt_capable=='Y') :
			ser.write(b"FM1\r") # not retained across poweroff so a 7 byte packet is the 1st warning we get the tablet may have been restarted. Since once Tilt is enabled the DigitizerII at least sends no 7 byte packets
		n=[]

	n.append(x[0])
	if len(n)==9 or (len(n)>=7 and tablet_proved_tilt_capable=='N') :
		if n[0]&b'\x48'[0]==8  : # button pressed and not pointing device, must be strip button seems to use pressure bits to return button number
			if n[6]==1 :
				xmul=Xmul_1_1_full_y_height
				ymul=Ymul_1_1_full_y_height
				xoffset=0
				yoffset=0
			if n[6]==2 :
				xmul=Xmul_1_1_full_y_height
				ymul=Ymul_1_1_full_y_height
				xoffset=Xmax*xmul*.8   #   0.8 of a tablet across, about right on a 4:3 monitor
				yoffset=0
			if n[6]==3 :
				xmul=Xmul_1_1_full_y_height
				ymul=Ymul_1_1_full_y_height
				xoffset=Xmax*xmul*1.6
				yoffset=0
			if n[6]==4 :
				xmul=Xmul_1_1_full_y_height
				ymul=Ymul_1_1_full_y_height
				xoffset=Xmax*xmul*2.4
				yoffset=0
			if n[6]==5 :
				xmul=Xmul_1_1_full_y_height*2    #lower half of tablet across 2 displays
				ymul=Ymul_1_1_full_y_height*2
				xoffset=0
				yoffset=Ymax*ymul*-0.5
			if n[6]==6 :
				xmul=Xmul_1_1_full_y_height*3    #lower third of tablet across left 3 displays or  so
				ymul=Ymul_1_1_full_y_height*3
				xoffset=0
				yoffset=Ymax*ymul*-0.666666666
			if n[6]==31 : 
				print("Puck ABS")
				puckmode="abs"
			if n[6]==32  :
				print("Puck REL")
				puckmode="rel"
			print("strip button ",n[6])
		else :
			x=int(n[1])*128+int(n[0]&b'\x03'[0])*16384+int(n[2])
			y=int(n[5])+int(n[4])*128+int(n[3]&b'\x03'[0])*16384
			psb=int(n[6]&b'\x40'[0])
			#print(n[6])
			# old linuxwacom states byte3 bit 2 is P0 bit, 
			p=(((n[6]<<1)|((n[3]>>2) & b'\x01'[0]))  +127)&255 #+ (n[3]>>2 & b'\x01'[0])
			tx=0
			if(len(n)==9) :
				tx=n[7]
				if (tx & 64 !=0) :
					tx=tx-128
			ty=0
			if(len(n)==9) :
				ty=n[8]
				if (ty & 64 !=0) :
					ty=ty-128
		
			# only scan 3 button bits since 4 button puck simply seems to alias button4 to 1+2 bits. I can only guess that B3 was reserved for the 10 button puck, but I don't have one to test. 
			#print(n[3] & b'\xff'[0])
			events=[]
			if tool=="puck" :
				if n[3]&b'\x10'[0]==b'\x10'[0] and PuckState1==0 :
					PuckState1=1
					events.append(libevdev.InputEvent(Puck1,1))
				if n[3]&b'\x10'[0]==b'\x00'[0] and PuckState1==1 :
					PuckState1=0
					events.append(libevdev.InputEvent(Puck1,0))
				if n[3]&b'\x20'[0]==b'\x20'[0] and PuckState2==0 :
					PuckState2=1
					events.append(libevdev.InputEvent(Puck2,1))
				if n[3]&b'\x20'[0]==b'\x00'[0] and PuckState2==1 :
					PuckState2=0
					events.append(libevdev.InputEvent(Puck2,0))
				if n[3]&b'\x08'[0]==b'\x08'[0] and PuckState0==0 :
					print("M")
					PuckState0=1
					events.append(libevdev.InputEvent(Puck0,1))
				if n[3]&b'\x08'[0]==b'\x00'[0] and PuckState0==1 :
					PuckState0=0
					events.append(libevdev.InputEvent(Puck0,0))
			if n[0]&b'\x60'[0]==b'\x60'[0] and n[3]&b'\x20'[0] == b'\x20'[0] and tool== "none":
				tool="eraser"
				print("erasers down")
				events.append(libevdev.InputEvent(libevdev.EV_KEY.BTN_TOOL_RUBBER,1))
			if n[0]&b'\x60'[0]==b'\x60'[0] and tool== "none":
				tool="stylus"
				print("stylus down")
				events.append(libevdev.InputEvent(libevdev.EV_KEY.BTN_TOOL_PEN,1))
			if n[0]&b'\x60'[0]==b'\x40'[0] and tool== "none":
				tool="puck"
				if puckmode=="abs" :
					print("puck down abs")
					events.append(libevdev.InputEvent(libevdev.EV_KEY.BTN_TOOL_LENS,1))
				if puckmode=="rel" :
					print("puck down rel")
					events.append(libevdev.InputEvent(libevdev.EV_KEY.BTN_TOOL_LENS,1))
					lastx=x
					lasty=y
			if n[0]&b'\x40'[0]==0 and tool =="stylus" :
				tool="none"
				print("stylus up")
				if stylusstate==1 :
					stylusstate=0
					events.append(libevdev.InputEvent(stylus_lower,0))
				if stylusstate==2 :
					stylusstate=0
					events.append(libevdev.InputEvent(stylus_upper,0))
				events.append(libevdev.InputEvent(libevdev.EV_KEY.BTN_TOOL_PEN,0))
			if n[0]&b'\x40'[0]==0 and tool =="puck" :
				tool="none"
				print("puck up")
				if puckmode=="abs" :
					events.append(libevdev.InputEvent(libevdev.EV_KEY.BTN_TOOL_LENS,0))
					events.append(libevdev.InputEvent(libevdev.EV_KEY.BTN_TOOL_MOUSE,0))
				if puckmode=="rel" :
					events.append(libevdev.InputEvent(libevdev.EV_KEY.BTN_TOOL_LENS,0))
			if n[0]&b'\x40'[0]==0 and tool =="eraser" :
				tool="none"
				print("eraser up")
				events.append(libevdev.InputEvent(libevdev.EV_KEY.BTN_TOOL_RUBBER,0))
			if tool=="puck" and puckmode=="rel" :
				events.append(libevdev.InputEvent(libevdev.EV_REL.REL_X, int((x-lastx)/4)))
				events.append(libevdev.InputEvent(libevdev.EV_REL.REL_Y, int((y-lasty)/4)))
			elif tool !="none" :
				events.append(libevdev.InputEvent(libevdev.EV_ABS.ABS_X,  int(x*xmul+xoffset) ))
				events.append(libevdev.InputEvent(libevdev.EV_ABS.ABS_Y,  int(y*ymul+yoffset)))
			if (tool=="stylus" or tool=="eraser" ):
				pp=0
				if p>=threshold :
					pp=p-threshold
				events.append(libevdev.InputEvent(libevdev.EV_ABS.ABS_PRESSURE,pp))
				events.append(libevdev.InputEvent(libevdev.EV_ABS.ABS_TILT_X ,tx))
				events.append(libevdev.InputEvent(libevdev.EV_ABS.ABS_TILT_Y ,ty))
#				if n[3]&b'\x10'[0]==b'\x10'[0] :
#					print("styluslow")
#				if n[3]&b'\x20'[0]==b'\x20'[0] :
#					print("stylushigh")
#			if tool=="puck" :
#				events.append(libevdev.InputEvent(libevdev.EV_ABS.ABS_PRESSURE,0))
#				events.append(libevdev.InputEvent(libevdev.EV_ABS.ABS_TILT_X ,0))
#				events.append(libevdev.InputEvent(libevdev.EV_ABS.ABS_TILT_Y ,0))
#			if p >= threshold and touchon==0 and (tool=="stylus" or tool =="eraser") :
#				events.append(libevdev.InputEvent(libevdev.EV_KEY.BTN_LEFT,1))
#				events.append(libevdev.InputEvent(libevdev.EV_KEY.BTN_STYLUS,1))
				touchon=1
#			if (p<threshold or tool=="none" ) and touchon==1 :
#				events.append(libevdev.InputEvent(libevdev.EV_KEY.BTN_LEFT,0))
#				events.append(libevdev.InputEvent(libevdev.EV_KEY.BTN_STYLUS,0))
				touchon=0
			if (tool=="stylus" ):
				if n[3]&b'\x10'[0]==b'\x10'[0] and stylusstate == 0 :
					stylusstate=1
					events.append(libevdev.InputEvent(stylus_lower,1))
				if n[3]&b'\x10'[0]==b'\x00'[0] and stylusstate == 1 :
					stylusstate=0
					events.append(libevdev.InputEvent(stylus_lower,0))
				if n[3]&b'\x20'[0]==b'\x20'[0] and stylusstate == 0 :
					stylusstate=2
					events.append(libevdev.InputEvent(stylus_upper,1))
				if n[3]&b'\x20'[0]==b'\x00'[0] and stylusstate == 2 :
					stylusstate=0
					events.append(libevdev.InputEvent(stylus_upper,0))


			events.append(libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT,0))
			if (tool=="puck" and puckmode=="rel") :

				uinputr.send_events(events)
			if (tool=="puck" and puckmode=="abs") :

				uinputa.send_events(events)
			else :
				uinput.send_events(events)
			lastx=x
			lasty=y
			


# WacomUD-python
Highly customizable driver written in Python for Wacom UD tablets, including tilt support. 

Requires a Wacom Digitizer II series tablet to be useful
Since it needs to register a HID device, this must be run as root

Should work on any playform that supports Python3 (3.5 required, only tested on 3.7) and libevdev 

Requires python serial and libevdev 
 
 Tested on FreeBSD and Ubuntu 20

Edit the line begining serial_port to specify the name of your serial port before running.

Edit the button assignment to the buttons on your tablet. In particular modify the ABS REL to the last 2 buttons on your tablet, no 31 and 32 is for the 12x18" inch tablet 

By default, the first 6 tablet buttons are set to control the mapping of the tablet to the desktop.



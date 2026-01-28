# Pi_USB_Hailo_Detect

Detects objects and saves MP4 videos, using USB camera, pi5 and hailo hat.

![screenshot](screen.jpg)

To setup the hailo..

sudo apt update && sudo apt full-upgrade -y
 
 sudo reboot

 with Trixie sudo apt install dkms

 with hailo 8L (Ai HAT+) sudo apt install hailo-all

 with hailo 10H (Ai HAT+2) sudo apt install hailo-h10-all

 sudo reboot

 git clone --depth 1 https://github.com/raspberrypi/picamera2
 
reboot

sudo apt install python3-opencv -y

put detectUSB.py in /home/USERNAME/picamera2/examples/hailo

Captures .mp4 videos  in /home/USERNAME/Videos

set required objects in objects = ["person","dog","cat"]

tested on Pi5, hailo, logitech c270.

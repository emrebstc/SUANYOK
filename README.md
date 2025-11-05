Hardware Specifications of ASUS Tinker Board S
----------------------------------------------
CPU: Rockchip Quad-core 32Bit ARMv7 Cortex-A17, up to 1.8 GHz RK3288 processor (SoC) 

Memory: 2GB Dual Channel DDR3 

Graphic: Integrated Graphics Processor & ARM® Mali™-T764 GPU 

Storage: 16GB eMMC 

USB Ports: 4 x USB 2.0 


Configuration
-------------
OS : Armbian Bookworm 25.8.2 (headless, no GUI)

Download Link: https://www.armbian.com/tinkerboard/

Kernel: Linux tinkerboard 6.12.55-current-rockchip #1 SMP armv7l 

Python Version: 3.11.2

Flask Version: 3.1.2 

Tflite-runtime Version: 2.14.0

Numpy Version: 1.24.2

OpenCV Version: 4.6.0 (headless)

Model	Type	Path	Description
-----------------------------
res10_300x300_ssd_iter_140000.caffemodel  path: /root/

deploy.prototxt , path : /root/

selfie_multiclass_256x256.tflite , path : /root/


Devices
-------
Camera: USB UVC-compatible camera (e.g. /dev/video0 or /dev/video1)

Resolution: 640×480 @ 30 FPS

Backend: V4L2, v4l2-ctl 1.22.1 


Network & Access
----------------
Flask Web Stream: http://<TINKER_IP>:5000

Gallery Page: http://<TINKER_IP>:5000/gallery

Port: 5000 (TCP)

Access via LAN browser


Filesystem
----------
Segmented image save directory: /root/segments

Saved images format: .jpg

Naming: segment_001.jpg, segment_002.jpg, …


Executing the program
---------------------
1) sudo su
   
2) cd /root
   
3) Find IPv4 of your tinkerboard, type : ip a

4) ls /dev/video* (Find your device its name will be something like "/dev/video0-5", example: video3)

5) Edit, cap = cv2.VideoCapture("/dev/video0", cv2.CAP_V4L2) on det_seg_gallery.py
   
6) for c in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do echo performance > $c, done
   
7) python3 det_seg_gallery.py
   
8) Type "http://<TinkerIp>:5000 , for watch streaming
    
9) Type "http://<TinkerIp>:5000 , for reach gallery
  
10) "CTRL + C" for kill the program

Additional
----------
You may share your file to tinker board via SCP tool, for that:

1)sudo apt install openssh-client -y

2)After installation execute powershell or terminal

3)For send files, find your file path and just type on powershell: 

4)scp "C:\Users\YOURUSERNAME\Downloads\YOURFILE.py" root@<TINKERIP>:/root

5)For get files, find your file path and just type on terminal:

6)scp -r root@<TINKERIP>:/root/YOURFILE.py C:\Users\YOURUSERNAME\Downloads




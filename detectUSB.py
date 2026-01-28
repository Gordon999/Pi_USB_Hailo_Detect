#!/usr/bin/env python3

"""Example module for Hailo Detection using USB camera."""

"""Copyright (c) 2026
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE. """

version = 1.01

import argparse
import cv2
from picamera2.devices import Hailo
import os
import numpy as np
import datetime
import time

# detection objects
objects = ["person","dog","cat"]

# set parameters
bw = 200
winName = "winName"
cv2.namedWindow(winName)
ix = 0
font = cv2.FONT_HERSHEY_SIMPLEX
encoding = False
det_timer = time.monotonic()
show_detects = True
h_user = "/home/" + os.getlogin( )

# find USB camera
cam1 = -1
x = 0
while cam1 == -1 and x < 42:
    txt = "v4l2-ctl -d " + str(x) + " --list-ctrls > /run/shm/cam_ctrls.txt"
    os.system(txt)
    ctrls = []
    with open("/run/shm/cam_ctrls.txt", "r") as file:
        line = file.readline()
        while line:
            ctrls.append(line)
            line = file.readline()
    if 'User Controls\n' in ctrls and ('Camera Controls\n' in ctrls):
        cam1 = x
    else:
        x +=1

if cam1 == -1:
    print(" No USB camera found !!")
    exit()

txt = "lsusb > usb_list.txt"
os.system(txt)
webcam = 0
with open("usb_list.txt", "r") as file:
    line = file.readline()
    if "C270" in line and "Logitech" in line: 
        webcam = 270
    while line:
        line = file.readline()
        if "C270" in line and "Logitech" in line: 
            webcam = 270

def onmouse(event,x,y,flags,params):
  global ix,iy,iy2,bh,bw,ix2
  ix = 0
  if event == cv2.EVENT_LBUTTONDOWN:
      if x > panel_width and x < panel_width + bw/2:
          ix = 1
      elif x >= panel_width + bw/2:
          ix = 2
      iy = int(y/bh)
      iy2 = (y/bh) - iy
      ix2 = (x-panel_width)/bw

cv2.setMouseCallback(winName,onmouse)

def keys (cn,rn,bh,kr,kg,kb,kf):
    global bw
    kx = (cn)
    ky = (rn * bh)
    cv2.rectangle(q,(kx,ky),(kx+bw,ky+(bh-4)),(kb,kg,kr),kf)

def text (cn,rn,th,text,tf,tr,tg,tb,tw):
    global bh,bw
    tx = cn
    ty = (rn*bh) + int(bh/2) 
    if th == 1:
        tx += int(bw/2.2)
        ty += int(bh/3)
    cv2.putText(q,text,(tx ,ty), font, tf,(tb,tg,tr),tw)
    
# detect which hailo
if os.path.exists ("/run/shm/hailo_m.txt"): 
    os.remove("/run/shm/hailo_m.txt")
os.system("hailortcli fw-control identify >> /run/shm/hailo_m.txt")
hver = ""
with open("/run/shm/hailo_m.txt", "r") as file:
    line = file.readline()
    while line:
       line = file.readline()
       if line[0:11] == "Device Arch":
           hver = line[26:28]
if hver != "":
    print("HAILO",hver)
else:
    print("No Hailo HAT installed ?")
    quit()

def camera_controls():
    # find camera controls
    global cam1,parameters,panel_height,bh,ft,fv,text
    txt = "v4l2-ctl -l -d " + str(cam1) + " > /run/shm/cam_ctrls.txt"
    os.system(txt)
    config = []
    with open("/run/shm/cam_ctrls.txt", "r") as file:
        line = file.readline()
        while line:
            config.append(line.strip())
            line = file.readline()
    parameters = []
    for x in range(0,len(config)):
        fet = config[x].split(' ')
        name = ""
        minm = -1
        maxm = -1
        step = -1
        defa = -1
        valu = -1
        for y in range(0,len(fet)):
            name = fet[0]
            if fet[y][0:3] == "min":
                minm = fet[y][4:]
            if fet[y][0:3] == "max":
                maxm = fet[y][4:]
            if fet[y][0:3] == "ste":
                step = fet[y][5:]
                if webcam == 270 and (name == "exposure_time_absolute" or name == "white_balance_temperature"):
                    step = 50
            if fet[y][0:3] == "def":
                defa = fet[y][8:]
            if fet[y][0:3] == "val":
                valu = fet[y][6:]
            if valu != -1 and defa != -1: 
                parameters.append(name)
                parameters.append(minm)
                parameters.append(maxm)
                parameters.append(step)
                parameters.append(defa)
                parameters.append(valu)
                name = ""
                minm = -1
                maxm = -1
                step = -1
                defa = -1
                valu = -1
    if len(parameters) > 0:
        bh = int(panel_height/((len(parameters)/6)+2))
        bh = min(bh,80)
        ft = int(bh/2.6)
        ft = min(ft,20)
        fv = int(bh/2.6)
        fv = min(fv,20)

def setup_screen():
    global bw,bh,preview_width
    for j in range(0,int(len(parameters)/6)):
        keys (0,j,bh,128,128,128,-1)
    for j in range(0,int(len(parameters)),6):
        text (0,int(j/6),0,parameters[j],.4,255,255,255,1)
        text (0,int(j/6),1,parameters[j+5],.4,255,0,0,1)
        l = int(bh/25)
        if int(parameters[j + 1]) != -1:
            k = 1 + int(int(parameters[j+5]) / (int(parameters[j + 2]) - int(parameters[j + 1]))  * bw)
            cv2.rectangle(q, (0,((int(j/6)) * bh)+3),(bw,((int(j/6)) * bh)+3 + l), (50, 50, 50, 0), 5)
            cv2.rectangle(q, (k-5,((int(j/6)) * bh)+3),(k+1,((int(j/6)) * bh)+3 + l), (0, 0, 200, 0), 4)
    keys (0,int(len(parameters)/6),bh,100,128,128,-1)
    text (0,int(len(parameters)/6),0,"Factory Defaults",.4,255,255,255,1)
    keys (0,int(len(parameters)/6)+1,bh,100,128,128,-1)
    text (0,int(len(parameters)/6)+1,0,"EXIT",.4,255,255,255,1)

def extract_detections(hailo_output, w, h, class_names, threshold=0.5):
    """Extract detections from the HailoRT-postprocess output."""
    results = []
    for class_id, detections in enumerate(hailo_output):
        for detection in detections:
            score = detection[4]
            if score >= threshold:
                y0, x0, y1, x1 = detection[:4]
                bbox = (int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h))
                results.append([class_names[class_id], bbox, score])
    return results

def draw_objects(request):
    global show_detects
    current_detections = detections
    if current_detections and show_detects == True:
        for class_name, bbox, score in current_detections:
            x0, y0, x1, y1 = bbox
            label = f"{class_name} %{int(score * 100)}"
            cv2.rectangle(winName, (x0, y0), (x1, y1), (0, 255, 0, 0), 2)
            cv2.putText(winName, label, (x0 + 5, y0 + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0, 0), 1, cv2.LINE_AA)

if __name__ == "__main__":
    # Parse command-line arguments.
    parser = argparse.ArgumentParser(description="Detection Example")
    if hver == "8L":
        parser.add_argument("-m", "--model", help="Path for the HEF model.",
                        default="/usr/share/hailo-models/yolov8s_h8l.hef")
    else:
        parser.add_argument("-m", "--model", help="Path for the HEF model.",
                        default="/usr/share/hailo-models/yolov8m_h10.hef")
    parser.add_argument("-l", "--labels", default= h_user + "/picamera2/examples/hailo/coco.txt",
                        help="Path to a text file containing labels.")
    parser.add_argument("-s", "--score_thresh", type=float, default=0.5,
                        help="Score threshold, must be a float between 0 and 1.")
    args = parser.parse_args()

    # Get the Hailo model, the input size it wants.
    with Hailo(args.model) as hailo:
        model_h, model_w, _ = hailo.get_input_shape()
        panel_width = model_w
        panel_height = model_h
        q = np.zeros((panel_height,bw,3), np.uint8)
        camera_controls()
        camera_controls()
        setup_screen()

        # Load class names from the labels file
        with open(args.labels, 'r', encoding="utf-8") as f:
            class_names = f.read().splitlines()

        # The list of detected objects to draw.
        detections = None

        # Start CV2 Videocapture.
        cap = cv2.VideoCapture(cam1)
        if not cap.isOpened():
            print("Cannot open camera")
            exit()

        fourcc = cv2.VideoWriter_fourcc(*'MP4V')
 
        # Process each camera winName.
        while True:
            # Capture frames
            ret, frame = cap.read()
            vid_h,vid_w = frame.shape[:2]
            winName = cv2.resize(frame, (model_h, model_w))
                
            # Run inference on the preprocessed winName
            results = hailo.run(winName)

            # Extract detections from the inference results
            detections = extract_detections(results, model_h, model_w, class_names, args.score_thresh)
            # Draw boxes
            draw_objects(detections)
            # detection
            for d in range(0,len(objects)):
                if len(detections) != 0:
                    value = float(detections[0][2])
                    obj = detections[0][0]
                    print(obj)
                    if value > args.score_thresh and value < 1 and obj == objects[d]:
                        det_timer = time.monotonic()
                        # start MP4 recording
                        if not encoding:
                            startrec = time.monotonic()
                            encoding = True
                            show_detects = False
                            now = datetime.datetime.now()
                            timestamp = now.strftime("%y%m%d_%H%M%S")
                            out = cv2.VideoWriter(h_user + "/Videos/" + timestamp + '.mp4', fourcc, 7.0, (vid_w,vid_h))
                            print("Recording: ", timestamp)
            # write frames to MP4 video
            if encoding == True:
                 out.write(frame)
                 cv2.rectangle(winName,(10,10),(30,30),(0,0,200),-1)
            # stop MP4 recording
            if encoding == True and time.monotonic() - startrec > 10 and time.monotonic() - det_timer > 3:
                 out.release()
                 encoding = False
                 show_detects = True
                 now = datetime.datetime.now()
                 timestamp = now.strftime("%y%m%d_%H%M%S")
                 print("Stopped  : ",timestamp)
                            
            # Show winName
            winName = np.hstack((winName,q))
            cv2.imshow('winName', winName)
            if cv2.waitKey(1) == ord('q'):
                break
            
            # action menu selection   
            if ix > 0:
                if iy > (len(parameters)/6):
                    # exit
                    if encoding == True:
                        out.release()
                    cap.release
                    cv2.destroyAllWindows()
                    break
                if iy2 < 0.2 and iy < len(parameters)/6:
                    p = int((ix2) * (int(parameters[((iy)*6) + 2])-int(parameters[((iy)*6) + 1])))
                    parameters[((iy)*6) + 5] = str(p)
                    text (0,iy,1,parameters[((iy)*6)+5],.4,255,0,0,1)
                    txt = "v4l2-ctl --device=/dev/video" + str(cam1) + " -c " + parameters[(iy)*6] + "=" + str(p)
                    os.system(txt)
                    setup_screen()
                # set camera to factory defaults
                elif iy > (len(parameters)/6) - 1:
                    for h in range(0,len(parameters),6):
                        txt = "v4l2-ctl --device=/dev/video" + str(cam1) + " -c " + parameters[h] + "=" + str(parameters[h+4])
                        os.system(txt)
                    camera_controls()
                    setup_screen()
                else:
                    # change a camera parameter
                    p = int(parameters[(iy*6)+5])
                    if ix == 1:
                        if int(parameters[((iy)*6) + 3]) == -1:
                           p -=1
                        else:
                           p -=int(parameters[((iy)*6) + 3])
                        if int(parameters[((iy)*6) + 1]) != -1:
                           p = max(p,int(parameters[((iy)*6) + 1]))
                        else:
                           p = max(p,0)
                    else:
                        if int(parameters[((iy)*6) + 3]) == -1:
                           p +=1
                        else:
                           p +=int(parameters[((iy)*6) + 3])
                        if int(parameters[((iy)*6) + 2]) != -1:
                            p = min(p,int(parameters[((iy)*6) + 2]))
                        else:
                            p = min(p,1)
                    parameters[((iy)*6) + 5] = str(p)
                    text (0,iy,1,parameters[((iy)*6)+5],.4,255,0,0,1)
                    txt = "v4l2-ctl --device=/dev/video" + str(cam1) + " -c " + parameters[(iy)*6] + "=" + str(p)
                    os.system(txt)
                    if parameters[(iy)*6] == "auto_exposure" and p < 2 and webcam == 270:
                        for a in range(0,len(parameters)):
                            if parameters[a] == "exposure_time_absolute":
                                p = parameters[a+5]
                        txt = "v4l2-ctl --device=/dev/video" + str(cam1) + " -c exposure_time_absolute=" + str(p)
                    os.system(txt)
                    setup_screen()

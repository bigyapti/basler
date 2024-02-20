import pypylon.pylon as py
import os
import numpy as np
import cv2
import datetime

NUM_CAMERAS = 3
# setup demo environment with 3 cameras
os.environ["PYLON_CAMEMU"] = f"{NUM_CAMERAS}"

tlf = py.TlFactory.GetInstance()
# create a device filter for Pylon CamEmu devices
di = py.DeviceInfo()
di.SetDeviceClass("BaslerCamEmu")

# create an array to store the cameras
cam_array = py.InstantCameraArray(NUM_CAMERAS)

# Attach and open cameras, and set triggering configurations
for idx, cam in enumerate(cam_array):
    cam.Attach(tlf.CreateDevice(tlf.EnumerateDevices()[idx]))
    cam.Open()
    cam.SetCameraContext(idx)
    cam.TriggerSelector.SetValue("FrameStart")
    cam.TriggerMode.SetValue("On")
    cam.TriggerSource.SetValue("Software")  
    cam.ExposureTimeRaw.Value = 10000

# start grabbing
cam_array.StartGrabbing()

# Create OpenCV windows for each camera
window_names = [f"Camera {idx}" for idx in range(NUM_CAMERAS)]
for window_name in window_names:
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

# Grab frames indefinitely until interrupted manually

while True:
    for cam in cam_array:
        cam.ExecuteSoftwareTrigger()
    with cam_array.RetrieveResult(1000) as res:
        if res.GrabSucceeded():
            # Get the current time including milliseconds
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            img_nr = res.ImageNumber
            cam_id = res.GetCameraContext()
            print(f"cam #{cam_id}  image #{img_nr} Time: {current_time}")
            
            # Get the grabbed image data
            img = res.Array
            
            # Display the image number and timestamp in the corresponding window
            text = f"Image: {img_nr} | Time: {current_time}"
            cv2.putText(img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow(window_names[cam_id], img)
            cv2.waitKey(1)  # Refresh the display


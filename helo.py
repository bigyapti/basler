import pypylon.pylon as py
import os
import numpy as np
import cv2
import datetime
import threading
cv2.getBuildInformation()

# NUM_CAMERAS = 5
# # setup demo environment with 4 cameras
# os.environ["PYLON_CAMEMU"] = f"{NUM_CAMERAS}"

# tlf = py.TlFactory.GetInstance()
# # create a device filter for Pylon CamEmu devices
# di = py.DeviceInfo()
# di.SetDeviceClass("BaslerCamEmu")

# # create an array to store the cameras
# cam_array = py.InstantCameraArray(NUM_CAMERAS)

# # Attach and open cameras, and set triggering configurations
# for idx, cam in enumerate(cam_array):
#     cam.Attach(tlf.CreateDevice(tlf.EnumerateDevices()[idx]))
#     cam.Open()
#     cam.SetCameraContext(idx)
#     cam.TriggerSelector.SetValue("FrameStart")
#     cam.TriggerMode.SetValue("On")
#     cam.TriggerSource.SetValue("Software")  
#     cam.ExposureTimeRaw.Value = 10000

# # start grabbing
# cam_array.StartGrabbing()

# # Function to trigger and grab frames for a single camera
# def trigger_and_grab(cam, num_frames, barrier):
#     frames = 0
#     try:
#         # Wait for all threads to reach the barrier before starting grabbing
#         barrier.wait()
        
#         while frames < num_frames:
#             cam.ExecuteSoftwareTrigger()
#             with cam.RetrieveResult(1000) as res:
#                 if res.GrabSucceeded():
#                     # Get the current time including milliseconds
#                     current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
#                     img_nr = res.ImageNumber
#                     cam_id = res.GetCameraContext()
#                     print(f"cam #{cam_id}  image #{img_nr} Time: {current_time}")
                    
#                     # Display the image using OpenCV in the corresponding window
#                     # img = res.Array
#                     # cv2.putText(img, f"Camera: {cam_id} | Time: {current_time}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    
#                 frames += 1
#     except KeyboardInterrupt:
#         print("Terminating program...")

# # Barrier to synchronize the start of grabbing frames for all cameras
# start_barrier = threading.Barrier(NUM_CAMERAS)

# # Start threads for triggering and grabbing frames for each camera
# threads = []

# for cam in cam_array:
#     thread = threading.Thread(target=trigger_and_grab, args=(cam, 200, start_barrier))
#     threads.append(thread)

# for thread in threads:
#     thread.start()

# # Wait for all threads to finish
# for thread in threads:
#     thread.join()

# # Stop grabbing and close cameras
# cam_array.StopGrabbing()
# for cam in cam_array:
#     cam.Close()

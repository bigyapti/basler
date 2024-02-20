import os
import cv2
import numpy as np
import datetime
import pypylon.pylon as py


NUM_CAMERAS = 2
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
    cam.ExposureTimeRaw.Value = 100000

# start grabbing
cam_array.StartGrabbing()

# Initialize variables to hold previous timestamps
prev_timestamps = [None] * NUM_CAMERAS

# Create OpenCV windows for each camera
window_names = [f"Camera {idx}" for idx in range(NUM_CAMERAS)]
for window_name in window_names:
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

# Define video writer parameters
fps = 25
frame_width = 1000
frame_height = 500
# Use H.264 codec (AVC1)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
isColor = True

# Create video writer objects for each camera
video_writers = [cv2.VideoWriter(f'camera_{idx}.mp4', fourcc, 60, (frame_width, frame_height), isColor) for idx in range(NUM_CAMERAS)]

# Grab frames until interrupted manually or 'q' is pressed
while True:
    # Execute software trigger and grab frames
    timestamps = []
    frames = []
    for cam, prev_timestamp in zip(cam_array, prev_timestamps):
        cam.ExecuteSoftwareTrigger()
        with cam.RetrieveResult(1000) as res:
            if res.GrabSucceeded():
                # Get the current time including milliseconds
                current_time = datetime.datetime.now()
                img_nr = res.ImageNumber
                cam_id = res.GetCameraContext()

                # Get the grabbed image data
                img = res.Array
                img = cv2.resize(img, (frame_width, frame_height))
                
                # Assign timestamp to the frame
                timestamp = current_time.timestamp()
                timestamps.append(timestamp)
                frames.append((cam_id, img, img_nr, current_time))

    if not timestamps:
        print("No frames grabbed. Skipping this iteration.")
        continue

    # Synchronize frames based on timestamps
    min_timestamp = min(timestamps)
    rounded_timestamps = [round((ts - min_timestamp), 3) for ts in timestamps]

    # Dictionary to hold matched frames with similar timestamps
    matched_frames = {}

    for (cam_id, img, img_nr, current_time), rounded_ts in zip(frames, rounded_timestamps):
        if rounded_ts in matched_frames:
            matched_frames[rounded_ts].append((cam_id, img, img_nr, current_time))
        else:
            matched_frames[rounded_ts] = [(cam_id, img, img_nr, current_time)]

    # Display matched frames together
    for timestamp, matched_frame_list in matched_frames.items():
        for cam_id, img, img_nr, current_time in matched_frame_list:
            print(f"Camera {cam_id} | Frame #{img_nr} | Timestamp: {current_time} | Rounded Timestamp: {timestamp}")
            # Display the image in OpenCV window
            cv2.imshow(window_names[cam_id], img)
            # Write frame to corresponding video writer
            try:
                video_writers[cam_id].write(img)
            except Exception as e:
                print("Error writing frame to video:", e)

    key = cv2.waitKey(1)  # Refresh the display
    if key == ord('q'):  # Check if 'q' is pressed
        break  # Exit the loop if 'q' is pressed

# Stop grabbing and close cameras
cam_array.StopGrabbing()
for cam in cam_array:
    cam.Close()

# Release video writer objects
for writer in video_writers:
    writer.release()

import os
import cv2
import numpy as np
import datetime
import pypylon.pylon as py

NUM_CAMERAS = 2
# Setup demo environment with 3 cameras
os.environ["PYLON_CAMEMU"] = f"{NUM_CAMERAS}"

tlf = py.TlFactory.GetInstance()
# Create a device filter for Pylon CamEmu devices
di = py.DeviceInfo()
di.SetDeviceClass("BaslerCamEmu")
# Create an array to store the cameras
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

# Start grabbing
cam_array.StartGrabbing()

# Define video writer parameters
fps = 25
frame_width = 1000
frame_height = 500

# Directory to save images and videos with a unique timestamp
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
image_dir = f"saved_frames_{timestamp}"
video_dir = f"saved_videos_{timestamp}"
os.makedirs(image_dir, exist_ok=True)
os.makedirs(video_dir, exist_ok=True)

# Create OpenCV windows for each camera
window_names = [f"Camera {idx}" for idx in range(NUM_CAMERAS)]
for window_name in window_names:
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

# Grab frames until interrupted manually or 'q' is pressed
while True:
    # Execute software trigger and grab frames
    timestamps = []
    frames = []
    for cam in cam_array:
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

    # Display matched frames together and save them
    for timestamp, matched_frame_list in matched_frames.items():
        for cam_id, img, img_nr, current_time in matched_frame_list:
            print(f"Camera {cam_id} | Frame #{img_nr} | Timestamp: {current_time} | Rounded Timestamp: {timestamp}")
            # Display the image in OpenCV window
            cv2.imshow(window_names[cam_id], img)
            # Save frame as an image
            image_path = os.path.join(image_dir, f"camera_{cam_id}_frame_{img_nr}.jpg")
            cv2.imwrite(image_path, img)

    key = cv2.waitKey(1)  # Refresh the display
    if key == ord('q'):  # Check if 'q' is pressed
        break  # Exit the loop if 'q' is pressed

# Stop grabbing and close cameras
cam_array.StopGrabbing()
for cam in cam_array:
    cam.Close()

# Close OpenCV windows
cv2.destroyAllWindows()

# Create VideoWriter objects for each camera
video_writers = [cv2.VideoWriter(f'{video_dir}/camera_{idx}.avi', cv2.VideoWriter_fourcc(*'XVID'), 25, (frame_width, frame_height)) for idx in range(NUM_CAMERAS)]

# Loop through saved images and write them to videos
for idx in range(NUM_CAMERAS):
    # Retrieve images
    images = [img for img in os.listdir(image_dir) if img.startswith(f'camera_{idx}_frame_')]
    images.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))  # Sort images by frame number
    
    # Write images to video
    for image in images:
        img_path = os.path.join(image_dir, image)
        frame = cv2.imread(img_path)
        video_writers[idx].write(frame)

# Release VideoWriter objects
for writer in video_writers:
    writer.release()

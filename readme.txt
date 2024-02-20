In the provided code, synchronization is achieved through timestamp alignment. Here's how it works:

Grabbing Frames: Each camera grabs frames independently.

Timestamping: Each frame is assigned a timestamp based on the current system time when it was grabbed.

Synchronization: The timestamps of the frames from different cameras are compared and synchronized based on the minimum timestamp. This ensures that frames from different cameras are aligned as closely as possible in time.

Matching Frames: Frames with similar synchronized timestamps are grouped together, creating sets of frames that are considered synchronized across cameras.

Display and Save: Matched frames from each camera are displayed in OpenCV windows and saved as images. These images are stored in separate directories for each camera with filenames indicating the camera index and frame number.

Writing to Videos: The saved images are then loaded, sorted by frame number, and written to video files using OpenCV's VideoWriter. This process creates synchronized video files for each camera.

By aligning the frames based on their timestamps, this code ensures that frames captured by different cameras at similar points in time are considered synchronized.





import os
import cv2
from skimage.metrics import structural_similarity

def my_slice(video_path, start_frame, end_frame, save_path):
    # Read the video file
    video_capture = cv2.VideoCapture(video_path)
    # Set the starting frame
    video_capture.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    # Get the video frame rate and dimensions
    fps = int(video_capture.get(cv2.CAP_PROP_FPS))
    width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Create a VideoWriter object for writing the new video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(save_path, fourcc, fps, (width, height))

    # Read each frame between the specified range and write it to the new video
    for i in range(start_frame, end_frame):
        ret, frame = video_capture.read()
        if ret:
            out.write(frame)

    # Release resources
    out.release()
    video_capture.release()

def ssim(frame1, frame2):
    """Calculate Structural Similarity (SSIM) between two frames"""
    frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    frame1 = cv2.resize(frame1, (256, 256))
    frame2 = cv2.resize(frame2, (256, 256))
    return structural_similarity(frame1, frame2)

def slice_by_ssim(video_path, ssim_threshold, min_frames_per_slice, save_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video file")
        return

    start = 0
    end = 0
    slice_count = 0

    while True:
        # Set the position of the next frame to read
        cap.set(cv2.CAP_PROP_POS_FRAMES, end)
        ret, prev = cap.read()

        # If we have reached the end of the video, break the loop
        if not ret:
            break

        # Set the position of the next frame to read
        cap.set(cv2.CAP_PROP_POS_FRAMES, end + 10)
        ret, current = cap.read()

        # If we have reached the end of the video, break the loop
        if not ret:
            break

        # Compute the SSIM between prev and current
        ssim_val = ssim(prev, current)
        print("SSIM is", ssim_val)
        if ssim_val > ssim_threshold:
            end += 10
        else:
            # Search for the end of the current slice
            slice_start = start
            slice_end = start
            frames = []
            cap.set(cv2.CAP_PROP_POS_FRAMES, end)

            for i in range(10):
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)
            for i in range(len(frames)-1):
                ssim_val = ssim(frames[i], frames[i+1])
                if ssim_val < ssim_threshold:
                    slice_end = end+i
                    start = end+i+1
                    end = end+i+1
                    break

            if slice_start != slice_end:
                # Check if the slice is long enough
                if slice_end - slice_start > min_frames_per_slice:
                    # Slice the video and save it
                    slice_count += 1
                    slice_path = os.path.join(save_path, f"slice{slice_count}.mp4")
                    print("Saving ", slice_start, " to ", slice_end)
                    my_slice(video_path, slice_start, slice_end, slice_path)
            else:
                end += 10

    cap.release()

if __name__ == '__main__':
    slice_by_ssim("test_input/test.mp4", 0.75, 30, "test_output")

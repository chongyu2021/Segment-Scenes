import os
import cv2
from skimage.metrics import structural_similarity

def ssim(frame1, frame2):
    """Calculate Structural Similarity (SSIM) between two frames"""
    frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    frame1 = cv2.resize(frame1, (512, 512))
    frame2 = cv2.resize(frame2, (512, 512))
    return structural_similarity(frame1, frame2)


def read_frames(video_path, size=1000):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error opening video file")
        return

    while True:
        frames = []

        for _ in range(size):
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)

        if not frames:
            break

        yield frames

    cap.release()

def slice_frames(frames,ssim_threshold):
    start = 0
    end = start + 1
    total_length = len(frames)
    borders = []
    while end != total_length:
        left = end
        right = total_length - 1
        while left != right:
            mid = int((left + right)/2)
            ssim_val = ssim(frames[start], frames[mid])
            if ssim_val > ssim_threshold: # indicating that the same scene
                left = mid + 1
            else:
                right = mid
        borders.append(left)
        start = left
        end = start + 1
    return borders

def frames_to_video(video_path, borders, output_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error opening video file")
        return

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    video_writer = None
    segment_count = 1
    frame_count = 0
    current_border = 0

    while True:
        ret, frame = cap.read()
        frame_count += 1

        if not ret:
            break

        if current_border < len(borders) and frame_count > borders[current_border]:
            if video_writer:
                video_writer.release()

            segment_path = os.path.join(output_path, f"segment_{segment_count}.mp4")
            video_writer = cv2.VideoWriter(segment_path, fourcc, fps, (width, height))
            segment_count += 1
            current_border += 1

        if video_writer:
            video_writer.write(frame)
        else:
            segment_path = os.path.join(output_path, f"segment_{segment_count}.mp4")
            video_writer = cv2.VideoWriter(segment_path, fourcc, fps, (width, height))
            segment_count += 1
            current_border += 1

    if video_writer:
        video_writer.release()

    cap.release()

def segment_scenes(video_path, read_size, min_interval, ssim_threshold, output_path):
    last_frame = None  # Used to determine if two segments are connected
    generator = read_frames(video_path, read_size)
    final_borders = []
    offset = 0

    for frames in generator:
        first_frame = frames[0]
        print(f"Read {len(frames)} frames over")
        borders = slice_frames(frames, ssim_threshold)

        # Check if the last frame of the previous segment is similar to the first frame of the current segment
        if last_frame is not None and ssim(first_frame, last_frame) >= ssim_threshold:
            final_borders.pop()

        final_borders.extend(b + offset for b in borders)
        offset += read_size
        last_frame = frames[-1]

    last = 0
    filtered_borders = []

    # Filter borders based on the minimum interval
    for item in final_borders:
        if item - last < min_interval:
            continue
        else:
            last = item
            filtered_borders.append(item)

    print(filtered_borders)

    frames_to_video(video_path, filtered_borders, output_path)


if __name__ == '__main__':
    read_size = 500
    min_interval = 100  # Set the minimum interval value
    ssim_threshold = 0.50  # Set the threshold for SSIM
    video_path = "test_input/test.mp4"
    output_path = "test_output"
    segment_scenes(video_path, read_size, min_interval, ssim_threshold, output_path)


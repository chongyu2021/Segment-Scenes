# Video Scene Detection and Segmentation

This script is designed to detect different scenes in a video and segment it into different clips. The detection is performed using Structural Similarity (SSIM) between frames. If the SSIM value falls below a specified threshold, a new scene is identified.

## Requirements

- Python 3.x
- OpenCV (`cv2`)
- Scikit-Image (`skimage`)

## Installation

```
pip install opencv-python scikit-image
```

## Function Arguments

--`video_path`: Path to the input video file.

--`read_size`: Number of frames to read in each batch (default: 500).

--`min_interval`: Minimum interval between scene borders (default: 200).

--`ssim_threshold`: SSIM threshold for scene change detection (default: 0.50).

--`output_path`: Directory to save the segmented clips.





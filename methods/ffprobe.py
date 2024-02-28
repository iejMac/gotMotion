import os
import subprocess

def compression_estimator(file_path):
    # Get frame data and stream information using ffprobe
    frame_command = f"ffprobe -show_frames -v error -select_streams v:0 {file_path}"
    stream_command = f"ffprobe -show_streams -v error -select_streams v:0 {file_path}"

    frame_result = subprocess.run(frame_command, shell=True, text=True, capture_output=True)
    stream_result = subprocess.run(stream_command, shell=True, text=True, capture_output=True)

    frame_output = frame_result.stdout.splitlines()
    stream_output = stream_result.stdout.splitlines()

    # Initialize variables
    frame_sizes = {'P': [], 'B': [], 'I': []}
    current_frame_type = None
    video_duration = None

    for line in frame_output:
        if 'pict_type=' in line:
            current_frame_type = line.split('=')[-1]
        elif 'pkt_size=' in line and current_frame_type:
            size = int(line.split('=')[-1])
            frame_sizes[current_frame_type].append(size)
            current_frame_type = None

    for line in stream_output:
        if 'duration=' in line:
            video_duration = float(line.split('=')[-1])

    c = len(frame_sizes['P']) + len(frame_sizes['B']) + len(frame_sizes['I'])
    avg_sizes = {k: sum(v) / c if v else 0 for k, v in frame_sizes.items()}

    # Calculate motion estimate
    motion = (avg_sizes['B'] ** 2) * avg_sizes['I'] / video_duration

    return motion

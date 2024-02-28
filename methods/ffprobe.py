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


# NOTE: used for finding the best compression "features"
def compression_features(file_path):
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
    frame_rate = None
    video_height = None
    video_width = None
    video_duration = None

    # Parse frame output
    for line in frame_output:
        if 'pict_type=' in line:
            current_frame_type = line.split('=')[-1]
        elif 'pkt_size=' in line and current_frame_type:
            size = int(line.split('=')[-1])
            frame_sizes[current_frame_type].append(size)
            current_frame_type = None

    # Parse stream output for frame rate, video dimensions, and duration
    for line in stream_output:
        if 'avg_frame_rate=' in line:
            frame_rate_str = line.split('=')[-1]
            if '/' in frame_rate_str:
                num, denom = map(int, frame_rate_str.split('/'))
                frame_rate = num / denom if denom != 0 else 0
        elif 'height=' in line:
            video_height = int(line.split('=')[-1])
        elif 'width=' in line:
            video_width = int(line.split('=')[-1])
        elif 'duration=' in line:
            video_duration = float(line.split('=')[-1])

    l = len(frame_sizes['P']) + len(frame_sizes['B']) + len(frame_sizes['I'])
    avg_sizes = {k: sum(v) / l if v else 0 for k, v in frame_sizes.items()}
    frame_counts = {k: len(v) if v else 0 for k, v in frame_sizes.items()}

    file_size = os.path.getsize(file_path)

    tot_fc = video_duration * frame_rate

    # Prepare the return vector
    motion_data = {
        'frame_rate': frame_rate,
        'video_height': video_height,
        'video_width': video_width,
        'video_duration': video_duration,
        'file_size': file_size,
        'total_frame_count': tot_fc,
    }
    for k, fc in frame_counts.items():
      motion_data[f"{k}_frame_count"] = fc
    for k, fc in avg_sizes.items():
      motion_data[f"{k}_avg_size"] = fc

    return motion_data

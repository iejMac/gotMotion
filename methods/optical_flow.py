# based on https://docs.opencv.org/4.x/d4/dee/tutorial_optical_flow.html
import cv2 as cv
import numpy as np


def dense_OF(file_path, downsample_factor=1, target_fps=-1):
    cap = cv.VideoCapture(file_path)
    fps = cap.get(cv.CAP_PROP_FPS)
    frame_skip = 1 if target_fps == -1 else round(fps / target_fps)

    ret, frame1 = cap.read()
    if not ret:
        return None

    frame1 = cv.resize(frame1, (frame1.shape[1] // downsample_factor, frame1.shape[0] // downsample_factor)) if downsample_factor != 1 else frame1
    prvs = cv.cvtColor(frame1, cv.COLOR_BGR2GRAY)
    mags, frame_count = [], 0

    while True:
        ret, frame2 = cap.read()
        if not ret:
            break
        frame_count += 1
        if frame_count % frame_skip != 0:
            continue

        frame2 = cv.resize(frame2, (frame2.shape[1] // downsample_factor, frame2.shape[0] // downsample_factor)) if downsample_factor != 1 else frame2
        next = cv.cvtColor(frame2, cv.COLOR_BGR2GRAY)
        flow = cv.calcOpticalFlowFarneback(prvs, next, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag = np.mean(cv.cartToPolar(flow[..., 0], flow[..., 1])[0])
        mags.append(mag)
        prvs = next

    return np.mean(mags)


def sparse_OF(file_path):
    cap = cv.VideoCapture(file_path)
    # Parameters for ShiTomasi corner detection
    feature_params = dict(maxCorners=100,
                          qualityLevel=0.3,
                          minDistance=7,
                          blockSize=7)
    # Parameters for Lucas-Kanade optical flow
    lk_params = dict(winSize=(15, 15),
                     maxLevel=2,
                     criteria=(cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))

    # Take the first frame and find corners in it
    ret, old_frame = cap.read()
    old_gray = cv.cvtColor(old_frame, cv.COLOR_BGR2GRAY)
    p0 = cv.goodFeaturesToTrack(old_gray, mask=None, **feature_params)

    motion_estimates = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        # Calculate optical flow
        p1, st, err = cv.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)

        # Select good points
        if p1 is not None and st is not None:
            good_new = p1[st == 1]
            good_old = p0[st == 1]

            # Calculate motion vectors
            motion_vectors = good_new - good_old
            magnitudes = np.linalg.norm(motion_vectors, axis=1)
            motion_estimates.append(np.mean(magnitudes))

        # Now update the previous frame and previous points
        old_gray = frame_gray.copy()
        if p1 is not None:
            p0 = good_new.reshape(-1, 1, 2)

    return np.mean(motion_estimates)

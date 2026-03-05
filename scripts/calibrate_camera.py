#!/usr/bin/env python3
"""
Camera calibration script using OpenCV.
Move checkerboard in front of camera from different angles.
Press 'c' to capture a frame, 'q' to quit and compute calibration.
Need at least 15-20 good captures for accurate results.

Author: Meet Jain
"""

import cv2
import numpy as np
import os
import yaml

# checkerboard dimensions (inner corners)
CHECKERBOARD = (9, 6)
SQUARE_SIZE  = 0.025  # 25mm in meters

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# 3D points of checkerboard corners in real world
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0],
                        0:CHECKERBOARD[1]].T.reshape(-1, 2)
objp *= SQUARE_SIZE

objpoints = []  # 3D points
imgpoints = []  # 2D points in image
captures  = 0

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

os.makedirs("scripts/calibration_imgs", exist_ok=True)

print("=" * 50)
print(" Camera Calibration")
print("=" * 50)
print(" Hold checkerboard in front of camera")
print(" Press 'c' to capture frame")
print(" Press 'q' to finish and compute calibration")
print(f" Need at least 15 captures (have: {captures})")
print("=" * 50)

while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Cannot read from camera")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    found, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

    display = frame.copy()
    if found:
        # refine corner positions
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        cv2.drawChessboardCorners(display, CHECKERBOARD, corners2, found)
        cv2.putText(display, "CHECKERBOARD DETECTED - Press 'c' to capture",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    else:
        cv2.putText(display, "No checkerboard found",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    cv2.putText(display, f"Captures: {captures}/15",
                (10, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    cv2.imshow("Calibration", display)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('c') and found:
        objpoints.append(objp)
        imgpoints.append(corners2)
        captures += 1
        cv2.imwrite(f"scripts/calibration_imgs/capture_{captures}.png", frame)
        print(f"[INFO] Captured {captures}/15")

    elif key == ord('q'):
        if captures < 10:
            print(f"[WARN] Only {captures} captures — need at least 10")
        else:
            break

cap.release()
cv2.destroyAllWindows()

if captures >= 10:
    print("\n[INFO] Computing calibration...")
    h, w = frame.shape[:2]
    ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, (w, h), None, None)

    print(f"\n=== Calibration Results ===")
    print(f"RMS reprojection error: {ret:.4f} px  (good if < 1.0)")
    print(f"\nCamera Matrix K:")
    print(K)
    print(f"\nDistortion coefficients:")
    print(dist)

    # save as YAML for ORB-SLAM3
    calib = {
        "Camera.fx": float(K[0, 0]),
        "Camera.fy": float(K[1, 1]),
        "Camera.cx": float(K[0, 2]),
        "Camera.cy": float(K[1, 2]),
        "Camera.k1": float(dist[0, 0]),
        "Camera.k2": float(dist[0, 1]),
        "Camera.p1": float(dist[0, 2]),
        "Camera.p2": float(dist[0, 3]),
        "Camera.width":  w,
        "Camera.height": h,
        "Camera.fps":    30,
        "RMS_error":     float(ret)
    }

    out_path = "scripts/camera_calibration.yaml"
    with open(out_path, 'w') as f:
        yaml.dump(calib, f, default_flow_style=False)

    print(f"\n[INFO] Calibration saved to {out_path}")
    print("[INFO] Use these values in your ORB-SLAM3 config!")
else:
    print("[ERROR] Not enough captures for calibration")

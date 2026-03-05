#!/bin/bash
# -------------------------------------------------------
# Run ORB-SLAM3 live with laptop webcam (monocular)
# Author: Meet Jain
# -------------------------------------------------------

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SLAM_DIR="$PROJECT_ROOT/ORB_SLAM3"
VOCAB="$SLAM_DIR/Vocabulary/ORBvoc.txt"
CONFIG="$PROJECT_ROOT/config/webcam_orbslam3.yaml"

export LD_LIBRARY_PATH=$SLAM_DIR/lib:$SLAM_DIR/Thirdparty/DBoW2/lib:$SLAM_DIR/Thirdparty/g2o/lib:$LD_LIBRARY_PATH

echo "Starting live webcam SLAM..."
"$SLAM_DIR/Examples/Monocular/mono_webcam" "$VOCAB" "$CONFIG"

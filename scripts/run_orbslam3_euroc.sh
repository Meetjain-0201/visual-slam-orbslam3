#!/bin/bash
# -------------------------------------------------------
# Run ORB-SLAM3 on EuRoC Machine Hall sequences
# Supports: mono, stereo modes
# Usage: ./scripts/run_orbslam3_euroc.sh [mono|stereo] [sequence]
# Example: ./scripts/run_orbslam3_euroc.sh stereo MH01
# Author: Meet Jain
# -------------------------------------------------------

set -e

# --- paths ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SLAM_DIR="$PROJECT_ROOT/ORB_SLAM3"
DATASET_DIR="$PROJECT_ROOT/datasets/EuRoC"
RESULTS_DIR="$PROJECT_ROOT/results"

VOCAB="$SLAM_DIR/Vocabulary/ORBvoc.txt"

# --- args ---
MODE=${1:-stereo}
SEQ=${2:-MH01}

# map sequence name to folder name
declare -A SEQ_MAP
SEQ_MAP["MH01"]="MH_01_easy"
SEQ_MAP["MH02"]="MH_02_easy"
SEQ_MAP["MH03"]="MH_03_medium"
SEQ_MAP["MH04"]="MH_04_difficult"
SEQ_MAP["MH05"]="MH_05_difficult"

SEQ_FOLDER=${SEQ_MAP[$SEQ]}
if [ -z "$SEQ_FOLDER" ]; then
    echo "[ERROR] Unknown sequence: $SEQ"
    echo "Valid options: MH01 MH02 MH03 MH04 MH05"
    exit 1
fi

SEQ_PATH="$DATASET_DIR/$SEQ_FOLDER"
if [ ! -d "$SEQ_PATH" ]; then
    echo "[ERROR] Dataset not found at: $SEQ_PATH"
    echo "Please download EuRoC dataset first"
    exit 1
fi

mkdir -p "$RESULTS_DIR"
RESULT_FILE="$RESULTS_DIR/${SEQ}_${MODE}_trajectory.txt"

echo "========================================"
echo " ORB-SLAM3 EuRoC Runner"
echo "========================================"
echo " Mode     : $MODE"
echo " Sequence : $SEQ ($SEQ_FOLDER)"
echo " Dataset  : $SEQ_PATH"
echo " Output   : $RESULT_FILE"
echo "========================================"

# --- run ---
if [ "$MODE" == "mono" ]; then
    CONFIG="$SLAM_DIR/Examples/Monocular/EuRoC.yaml"
    TIMESTAMPS="$SLAM_DIR/Examples/Monocular/EuRoC_TimeStamps/${SEQ}.txt"
    EXEC="$SLAM_DIR/Examples/Monocular/mono_euroc"

    "$EXEC" "$VOCAB" "$CONFIG" "$SEQ_PATH" "$TIMESTAMPS" "$RESULT_FILE"

elif [ "$MODE" == "stereo" ]; then
    CONFIG="$SLAM_DIR/Examples/Stereo/EuRoC.yaml"
    TIMESTAMPS="$SLAM_DIR/Examples/Stereo/EuRoC_TimeStamps/${SEQ}.txt"
    EXEC="$SLAM_DIR/Examples/Stereo/stereo_euroc"

    "$EXEC" "$VOCAB" "$CONFIG" "$SEQ_PATH" "$TIMESTAMPS" "$RESULT_FILE"

else
    echo "[ERROR] Unknown mode: $MODE. Use mono or stereo"
    exit 1
fi

echo ""
echo "[INFO] Done! Trajectory saved to $RESULT_FILE"
echo "[INFO] Run evaluation with:"
echo "  python3 scripts/evaluate_trajectory.py -e $RESULT_FILE -g $SEQ_PATH/mav0/state_groundtruth_estimate0/data.csv -s $SEQ"

#!/usr/bin/env python3
"""
Trajectory evaluation script for ORB-SLAM3 results.
Computes ATE (Absolute Trajectory Error) and RPE (Relative Pose Error)
against EuRoC ground truth using the evo library.

Author: Meet Jain
"""

import os
import sys
import argparse
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate ORB-SLAM3 trajectory against ground truth"
    )
    parser.add_argument(
        "--estimated", "-e",
        required=True,
        help="Path to estimated trajectory file (TUM format)"
    )
    parser.add_argument(
        "--groundtruth", "-g",
        required=True,
        help="Path to ground truth file (EuRoC CSV format)"
    )
    parser.add_argument(
        "--sequence", "-s",
        default="MH01",
        help="Sequence name for labeling results (default: MH01)"
    )
    parser.add_argument(
        "--output", "-o",
        default="results/",
        help="Output directory for plots and metrics"
    )
    return parser.parse_args()


def check_dependencies():
    """Check if evo evaluation library is installed."""
    try:
        import evo
        return True
    except ImportError:
        print("[ERROR] evo library not found.")
        print("Install with: pip install evo")
        return False


def load_tum_trajectory(filepath):
    """
    Load a trajectory in TUM format.
    Each line: timestamp tx ty tz qx qy qz qw
    """
    timestamps, positions = [], []
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            vals = line.strip().split()
            if len(vals) < 8:
                continue
            timestamps.append(float(vals[0]))
            # store x, y, z position only for quick stats
            positions.append([float(vals[1]),
                               float(vals[2]),
                               float(vals[3])])
    return np.array(timestamps), np.array(positions)


def print_trajectory_stats(timestamps, positions, label="Trajectory"):
    """Print basic statistics about a loaded trajectory."""
    duration = timestamps[-1] - timestamps[0]
    n_frames = len(timestamps)
    path_length = np.sum(np.linalg.norm(
        np.diff(positions, axis=0), axis=1))

    print(f"\n--- {label} Stats ---")
    print(f"  Frames    : {n_frames}")
    print(f"  Duration  : {duration:.2f} s")
    print(f"  Path len  : {path_length:.3f} m")


def main():
    args = parse_args()

    if not check_dependencies():
        sys.exit(1)

    # lazy import after dependency check
    from evo.tools import file_interface
    from evo.core import metrics, trajectory, sync
    from evo.tools import plot as evo_plot
    import matplotlib.pyplot as plt

    os.makedirs(args.output, exist_ok=True)

    print(f"[INFO] Loading estimated trajectory: {args.estimated}")
    traj_est = file_interface.read_tum_trajectory_file(args.estimated)

    print(f"[INFO] Loading ground truth: {args.groundtruth}")
    traj_ref = file_interface.read_euroc_csv_trajectory(args.groundtruth)

    # sync trajectories by timestamp
    traj_ref, traj_est = sync.associate_trajectories(traj_ref, traj_est)
    print(f"[INFO] Synced {len(traj_est.positions_xyz)} pose pairs")

    # align estimated trajectory to ground truth (Umeyama alignment)
    traj_est_aligned = trajectory.align_trajectory(
        traj_est, traj_ref, correct_scale=False)

    # compute ATE (Absolute Trajectory Error)
    ate_metric = metrics.APE(metrics.PoseRelation.translation_part)
    ate_metric.process_data((traj_ref, traj_est_aligned))
    ate_stats = ate_metric.get_all_statistics()

    print(f"\n=== ATE Results for {args.sequence} ===")
    print(f"  RMSE  : {ate_stats['rmse']:.4f} m")
    print(f"  Mean  : {ate_stats['mean']:.4f} m")
    print(f"  Median: {ate_stats['median']:.4f} m")
    print(f"  Std   : {ate_stats['std']:.4f} m")
    print(f"  Max   : {ate_stats['max']:.4f} m")

    # save metrics to file
    results_file = os.path.join(args.output, f"{args.sequence}_ate.txt")
    with open(results_file, 'w') as f:
        f.write(f"Sequence: {args.sequence}\n")
        for k, v in ate_stats.items():
            f.write(f"{k}: {v:.6f}\n")
    print(f"\n[INFO] Metrics saved to {results_file}")

    # plot trajectory comparison
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.plot(traj_ref.positions_xyz[:, 0],
            traj_ref.positions_xyz[:, 1],
            'b-', label='Ground Truth', linewidth=1.5)
    ax.plot(traj_est_aligned.positions_xyz[:, 0],
            traj_est_aligned.positions_xyz[:, 1],
            'r--', label='ORB-SLAM3', linewidth=1.5)
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_title(f'Trajectory Comparison - {args.sequence}')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')

    plot_file = os.path.join(args.output, f"{args.sequence}_trajectory.png")
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    print(f"[INFO] Plot saved to {plot_file}")
    plt.show()


if __name__ == "__main__":
    main()

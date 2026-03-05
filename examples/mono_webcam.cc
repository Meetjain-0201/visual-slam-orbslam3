/**
 * Live monocular SLAM using laptop webcam.
 * Captures frames from /dev/video0 and feeds them to ORB-SLAM3.
 * Author: Meet Jain
 */

#include <iostream>
#include <chrono>
#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/highgui.hpp>
#include "System.h"

int main(int argc, char **argv)
{
    if (argc != 3) {
        std::cerr << "Usage: mono_webcam <vocabulary> <config>\n";
        return 1;
    }

    // open default webcam
    cv::VideoCapture cap(0);
    if (!cap.isOpened()) {
        std::cerr << "[ERROR] Cannot open webcam\n";
        return 1;
    }

    cap.set(cv::CAP_PROP_FRAME_WIDTH,  640);
    cap.set(cv::CAP_PROP_FRAME_HEIGHT, 480);
    cap.set(cv::CAP_PROP_FPS,          30);

    // init ORB-SLAM3 in monocular mode
    ORB_SLAM3::System SLAM(argv[1], argv[2],
                           ORB_SLAM3::System::MONOCULAR, true);

    std::cout << "\n[INFO] Webcam SLAM started. Press 'q' to quit.\n";

    cv::Mat frame;
    auto t_start = std::chrono::steady_clock::now();

    while (true) {
        cap >> frame;
        if (frame.empty()) {
            std::cerr << "[ERROR] Empty frame\n";
            break;
        }

        // compute timestamp in seconds from start
        auto now = std::chrono::steady_clock::now();
        double t = std::chrono::duration<double>(now - t_start).count();

        // feed frame to SLAM
        SLAM.TrackMonocular(frame, t);

        // quit on 'q'
        if (cv::waitKey(1) == 'q')
            break;
    }

    SLAM.Shutdown();
    SLAM.SaveKeyFrameTrajectoryTUM("results/webcam_trajectory.txt");
    std::cout << "[INFO] Trajectory saved.\n";

    cap.release();
    return 0;
}

import cv2
import mediapipe as mp
import numpy as np
import os

def analyze_swing(video_path, output_dir, club_type="iron"):
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return "Error: Cannot open video.", None

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    output_path = os.path.join(output_dir, 'annotated_swing.mp4')
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'avc1'), fps, (width, height))

    shoulder_angles = []
    wrist_heights = []
    shoulder_levels = []

    club_targets = {
        "driver": {
            "shoulder_turn_min": 85,
            "wrist_arc_min": 0.1,
            "shoulder_level_max": 0.08,
            "tips": {
                "shoulder_rotation": "Your shoulder turn is too shallow — rotate more to generate coil and power.",
                "wrist_arc": "Wrist arc is compact — work on extending your hands away from your body on the backswing.",
                "shoulder_level": "You’re tilting too much laterally — keep your shoulders more level to avoid swaying."
            }
        },
        "iron": {
            "shoulder_turn_min": 75,
            "wrist_arc_min": 0.07,
            "shoulder_level_max": 0.08,
            "tips": {
                "shoulder_rotation": "Lack of shoulder rotation — rotate your lead shoulder under your chin on the backswing.",
                "wrist_arc": "Wrist arc appears restricted — improve your extension for more consistent ball-striking.",
                "shoulder_level": "Uneven shoulders — stay centered and resist collapsing your trail side."
            }
        },
        "wedge": {
            "shoulder_turn_min": 60,
            "wrist_arc_min": 0.04,
            "shoulder_level_max": 0.08,
            "tips": {
                "shoulder_rotation": "You’re rotating too little — even with wedges, maintain rotational control for spin.",
                "wrist_arc": "Wrist motion is too tight — allow soft hinge and controlled unhinge.",
                "shoulder_level": "Inconsistent shoulder height — avoid collapsing your upper body during the swing."
            }
        },
        "putter": {
            "shoulder_turn_min": 0,
            "wrist_arc_min": 0,
            "shoulder_level_max": 0,
            "tips": {
                "putting": "Maintain a pendulum motion, led by the shoulders — no wrist breakdown."
            }
        }
    }

    club_data = club_targets.get(club_type, club_targets["iron"])

    if club_type != "putter":
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, smooth_landmarks=True) as pose:
            frame_count = 0
            frame_step = 2 if fps > 30 else 1
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % frame_step != 0:
                    frame_count += 1
                    continue

                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = pose.process(image)

                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                    landmarks = results.pose_landmarks.landmark

                    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
                    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
                    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
                    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]

                    dx = left_shoulder.x - right_shoulder.x
                    dy = left_shoulder.y - right_shoulder.y
                    angle = np.degrees(np.arctan2(dy, dx))
                    shoulder_angles.append(angle)

                    wrist_heights.append((left_wrist.y + right_wrist.y) / 2)
                    shoulder_levels.append(abs(left_shoulder.y - right_shoulder.y))

                out.write(image)
                frame_count += 1

        cap.release()
        out.release()

    report = f"📊 SWING ANALYSIS REPORT ({club_type.upper()})\n"
    faults = []

    if club_type == "putter":
        report += "\n🧘 Putter Stroke Analysis:\n"
        for key, tip in club_data["tips"].items():
            report += f"  💡 {tip}\n"
        return report, 'annotated_swing.mp4'

    if shoulder_angles:
        r = max(shoulder_angles) - min(shoulder_angles)
        report += f"\n🧍 Shoulder Rotation Range: {r:.2f}°\n"
        if r < club_data["shoulder_turn_min"]:
            faults.append(("Limited Shoulder Rotation", club_data['tips']['shoulder_rotation']))
        else:
            faults.append(("Good Shoulder Turn", None))
    else:
        report += "❌ Could not track shoulders.\n"

    if wrist_heights:
        w_range = max(wrist_heights) - min(wrist_heights)
        report += f"\n🖐 Wrist Arc Vertical Range: {w_range:.3f}\n"
        if w_range < club_data["wrist_arc_min"]:
            faults.append(("Compact Wrist Arc", club_data['tips']['wrist_arc']))
        else:
            faults.append(("Good Wrist Extension", None))
    else:
        report += "❌ Could not track wrists.\n"

    if shoulder_levels:
        avg_level = sum(shoulder_levels) / len(shoulder_levels)
        report += f"\n📋 Shoulder Plane Balance: {avg_level:.3f} (L-R deviation)\n"
        if avg_level > club_data["shoulder_level_max"]:
            faults.append(("Excessive Shoulder Tilt", club_data['tips']['shoulder_level']))
        else:
            faults.append(("Balanced Shoulder Plane", None))

    report += "\n🎯 Final Coaching Insights (Tailored):\n"
    for issue, tip in faults:
        if tip:
            report += f"  ❌ {issue}: {tip}\n"
        else:
            report += f"  ✅ {issue}: Great job, keep doing this!\n"

    return report, 'annotated_swing.mp4'

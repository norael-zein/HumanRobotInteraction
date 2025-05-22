import cv2
import time
import mediapipe as mp
from furhat_remote_api import FurhatRemoteAPI

"""
Gaze tracking during the interview with the emotional robot

"""
def start_gaze_tracking(furhat):
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(
        model_selection=0, 
        min_detection_confidence=0.6
    )
    cap = cv2.VideoCapture(0)

    prev_pan = 0
    prev_tilt = 0
    alpha = 0.2 

    def get_gaze_direction(detection):
        bbox = detection.location_data.relative_bounding_box
        x_center = bbox.xmin + bbox.width / 2
        y_center = bbox.ymin + bbox.height / 2

        #Left and right
        pan = (0.5 - x_center) * 60
        pan = max(min(pan, 30), -30)

        #Tilt up and down
        tilt = (y_center - 0.5) * 30
        tilt = max(min(tilt, 15), -15)

        return pan, tilt

    def user_present(frame):
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(image_rgb)
        if results.detections:
            return True, results.detections[0]
        return False, None

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            found, detection = user_present(frame)
            if found:
                pan_angle, tilt_angle = get_gaze_direction(detection)

                smoothed_pan = (1 - alpha) * prev_pan + alpha * pan_angle
                smoothed_tilt = (1 - alpha) * prev_tilt + alpha * tilt_angle

                prev_pan = smoothed_pan
                prev_tilt = smoothed_tilt

                furhat.gesture(body={
                    "frames": [
                        {
                            "time": [0.33],
                            "params": {
                                "NECK_PAN": smoothed_pan,
                                "NECK_TILT": smoothed_tilt
                            },
                            "persist": True
                        }
                    ],
                    "class": "furhatos.gestures.Gesture"
                })

            time.sleep(0.1)

    except Exception as e:
        print("Gaze tracking error:", e)

    finally:
        cap.release()
        face_detection.close()
        cv2.destroyAllWindows()


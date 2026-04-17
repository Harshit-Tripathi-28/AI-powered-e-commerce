import cv2
import mediapipe as mp
import numpy as np
from .utils import overlay_transparent

mp_pose = mp.solutions.pose
mp_selfie = mp.solutions.selfie_segmentation

def apply_clothes(user_image_path, cloth_image_path, output_path):

    image = cv2.imread(user_image_path)
    cloth = cv2.imread(cloth_image_path, cv2.IMREAD_UNCHANGED)

    if image is None or cloth is None:
        return False

    h, w, _ = image.shape

    with mp_pose.Pose(static_image_mode=True) as pose, \
         mp_selfie.SelfieSegmentation(model_selection=1) as segmenter:

        pose_results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not pose_results.pose_landmarks:
            return False

        seg_results = segmenter.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        mask = (seg_results.segmentation_mask > 0.5).astype(np.uint8)

        landmarks = pose_results.pose_landmarks.landmark

        # Shoulder & Hip points
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        left_hip = landmarks[23]
        right_hip = landmarks[24]

        x1 = int(left_shoulder.x * w)
        x2 = int(right_shoulder.x * w)

        y_shoulder = int(left_shoulder.y * h)
        y_hip = int((left_hip.y + right_hip.y) / 2 * h)

        shoulder_width = abs(x2 - x1)
        torso_height = abs(y_hip - y_shoulder)

        # Clean scaling (stable)
        cloth_width = int(shoulder_width * 1.35)
        cloth_height = int(torso_height * 1.4)

        center_x = int((x1 + x2) / 2)

        x = int(center_x - cloth_width / 2)
        y = int(y_shoulder + (0.02 * h))

        # Resize cloth
        cloth_resized = cv2.resize(
            cloth,
            (cloth_width, cloth_height),
            interpolation=cv2.INTER_AREA
        )

        # Overlay
        result = overlay_transparent(image.copy(), cloth_resized, x, y)

        # Apply body mask (so cloth not on background)
        for c in range(3):
            result[:, :, c] = result[:, :, c] * mask + image[:, :, c] * (1 - mask)

        cv2.imwrite(output_path, result)

        return True

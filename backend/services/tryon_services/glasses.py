import cv2
import mediapipe as mp
from .utils import overlay_transparent

mp_face_mesh = mp.solutions.face_mesh

def apply_glasses(user_image_path, glasses_image_path, output_path):
    image = cv2.imread(user_image_path)
    glasses = cv2.imread(glasses_image_path, cv2.IMREAD_UNCHANGED)

    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5
    ) as face_mesh:

        result = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if not result.multi_face_landmarks:
            return False

        landmarks = result.multi_face_landmarks[0]

        h, w, _ = image.shape

        # Eye landmarks
        left_eye = landmarks.landmark[33]
        right_eye = landmarks.landmark[263]

        x1 = int(left_eye.x * w)
        x2 = int(right_eye.x * w)
        y1 = int(left_eye.y * h)

        eye_width = abs(x2 - x1)

        glasses_width = int(eye_width * 2)
        glasses_height = int(glasses_width * 0.5)

        x = int((x1 + x2) / 2 - glasses_width / 2)
        y = int(y1 - glasses_height / 2)

        result_img = overlay_transparent(
            image, glasses, x, y, (glasses_width, glasses_height)
        )

        cv2.imwrite(output_path, result_img)

        return True

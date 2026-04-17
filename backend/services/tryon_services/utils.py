import cv2
import numpy as np

def overlay_transparent(background, overlay, x, y, size=None):

    bg_h, bg_w = background.shape[:2]

    if size is not None:
        overlay = cv2.resize(overlay, size, interpolation=cv2.INTER_AREA)

    h, w = overlay.shape[:2]

    # Boundary safety check
    if x >= bg_w or y >= bg_h:
        return background

    if x + w > bg_w:
        w = bg_w - x
        overlay = overlay[:, :w]

    if y + h > bg_h:
        h = bg_h - y
        overlay = overlay[:h]

    if overlay.shape[2] < 4:
        return background

    # Separate color and alpha channels
    overlay_rgb = overlay[:, :, :3]
    alpha_mask = overlay[:, :, 3] / 255.0

    # Smooth alpha edges
    alpha_mask = cv2.GaussianBlur(alpha_mask, (5, 5), 0)

    # Region of interest
    roi = background[y:y+h, x:x+w]

    # Blend
    for c in range(3):
        roi[:, :, c] = (
            alpha_mask * overlay_rgb[:, :, c] +
            (1 - alpha_mask) * roi[:, :, c]
        )

    background[y:y+h, x:x+w] = roi

    return background

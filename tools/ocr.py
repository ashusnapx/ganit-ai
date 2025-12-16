from paddleocr import PaddleOCR
import cv2
import numpy as np
from PIL import Image
import os

os.environ["FLAGS_allocator_strategy"] = "auto_growth"

# Initialize OCR engines once (performance)
PRINTED_OCR = PaddleOCR(use_angle_cls=True, lang="en")
HANDWRITTEN_OCR = PaddleOCR(
    use_angle_cls=True,
    lang="en",
    det_db_box_thresh=0.3,
    det_db_unclip_ratio=2.0
)

def detect_handwritten(image_path: str) -> bool:
    """
    Heuristic-based handwriting detection.
    Uses edge density + noise patterns.
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    edges = cv2.Canny(img, 50, 150)

    edge_density = np.sum(edges > 0) / edges.size

    # Handwritten text generally has irregular strokes
    return edge_density > 0.08


def run_ocr(image_path: str) -> dict:
    is_handwritten = detect_handwritten(image_path)
    ocr_engine = HANDWRITTEN_OCR if is_handwritten else PRINTED_OCR

    result = ocr_engine.ocr(image_path)

    extracted_text = []
    confidences = []

    if result and result[0]:
        for line in result[0]:
            try:
                content = line[1]

                # Case 1: (text, confidence)
                if isinstance(content, (list, tuple)) and len(content) == 2:
                    text, confidence = content

                # Case 2: only text returned
                elif isinstance(content, str):
                    text = content
                    confidence = 0.5  # fallback heuristic

                else:
                    continue

                extracted_text.append(text)
                confidences.append(confidence)

            except Exception:
                continue  # skip corrupted lines safely

    avg_confidence = (
        sum(confidences) / len(confidences)
        if confidences else 0.0
    )

    return {
        "text": "\n".join(extracted_text),
        "confidence": round(avg_confidence, 3),
        "ocr_type": "handwritten" if is_handwritten else "printed"
    }

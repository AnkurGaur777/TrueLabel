import pytesseract
from PIL import Image
import cv2
import numpy as np
import io

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Prepare a photo of a nutrition label for OCR:
    1. Convert to grayscale (color info isn't needed for text, and it simplifies everything after)
    2. Upscale if the image is small (OCR does better on larger text)
    3. Apply adaptive thresholding (converts to clean black/white, handles
       uneven lighting/shadows much better than a single global threshold)
    4. Denoise slightly to clean up JPEG artifacts
    """
    file_bytes = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    height, width = gray.shape
    if width < 1000:
        scale = 1000 / width
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    denoised = cv2.fastNlMeansDenoising(gray, h=10)

    thresh = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=31,
        C=15,
    )

    return thresh

def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Take raw image bytes, preprocess for better OCR accuracy, run OCR,
    and return the raw extracted text.
    """
    processed = preprocess_image(image_bytes)
    pil_image = Image.fromarray(processed)
    raw_text = pytesseract.image_to_string(pil_image, config="--psm 6")
    return raw_text

import pytesseract
from PIL import Image
import cv2
import numpy as np
import io

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Prepare a photo of a nutrition label for OCR, tuned to preserve small
    details like decimal points that a naive pipeline tends to blur away:
    1. Grayscale
    2. Upscale more aggressively (1500px target width) so small characters
       like decimal points have more pixels to survive thresholding
    3. CLAHE contrast enhancement (boosts local contrast unevenly lit areas,
       better than a single global contrast adjustment for angled/shadowed photos)
    4. Bilateral filter instead of simple denoising (smooths noise while
       preserving sharp edges -- critical for keeping small dots/decimals intact)
    5. Adaptive thresholding to clean black/white
    """
    file_bytes = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    height, width = gray.shape
    if width < 1500:
        scale = 1500 / width
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    contrasted = clahe.apply(gray)

    smoothed = cv2.bilateralFilter(contrasted, d=9, sigmaColor=75, sigmaSpace=75)

    thresh = cv2.adaptiveThreshold(
        smoothed, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=31,
        C=15,
    )

    return thresh

def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Preprocess the image, then run OCR with two different page-segmentation
    modes and return whichever result contains more digits -- tabular nutrition
    labels sometimes parse better under psm 4 (variable-sized text column) than
    psm 6 (uniform block), and picking the digit-richer result is a simple way
    to automatically favor whichever mode did better on this particular photo.
    """
    processed = preprocess_image(image_bytes)
    pil_image = Image.fromarray(processed)

    text_psm6 = pytesseract.image_to_string(pil_image, config="--psm 6")
    text_psm4 = pytesseract.image_to_string(pil_image, config="--psm 4")

    digit_count_6 = sum(c.isdigit() for c in text_psm6)
    digit_count_4 = sum(c.isdigit() for c in text_psm4)

    return text_psm6 if digit_count_6 >= digit_count_4 else text_psm4

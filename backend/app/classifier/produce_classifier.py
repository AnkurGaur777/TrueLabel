from transformers import AutoModelForImageClassification, AutoImageProcessor
from PIL import Image
import torch
import io

MODEL_NAME = "jazzmacedo/fruits-and-vegetables-detector-36"

_model = None
_processor = None

def _load_model():
    """Lazy-load the model on first use, not at import time, so the API
    starts up fast and only pays the model-loading cost when /classify is
    actually called for the first time."""
    global _model, _processor
    if _model is None:
        _processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
        _model = AutoModelForImageClassification.from_pretrained(MODEL_NAME)
        _model.eval()
    return _model, _processor

def classify_produce(image_bytes: bytes, top_k: int = 3):
    """
    Classify a photo of raw produce into one of 36 fruit/vegetable categories.
    Returns the top_k most likely labels with confidence scores.
    """
    model, processor = _load_model()

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=-1)[0]

    top_probs, top_indices = torch.topk(probabilities, top_k)

    results = []
    for prob, idx in zip(top_probs, top_indices):
        label = model.config.id2label[idx.item()]
        results.append({
            "label": label,
            "confidence": round(prob.item(), 4),
        })

    return results

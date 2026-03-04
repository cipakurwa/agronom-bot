import logging
from PIL import Image
import torch
from transformers import MobileNetV2ImageProcessor, AutoModelForImageClassification

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_model = None
_processor = None
_id2label = None


def load_model(model_name: str, token: str):
    global _model, _processor, _id2label
    if _model is not None:
        return _model, _processor

    logger.info("⏳ Загрузка image processor (MobileNetV2ImageProcessor, use_fast=False)...")
    # Явно используем класс MobileNetV2ImageProcessor с отключением fast
    _processor = MobileNetV2ImageProcessor.from_pretrained(model_name, token=token, use_fast=False)

    logger.info("⏳ Загрузка модели...")
    _model = AutoModelForImageClassification.from_pretrained(model_name, token=token)

    _id2label = _model.config.id2label
    logger.info(f"✅ Модель загружена, количество классов: {len(_id2label)}")

    return _model, _processor


def predict(image_bytes, model_name, token):
    model, processor = load_model(model_name, token)

    image = Image.open(image_bytes).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.nn.functional.softmax(logits, dim=-1).squeeze()

    top_probs, top_indices = torch.topk(probs, k=3)

    predictions = []
    for prob, idx in zip(top_probs, top_indices):
        label = _id2label[idx.item()]
        predictions.append({
            "class": label,
            "confidence": prob.item()
        })

    return predictions

import sys
import os
import io

import grpc
import torch
from torch import softmax
from PIL import Image
from transformers import AutoModelForImageClassification, ViTImageProcessor
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import generated.classifier_pb2 as nsfw_pb2
    import generated.classifier_pb2_grpc as nsfw_pb2_grpc
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "Unable to import generated protobuf modules from src/generated."
    ) from exc


class NSFWClassifier(nsfw_pb2_grpc.NSFWClassifierServicer):
    def __init__(self, model_name: str, threshold: float):
        print(f"Initializing NSFWClassifier with model={model_name}", flush=True)
        self.model = AutoModelForImageClassification.from_pretrained(model_name)
        self.processor = ViTImageProcessor.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.threshold = threshold
        self.model.to(self.device)
        self.model.eval()
        self.model.requires_grad_(False)
    
    def ClassifyImage(self, request, context):
        image_bytes = request.image_data
        print(f"ClassifyImage called, bytes={len(image_bytes)}", flush=True)

        if not image_bytes:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("image_data is required and cannot be empty")
            return nsfw_pb2.ClassificationResponse()

        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as exc:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"invalid image_data payload: {exc}")
            return nsfw_pb2.ClassificationResponse()

        inputs = self.processor(images=image, return_tensors="pt")
        inputs = inputs.to(self.device)
        outputs = self.model(**inputs)
        logits = outputs.logits
        probs = softmax(logits, dim=1)
        probs = probs.detach().cpu().numpy()
        probs = probs[0]
        nsfw_confidence = float(probs[1])
        is_nsfw = nsfw_confidence >= self.threshold
        print(
            f"class_probs={{sfw:{float(probs[0]):.6f}, nsfw:{nsfw_confidence:.6f}}}, threshold={self.threshold}",
            flush=True,
        )

        return nsfw_pb2.ClassificationResponse(
            isnsfw=is_nsfw,
            confidence=nsfw_confidence,
            is_allowed=not is_nsfw,
        )
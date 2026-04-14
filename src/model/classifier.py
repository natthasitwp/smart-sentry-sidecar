import sys
import os
import io

import torch
from torch import sigmoid
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
    def __init__(self):
        self.model = AutoModelForImageClassification.from_pretrained("Falconsai/nsfw_image_detection")
        self.processor = ViTImageProcessor.from_pretrained('Falconsai/nsfw_image_detection')
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()
        self.model.requires_grad_(False)
    
    def ClassifyImage(self, request, context):
        image = Image.open(io.BytesIO(request.image_data))
        inputs = self.processor(images=image, return_tensors="pt")
        inputs = inputs.to(self.device)
        outputs = self.model(**inputs)
        logits = outputs.logits
        probs = sigmoid(logits)
        probs = probs.detach().cpu().numpy()
        probs = probs[0]

        return nsfw_pb2.ClassificationResponse(
            isnsfw=probs[1] > 0.5,
            confidence=probs[1],
            is_allowed=probs[1] > 0.5,
        )
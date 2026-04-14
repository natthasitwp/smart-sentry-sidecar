import grpc
from concurrent import futures

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import generated.classifier_pb2 as nsfw_pb2
    import generated.classifier_pb2_grpc as nsfw_pb2_grpc
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "Unable to import generated protobuf modules from src/generated."
    ) from exc



class NSFWClassifier(nsfw_pb2_grpc.NSFWClassifierServicer):
    def ClassifyImage(self, request, context):
        print(f"Received image, size: {len(request.image_data)} bytes")

        return nsfw_pb2.ClassificationResponse(
            isnsfw=False,
            confidence=0.15,
            is_allowed=True,
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    nsfw_pb2_grpc.add_NSFWClassifierServicer_to_server(NSFWClassifier(), server)
    
    # เปิด Port 50051
    server.add_insecure_port('[::]:50051')
    print("NSFW gRPC Server is running on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
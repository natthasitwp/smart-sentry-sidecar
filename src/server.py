import grpc
from concurrent import futures
import generated.classifier_pb2_grpc as nsfw_pb2_grpc
from config.loader import load_config
from model.classifier import NSFWClassifier

def serve():
    config = load_config()
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=config.server.max_workers)
    )
    nsfw_pb2_grpc.add_NSFWClassifierServicer_to_server(
        NSFWClassifier(
            model_name=config.model.name,
            threshold=config.model.threshold,
        ),
        server,
    )

    server.add_insecure_port(f"[::]:{config.server.port}")
    print(f"gRPC Server is running on port {config.server.port} with {config.server.max_workers} workers", flush=True)
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
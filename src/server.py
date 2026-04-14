import grpc
from concurrent import futures
import generated.classifier_pb2_grpc as nsfw_pb2_grpc
from model.classifier import NSFWClassifier

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    nsfw_pb2_grpc.add_NSFWClassifierServicer_to_server(NSFWClassifier(), server)
    
    # เปิด Port 50051
    server.add_insecure_port('[::]:50051')
    print("NSFW gRPC Server is running on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
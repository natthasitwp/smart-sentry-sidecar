# Smart Sentry: AI Inference Sidecar (Python)

This service acts as the high-performance "brain" of the Smart Sentry system. It is a dedicated gRPC server designed to ingest image streams from the Go Gateway and perform real-time content classification using Deep Learning.

## 🧠 Role in Architecture
The sidecar exists to isolate heavy computational tasks from the main API. By running in a separate process (or container), it ensures that 100% GPU/CPU utilization during a scan does not lead to dropped connections or timeouts in the user-facing Go service.

## 🛠 Features
* **gRPC Server:** Implementation of the `Scanner` service defined in `smartsentry.proto`.
* **Model Warm-up:** AI models (MobileNetV3/YOLOv10) are loaded into memory at startup to eliminate cold-start latency.
* **Stream Reconstruction:** Efficiently reassembles 32KB chunks into a contiguous byte array for processing.
* **Tensor Optimization:** Utilizes **ONNX Runtime** or **TorchScript** for faster inference compared to standard Python execution.

## 📋 Technical Requirements
* Python 3.10+
* `grpcio` & `grpcio-tools`
* `Pillow` (PIL) or `OpenCV`
* `torch` or `onnxruntime`

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install grpcio grpcio-tools torch torchvision pillow
```

### 2. Generate gRPC Stubs
Run this from the `sidecar/` directory:
```bash
python -m grpc_tools.protoc -I../proto --python_out=. --grpc_python_out=. ../proto/smartsentry.proto
```

### 3. Run the Server
```bash
python main.py
```

## 🛠 Implementation Details

### Stream Handling
The server implements the `ScanImage` RPC by iterating over the `request_iterator`. This allows the model to begin preparation as soon as the first packet arrives.
```python
def ScanImage(self, request_iterator, context):
    data = bytearray()
    for chunk in request_iterator:
        data.extend(chunk.data)
    
    # Process the completed byte array
    result = self.model.predict(data)
    return smartsentry_pb2.ScanResponse(is_safe=result.is_safe, ...)
```

### Environment Variables
| Variable | Description | Default |
| :--- | :--- | :--- |
| `GRPC_PORT` | The port the sidecar listens on | `50051` |
| `MODEL_PATH` | Path to the weights file (.pth / .onnx) | `./models/weights.onnx` |
| `CONFIDENCE_THRESHOLD` | Sensitivity of the AI scan | `0.75` |

## 🐳 Dockerization
The sidecar is packaged using a specialized image to support hardware acceleration:
* **CPU:** `python:3.10-slim`
* **GPU:** `nvidia/cuda:12.1.0-base-ubuntu22.04` (with Python installed)

---
**Develop By:** Natthasit Wongprang
# Smart Sentry Sidecar (Python)

Python gRPC sidecar for image NSFW classification using Hugging Face model
`Falconsai/nsfw_image_detection`.

## What This Service Does

- Exposes a unary gRPC endpoint: `NSFWClassifier/ClassifyImage`
- Accepts raw image bytes (`image_data`) and optional extension (`file_ext`)
- Runs inference with `transformers` + `torch`
- Returns:
  - `isnsfw` (bool)
  - `confidence` (float, NSFW class probability)
  - `is_allowed` (bool, opposite of `isnsfw`)

## Project Structure

- `src/server.py` - gRPC server bootstrap
- `src/model/classifier.py` - NSFW model loading + inference handler
- `src/config/loader.py` - YAML configuration loader/validator
- `configs/config.yaml` - default runtime configuration
- `protos/classifier.proto` - protobuf service/messages
- `src/generated/` - generated gRPC Python stubs
- `tests/client.py` - test client for two sample images in `inputs/`

## Requirements

- Python `>=3.11`
- Dependencies are declared in `pyproject.toml`:
  - `grpcio`
  - `grpcio-tools`
  - `pillow`
  - `pyyaml`
  - `torch`
  - `torchvision`
  - `transformers`

## Install

Using `uv` (recommended):

```bash
uv sync
```

Or with `pip`:

```bash
pip install -e .
```

## Configuration

By default, the service reads `configs/config.yaml`.

Example:

```yaml
server:
  port: 50051
  max_workers: 10

model:
  name: "Falconsai/nsfw_image_detection"
  threshold: 0.75
```

You can override config path with environment variable:

```bash
export SMART_SENTRY_CONFIG=/path/to/config.yaml
```

Validation rules:

- `server.port > 0`
- `server.max_workers > 0`
- `0.0 <= model.threshold <= 1.0`

## Run Server

From project root:

```bash
python src/server.py
```

The server starts on configured port and prints startup logs.

## gRPC API

Defined in `protos/classifier.proto`:

- Service: `nsfw_filter.NSFWClassifier`
- RPC: `ClassifyImage(ImageRequest) returns (ClassificationResponse)`

Messages:

- `ImageRequest`
  - `bytes image_data`
  - `string file_ext`
- `ClassificationResponse`
  - `bool isnsfw`
  - `float confidence`
  - `bool is_allowed`

## Test With Sample Images

Make sure server is running, then execute:

```bash
python tests/client.py
```

Optional target:

```bash
python tests/client.py --target localhost:50051
```

The script sends:

- `inputs/sfw-sample.jpeg`
- `inputs/nsfw-sample.jpeg`

and prints classification results for each image.
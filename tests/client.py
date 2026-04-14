from __future__ import annotations

from pathlib import Path
import argparse
import sys

import grpc

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from generated import classifier_pb2, classifier_pb2_grpc


def classify_image(
    stub: classifier_pb2_grpc.NSFWClassifierStub, image_path: Path
) -> classifier_pb2.ClassificationResponse:
    image_bytes = image_path.read_bytes()
    request = classifier_pb2.ImageRequest(
        image_data=image_bytes,
        file_ext=image_path.suffix.lower(),
    )
    return stub.ClassifyImage(request)


def run_test(target: str) -> int:
    image_paths = [
        ROOT_DIR / "inputs" / "sfw-sample.jpeg",
        ROOT_DIR / "inputs" / "nsfw-sample.jpeg",
    ]

    missing_paths = [path for path in image_paths if not path.exists()]
    if missing_paths:
        print("Missing required test images:")
        for path in missing_paths:
            print(f" - {path}")
        return 1

    with grpc.insecure_channel(target) as channel:
        stub = classifier_pb2_grpc.NSFWClassifierStub(channel)
        for image_path in image_paths:
            try:
                response = classify_image(stub, image_path)
            except grpc.RpcError as exc:
                print(
                    f"{image_path.name}: RPC failed "
                    f"({exc.code().name}) {exc.details()}"
                )
                return 1

            print(
                f"{image_path.name}: "
                f"is_nsfw={response.isnsfw}, "
                f"confidence={response.confidence:.4f}, "
                f"is_allowed={response.is_allowed}"
            )

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Test NSFW gRPC classifier with two sample images."
    )
    parser.add_argument(
        "--target",
        default="localhost:50051",
        help="gRPC server address (default: localhost:50051)",
    )
    args = parser.parse_args()
    return run_test(args.target)


if __name__ == "__main__":
    raise SystemExit(main())

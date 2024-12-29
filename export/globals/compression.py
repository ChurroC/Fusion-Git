import json
import base64
import zlib


def compress_json(data):
    """Compress JSON data using zlib with maximum compression."""
    json_str = json.dumps(data, separators=(",", ":"))
    compressed = zlib.compress(json_str.encode(), level=9)
    return base64.b64encode(compressed).decode()


def decompress_json(compressed_str):
    """Decompress a zlib-compressed JSON string back to data."""
    decoded = base64.b64decode(compressed_str)
    json_str = zlib.decompress(decoded).decode()
    return json.loads(json_str)

import io
import numpy as np
import torch


def encode_tensor(tensor: torch.Tensor) -> bytes:
    """Serialize a tensor to safe binary bytes (no pickle, no code execution risk)."""
    arr = tensor.detach().cpu().numpy()
    buf = io.BytesIO()
    np.save(buf, arr, allow_pickle=False)
    return buf.getvalue()


def decode_tensor(blob: bytes) -> torch.Tensor:
    """Deserialize bytes back into a tensor. Raises if the blob isn't a valid,
    non-pickled numpy array — this is what makes it safe against malicious blobs."""
    buf = io.BytesIO(blob)
    arr = np.load(buf, allow_pickle=False)
    return torch.from_numpy(arr)
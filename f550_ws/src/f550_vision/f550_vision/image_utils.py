"""Convert raw ROS image fields to NumPy arrays and back, without ROS or cv_bridge.

cv_bridge in ROS 2 Humble is built against NumPy 1.x and breaks when a pip
package such as ultralytics pulls NumPy 2. These helpers only need NumPy.
"""

import numpy as np

SUPPORTED_ENCODINGS = ('rgb8', 'bgr8')
_CHANNELS = 3


def image_fields_to_bgr(data, width, height, step, encoding):
    """Return a writable BGR uint8 array of shape (height, width, 3).

    ``data`` is the ``data`` field of a ``sensor_msgs/Image``; ``step`` is its
    row length in bytes and may be larger than ``width * 3`` because of padding.
    """
    if encoding not in SUPPORTED_ENCODINGS:
        raise ValueError(
            f'unsupported encoding {encoding!r}; expected one of {SUPPORTED_ENCODINGS}')
    row_bytes = width * _CHANNELS
    if width <= 0 or height <= 0 or step < row_bytes:
        raise ValueError('inconsistent image size or step')
    try:
        buffer = np.frombuffer(data, dtype=np.uint8)   # bytes, bytearray, array.array
    except TypeError:
        buffer = np.asarray(data, dtype=np.uint8)      # plain list of ints
    if buffer.size != step * height:
        raise ValueError(
            f'data has {buffer.size} bytes, expected {step * height}')
    pixels = buffer.reshape(height, step)[:, :row_bytes].reshape(height, width, _CHANNELS)
    if encoding == 'rgb8':
        pixels = pixels[:, :, ::-1]
    return np.array(pixels, dtype=np.uint8, order='C')


def bgr_to_image_fields(frame):
    """Return ``(data, width, height, step, encoding)`` for a BGR uint8 frame."""
    frame = np.asarray(frame)
    if frame.ndim != 3 or frame.shape[2] != _CHANNELS or frame.dtype != np.uint8:
        raise ValueError('frame must be a uint8 array of shape (height, width, 3)')
    height, width = frame.shape[:2]
    data = np.ascontiguousarray(frame).tobytes()
    return data, width, height, width * _CHANNELS, 'bgr8'

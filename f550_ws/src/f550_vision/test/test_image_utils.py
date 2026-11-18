"""Unit tests for the NumPy-only image conversion helpers."""

import array

import numpy as np
import pytest

from f550_vision.image_utils import bgr_to_image_fields, image_fields_to_bgr


def _rgb_bytes():
    """Return a 2x2 RGB image: red, green / blue, white."""
    return bytes([255, 0, 0, 0, 255, 0, 0, 0, 255, 255, 255, 255])


def test_rgb_is_converted_to_bgr():
    """The channel order is reversed for rgb8 input."""
    frame = image_fields_to_bgr(_rgb_bytes(), 2, 2, 6, 'rgb8')
    assert frame.shape == (2, 2, 3)
    assert frame[0, 0].tolist() == [0, 0, 255]
    assert frame[1, 0].tolist() == [255, 0, 0]


def test_bgr_is_kept():
    """bgr8 input is returned unchanged."""
    frame = image_fields_to_bgr(_rgb_bytes(), 2, 2, 6, 'bgr8')
    assert frame[0, 0].tolist() == [255, 0, 0]


def test_row_padding_is_discarded():
    """A step larger than width * 3 drops the padding bytes."""
    padded = bytes([1, 2, 3, 4, 5, 6, 99, 99, 7, 8, 9, 10, 11, 12, 99, 99])
    frame = image_fields_to_bgr(padded, 2, 2, 8, 'bgr8')
    assert frame.reshape(-1).tolist() == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]


def test_array_array_input_and_writable_result():
    """ROS delivers array.array data; the result must be writable."""
    data = array.array('B', _rgb_bytes())
    frame = image_fields_to_bgr(data, 2, 2, 6, 'bgr8')
    frame[0, 0, 0] = 7
    assert frame[0, 0, 0] == 7


def test_plain_list_input():
    """A list of ints is accepted as well."""
    frame = image_fields_to_bgr(list(_rgb_bytes()), 2, 2, 6, 'bgr8')
    assert frame[1, 1].tolist() == [255, 255, 255]


@pytest.mark.parametrize('args', [
    (_rgb_bytes(), 2, 2, 6, 'mono8'),
    (_rgb_bytes(), 2, 2, 5, 'rgb8'),
    (_rgb_bytes()[:-1], 2, 2, 6, 'rgb8'),
    (_rgb_bytes(), 0, 2, 6, 'rgb8'),
])
def test_invalid_input_is_rejected(args):
    """Unsupported encodings and inconsistent sizes raise ValueError."""
    with pytest.raises(ValueError):
        image_fields_to_bgr(*args)


def test_round_trip():
    """Converting back to ROS fields keeps the pixels."""
    frame = image_fields_to_bgr(_rgb_bytes(), 2, 2, 6, 'rgb8')
    data, width, height, step, encoding = bgr_to_image_fields(frame)
    assert (width, height, step, encoding) == (2, 2, 6, 'bgr8')
    assert np.frombuffer(data, dtype=np.uint8).tolist() == frame.reshape(-1).tolist()


def test_bgr_to_fields_rejects_bad_frames():
    """Only uint8 height x width x 3 arrays are accepted."""
    with pytest.raises(ValueError):
        bgr_to_image_fields(np.zeros((2, 2), dtype=np.uint8))
    with pytest.raises(ValueError):
        bgr_to_image_fields(np.zeros((2, 2, 3), dtype=np.float32))

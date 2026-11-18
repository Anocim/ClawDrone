"""Unit tests for turning detector output into detection records."""

import numpy as np
import pytest

from f550_vision.detections import build_detections, parse_labels

NAMES = {0: 'ball', 1: 'cone'}


def test_parse_labels():
    """Labels are split on commas and stripped; empty text means no filter."""
    assert parse_labels('ball, cone ,') == frozenset({'ball', 'cone'})
    assert parse_labels('') == frozenset()


def test_detections_are_sorted_by_score():
    """The most confident detection comes first."""
    found = build_detections(
        [[10, 20, 4, 5], [30, 40, 6, 7]], [0.5, 0.9], [0, 0], NAMES)
    assert [item.score for item in found] == [0.9, 0.5]
    assert found[0].center_x == 30.0 and found[0].height == 7.0
    assert found[0].label == 'ball'


def test_label_filter():
    """Only the requested labels are kept."""
    found = build_detections(
        np.array([[1, 1, 2, 2], [3, 3, 2, 2]]), np.array([0.8, 0.7]),
        np.array([0.0, 1.0]), NAMES, frozenset({'cone'}))
    assert [item.label for item in found] == ['cone']


def test_names_may_be_a_list_and_unknown_ids_fall_back():
    """Class names can come from a list; unknown ids use their number."""
    found = build_detections([[1, 1, 2, 2], [2, 2, 2, 2]], [0.6, 0.5], [0, 7], ['ball'])
    assert [item.label for item in found] == ['ball', '7']


def test_empty_input():
    """No boxes give no detections."""
    assert build_detections(np.zeros((0, 4)), np.zeros(0), np.zeros(0), NAMES) == []


def test_length_mismatch_is_rejected():
    """Boxes, scores and class ids must line up."""
    with pytest.raises(ValueError):
        build_detections([[1, 1, 2, 2]], [0.5, 0.6], [0], NAMES)

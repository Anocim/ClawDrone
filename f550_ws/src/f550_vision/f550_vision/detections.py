"""Turn raw detector output into plain, ROS-independent detection records."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Detection:
    """One detected object, in pixels of the processed image."""

    center_x: float
    center_y: float
    width: float
    height: float
    score: float
    class_id: int
    label: str


def parse_labels(text):
    """Split a comma-separated string into a set of labels (empty means all)."""
    return frozenset(item.strip() for item in text.split(',') if item.strip())


def _label_for(names, class_id):
    """Look a class name up in a dict or a list, falling back to the number."""
    if isinstance(names, dict):
        return str(names.get(class_id, class_id))
    if 0 <= class_id < len(names):
        return str(names[class_id])
    return str(class_id)


def build_detections(xywh, scores, class_ids, names, labels=frozenset()):
    """Build detections from center/size boxes, scores and class ids.

    Detections whose label is not in ``labels`` are dropped unless ``labels``
    is empty. The result is sorted from the highest to the lowest score.
    """
    xywh = np.asarray(xywh, dtype=float).reshape(-1, 4)
    scores = np.asarray(scores, dtype=float).reshape(-1)
    class_ids = np.asarray(class_ids).reshape(-1)
    if not len(xywh) == len(scores) == len(class_ids):
        raise ValueError('boxes, scores and class ids must have the same length')
    detections = []
    for box, score, class_id in zip(xywh, scores, class_ids):
        class_id = int(class_id)
        label = _label_for(names, class_id)
        if labels and label not in labels:
            continue
        detections.append(Detection(
            center_x=float(box[0]), center_y=float(box[1]),
            width=float(box[2]), height=float(box[3]),
            score=float(score), class_id=class_id, label=label))
    return sorted(detections, key=lambda detection: detection.score, reverse=True)

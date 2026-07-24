from difflib import SequenceMatcher
from typing import List, Tuple, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.ingest.canonical import CanonicalObject

class MatchResult(BaseModel):
    obj_a: Optional[CanonicalObject] = None
    obj_b: Optional[CanonicalObject] = None
    score: float = 0.0
    tag_score: float = 0.0
    iou_score: float = 0.0
    text_score: float = 0.0
    type_score: float = 0.0

def calculate_iou(bbox_a: List[float], bbox_b: List[float]) -> float:
    """Calculate Intersection over Union (IoU) of two bounding boxes [x0, y0, x1, y1]."""
    ax0, ay0, ax1, ay1 = bbox_a
    bx0, by0, bx1, by1 = bbox_b

    inter_x0 = max(ax0, bx0)
    inter_y0 = max(ay0, by0)
    inter_x1 = min(ax1, bx1)
    inter_y1 = min(ay1, by1)

    inter_w = max(0.0, inter_x1 - inter_x0)
    inter_h = max(0.0, inter_y1 - inter_y0)
    inter_area = inter_w * inter_h

    area_a = max(0.0, ax1 - ax0) * max(0.0, ay1 - ay0)
    area_b = max(0.0, bx1 - bx0) * max(0.0, by1 - by0)

    union_area = area_a + area_b - inter_area
    if union_area <= 0:
        return 0.0
    return inter_area / union_area

def calculate_text_similarity(text_a: str, text_b: str) -> float:
    """Calculate string similarity ratio."""
    return SequenceMatcher(None, text_a.lower(), text_b.lower()).ratio()

class WeightedMatcher:
    """
    Weighted scoring matcher for engineering document comparison.
    Score = 0.40 * TagMatch + 0.25 * IoU + 0.20 * TextSim + 0.15 * TypeSim
    """

    def __init__(
        self,
        weight_tag: float = 0.40,
        weight_iou: float = 0.25,
        weight_text: float = 0.20,
        weight_type: float = 0.15,
        match_threshold: float = 0.45
    ):
        self.w_tag = weight_tag
        self.w_iou = weight_iou
        self.w_text = weight_text
        self.w_type = weight_type
        self.threshold = match_threshold

    def compute_pair_score(self, a: CanonicalObject, b: CanonicalObject) -> MatchResult:
        # Tag score
        tag_score = 0.0
        if a.is_tagged() and b.is_tagged():
            tag_score = 1.0 if a.tag.strip().upper() == b.tag.strip().upper() else 0.0

        # Spatial IoU score
        iou_score = 0.0
        if a.page == b.page:
            iou_score = calculate_iou(a.bbox, b.bbox)

        # Text similarity score
        text_score = calculate_text_similarity(a.text, b.text)

        # Type similarity score
        type_score = 1.0 if a.type == b.type else 0.0

        total_score = (
            self.w_tag * tag_score +
            self.w_iou * iou_score +
            self.w_text * text_score +
            self.w_type * type_score
        )

        return MatchResult(
            obj_a=a,
            obj_b=b,
            score=total_score,
            tag_score=tag_score,
            iou_score=iou_score,
            text_score=text_score,
            type_score=type_score
        )

    def match(
        self,
        objs_a: List[CanonicalObject],
        objs_b: List[CanonicalObject]
    ) -> Tuple[List[MatchResult], List[CanonicalObject], List[CanonicalObject]]:
        """
        Greedy bipartite matching based on weighted score matrix.
        Returns: (matched_pairs, unmatched_a, unmatched_b)
        """
        all_pairs: List[MatchResult] = []

        for a in objs_a:
            for b in objs_b:
                pair = self.compute_pair_score(a, b)
                if pair.score >= self.threshold:
                    all_pairs.append(pair)

        # Sort pairs by highest match score
        all_pairs.sort(key=lambda x: x.score, reverse=True)

        matched_pairs: List[MatchResult] = []
        used_a = set()
        used_b = set()

        for pair in all_pairs:
            id_a = pair.obj_a.id
            id_b = pair.obj_b.id
            if id_a not in used_a and id_b not in used_b:
                matched_pairs.append(pair)
                used_a.add(id_a)
                used_b.add(id_b)

        unmatched_a = [a for a in objs_a if a.id not in used_a]
        unmatched_b = [b for b in objs_b if b.id not in used_b]

        return matched_pairs, unmatched_a, unmatched_b

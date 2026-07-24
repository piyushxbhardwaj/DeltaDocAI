from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from src.ingest.canonical import CanonicalObject, ObjectType
from src.delta.matcher import WeightedMatcher, MatchResult

ChangeType = Literal["Added", "Removed", "Modified", "Unchanged"]

class DeltaItem(BaseModel):
    id: str
    change_type: ChangeType
    object_type: ObjectType
    tag: Optional[str] = None
    description: str
    page_a: Optional[int] = None
    page_b: Optional[int] = None
    bbox_a: Optional[List[float]] = None
    bbox_b: Optional[List[float]] = None
    text_a: Optional[str] = None
    text_b: Optional[str] = None
    confidence: float
    details: Dict[str, Any] = Field(default_factory=dict)

class DeltaResult(BaseModel):
    summary: Dict[str, int]
    overall_confidence: float
    items: List[DeltaItem]

class DeltaComparator:
    """Calculates granular engineering document deltas."""

    def __init__(self, matcher: Optional[WeightedMatcher] = None):
        self.matcher = matcher or WeightedMatcher()

    def compare(
        self,
        doc_a: List[CanonicalObject],
        doc_b: List[CanonicalObject]
    ) -> DeltaResult:
        matched_pairs, unmatched_a, unmatched_b = self.matcher.match(doc_a, doc_b)
        delta_items: List[DeltaItem] = []

        # Process matched pairs (Check for Modified vs Unchanged)
        for pair in matched_pairs:
            a = pair.obj_a
            b = pair.obj_b
            
            # Check if text, type, or position modified
            text_changed = a.text.strip() != b.text.strip()
            type_changed = a.type != b.type
            bbox_changed = pair.iou_score < 0.85

            if text_changed or type_changed or bbox_changed:
                desc_parts = []
                if text_changed:
                    desc_parts.append(f"Text updated from '{a.text}' to '{b.text}'")
                if type_changed:
                    desc_parts.append(f"Type reclassified from '{a.type}' to '{b.type}'")
                if bbox_changed:
                    desc_parts.append("Coordinates/Position moved")
                
                desc = f"{a.type} '{a.tag or a.text}' modified: " + "; ".join(desc_parts)

                delta_items.append(DeltaItem(
                    id=f"mod-{a.id}-{b.id}",
                    change_type="Modified",
                    object_type=b.type,
                    tag=b.tag or a.tag,
                    description=desc,
                    page_a=a.page,
                    page_b=b.page,
                    bbox_a=a.bbox,
                    bbox_b=b.bbox,
                    text_a=a.text,
                    text_b=b.text,
                    confidence=round(pair.score, 2),
                    details={"text_changed": text_changed, "type_changed": type_changed}
                ))
            else:
                delta_items.append(DeltaItem(
                    id=f"unc-{a.id}-{b.id}",
                    change_type="Unchanged",
                    object_type=a.type,
                    tag=a.tag,
                    description=f"{a.type} '{a.tag or a.text}' remains unchanged.",
                    page_a=a.page,
                    page_b=b.page,
                    bbox_a=a.bbox,
                    bbox_b=b.bbox,
                    text_a=a.text,
                    text_b=b.text,
                    confidence=1.0
                ))

        # Process Removed (in A, missing in B)
        for a in unmatched_a:
            delta_items.append(DeltaItem(
                id=f"rem-{a.id}",
                change_type="Removed",
                object_type=a.type,
                tag=a.tag,
                description=f"{a.type} '{a.tag or a.text}' was removed from Revision B.",
                page_a=a.page,
                bbox_a=a.bbox,
                text_a=a.text,
                confidence=round(a.confidence, 2)
            ))

        # Process Added (in B, missing in A)
        for b in unmatched_b:
            delta_items.append(DeltaItem(
                id=f"add-{b.id}",
                change_type="Added",
                object_type=b.type,
                tag=b.tag,
                description=f"{b.type} '{b.tag or b.text}' was added in Revision B.",
                page_b=b.page,
                bbox_b=b.bbox,
                text_b=b.text,
                confidence=round(b.confidence, 2)
            ))

        # Summary calculations
        counts = {
            "total_changes": sum(1 for item in delta_items if item.change_type != "Unchanged"),
            "added": sum(1 for item in delta_items if item.change_type == "Added"),
            "removed": sum(1 for item in delta_items if item.change_type == "Removed"),
            "modified": sum(1 for item in delta_items if item.change_type == "Modified"),
            "unchanged": sum(1 for item in delta_items if item.change_type == "Unchanged"),
        }

        conf_values = [item.confidence for item in delta_items]
        overall_conf = round(sum(conf_values) / max(1, len(conf_values)), 2)

        return DeltaResult(
            summary=counts,
            overall_confidence=overall_conf,
            items=delta_items
        )

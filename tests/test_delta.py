from src.ingest.canonical import CanonicalObject
from src.delta.matcher import WeightedMatcher, calculate_iou
from src.delta.comparator import DeltaComparator

def test_iou_calculation():
    box_a = [0.0, 0.0, 10.0, 10.0]
    box_b = [5.0, 0.0, 15.0, 10.0]
    iou = calculate_iou(box_a, box_b)
    assert 0.3 < iou < 0.4

def test_weighted_matcher_exact_tag():
    a = CanonicalObject(id="1", type="Instrument", tag="26-PIT-9055", text="100 PSI", page=1, bbox=[0,0,10,10])
    b = CanonicalObject(id="2", type="Instrument", tag="26-PIT-9055", text="150 PSI", page=1, bbox=[0,0,10,10])
    
    matcher = WeightedMatcher()
    res = matcher.compute_pair_score(a, b)
    assert res.tag_score == 1.0
    assert res.score >= 0.75

def test_delta_comparator():
    doc_a = [
        CanonicalObject(id="1", type="Valve", tag="V-102", text="V-102 Valve", page=1, bbox=[10,10,20,20]),
        CanonicalObject(id="2", type="Instrument", tag="PIT-1", text="10 PSI", page=1, bbox=[30,30,40,40])
    ]
    doc_b = [
        CanonicalObject(id="3", type="Instrument", tag="PIT-1", text="20 PSI", page=1, bbox=[30,30,40,40]),
        CanonicalObject(id="4", type="Pipeline", tag="LINE-9", text="Main Line", page=1, bbox=[50,50,60,60])
    ]

    comparator = DeltaComparator()
    result = comparator.compare(doc_a, doc_b)

    assert result.summary["removed"] == 1  # V-102
    assert result.summary["added"] == 1    # LINE-9
    assert result.summary["modified"] == 1 # PIT-1
    assert result.overall_confidence > 0.0

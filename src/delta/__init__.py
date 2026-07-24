"""
Delta Engine module for DeltaDoc AI.
"""
from src.delta.matcher import WeightedMatcher, MatchResult
from src.delta.comparator import DeltaComparator, DeltaItem, DeltaResult
from src.delta.report import DeltaReportGenerator

__all__ = [
    "WeightedMatcher",
    "MatchResult",
    "DeltaComparator",
    "DeltaItem",
    "DeltaResult",
    "DeltaReportGenerator",
]

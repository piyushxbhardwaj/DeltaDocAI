from pydantic import BaseModel
from typing import List, Dict, Any

class GoldenQAPair(BaseModel):
    id: str
    question: str
    ground_truth_answer: str
    expected_citations: List[str]

class GoldenDataset:
    """Standard ground truth dataset for DeltaDoc AI evaluation benchmarks."""

    @staticmethod
    def get_ground_truth_deltas() -> List[Dict[str, Any]]:
        return [
            {"change_type": "Removed", "tag": "V-102", "object_type": "Valve", "page": 1},
            {"change_type": "Modified", "tag": "26-PIT-9055", "object_type": "Instrument", "page": 1, "text_a": "100 PSI", "text_b": "150 PSI"},
            {"change_type": "Added", "tag": '6"-CS-150', "object_type": "Pipeline", "page": 1},
            {"change_type": "Modified", "tag": "C-201", "object_type": "Equipment", "page": 1}
        ]

    @staticmethod
    def get_golden_qa_pairs() -> List[GoldenQAPair]:
        return [
            GoldenQAPair(
                id="qa-1",
                question="Which valves were removed in Revision B?",
                ground_truth_answer="Valve V-102 was removed from Revision B on Page 1.",
                expected_citations=["Revision A", "Delta Report"]
            ),
            GoldenQAPair(
                id="qa-2",
                question="What is the updated pressure value for PIT-9055?",
                ground_truth_answer="The pressure reading for 26-PIT-9055 was updated from 100 PSI to 150 PSI.",
                expected_citations=["Revision B", "Delta Report"]
            ),
            GoldenQAPair(
                id="qa-3",
                question="What new pipeline was added?",
                ground_truth_answer='Pipeline 6"-CS-150 was added in Revision B on Page 1.',
                expected_citations=["Revision B"]
            )
        ]

import pytest
from src.ingest.canonical import CanonicalObject
from src.ingest.dwg import DWGAdapter

@pytest.mark.asyncio
async def test_dwg_adapter():
    adapter = DWGAdapter()
    canonical_list = await adapter.process("sample_drawing.dwg")
    assert len(canonical_list) > 0
    assert isinstance(canonical_list[0], CanonicalObject)
    assert canonical_list[1].tag == "26-PIT-9055"
    assert canonical_list[1].type == "Instrument"

def test_canonical_object_schema():
    obj = CanonicalObject(
        type="Valve",
        tag="V-101",
        text="V-101 Ball Valve",
        page=1,
        bbox=[10.0, 20.0, 50.0, 60.0]
    )
    assert obj.is_tagged() is True
    assert obj.tag == "V-101"
    assert obj.type == "Valve"

import pytest

from app.api.endpoints.pipeline_version import (
    get_pipeline_versions,
    set_pipeline_versions,
)
from app.core.errors import CustomBaseError
from app.data_models.models import PipelineVersionItem
from app.db.schema import CodeVersion, PipelineVersion


def make_pipeline_version(version, position):
    cv = CodeVersion(id=position + 1, version=version)
    pv = PipelineVersion(code_version_id=cv.id, position=position)
    pv.code_version = cv
    return pv


@pytest.mark.unit
@pytest.mark.nondestructive
def test_get_pipeline_versions(mock_session):
    # GIVEN: The DB has two pipeline versions
    pv0 = make_pipeline_version("20260225.221405", 0)
    pv1 = make_pipeline_version("20260224.100000", 1)
    db = mock_session(lambda *_: [pv0, pv1])

    # WHEN: get_pipeline_versions is called
    result = get_pipeline_versions(db=db)

    # THEN: Both versions are returned in order
    assert len(result) == 2
    assert result[0] is pv0
    assert result[1] is pv1


@pytest.mark.unit
@pytest.mark.nondestructive
def test_set_pipeline_versions(mock_session):
    # GIVEN: A valid request with all 3 slots filled
    versions = [
        PipelineVersionItem(position=0, version="20260225.221405"),
        PipelineVersionItem(position=1, version="20260224.100000"),
        PipelineVersionItem(position=2, version="20260223.100000"),
    ]
    db = mock_session()

    # WHEN: set_pipeline_versions is called
    set_pipeline_versions(db=db, versions=versions)

    # THEN: A delete was issued, new versions were added, and it was committed
    assert db.did_commit
    assert not db.did_rollback
    added_pvs = [
        item for item in db.added_items if isinstance(item, PipelineVersion)
    ]
    assert len(added_pvs) == 3
    assert added_pvs[0].position == 0
    assert added_pvs[1].position == 1
    assert added_pvs[2].position == 2


@pytest.mark.unit
@pytest.mark.nondestructive
def test_set_pipeline_versions_rejects_wrong_count(mock_session):
    # GIVEN: A request with fewer than 3 versions
    versions = [
        PipelineVersionItem(position=0, version="20260225.221405"),
        PipelineVersionItem(position=1, version="20260224.100000"),
    ]
    db = mock_session()

    # WHEN/THEN: an error is raised before any DB changes
    with pytest.raises(CustomBaseError, match="Expected 3 versions"):
        set_pipeline_versions(db=db, versions=versions)

    assert not db.did_commit
    assert len(db.added_items) == 0


@pytest.mark.unit
@pytest.mark.nondestructive
def test_set_pipeline_versions_rejects_invalid_positions(mock_session):
    # GIVEN: A request where positions are not exactly {0, 1, 2}
    versions = [
        PipelineVersionItem(position=0, version="20260225.221405"),
        PipelineVersionItem(position=1, version="20260224.100000"),
        PipelineVersionItem(position=3, version="20260223.100000"),  # gap
    ]
    db = mock_session()

    # WHEN/THEN: an error is raised before any DB changes
    with pytest.raises(CustomBaseError, match="Invalid positional values"):
        set_pipeline_versions(db=db, versions=versions)

    assert not db.did_commit
    assert len(db.added_items) == 0


@pytest.mark.unit
@pytest.mark.nondestructive
def test_set_pipeline_versions_rejects_duplicates(mock_session):
    # GIVEN: A request with 3 versions where two share the same version string
    versions = [
        PipelineVersionItem(position=0, version="20260225.221405"),
        PipelineVersionItem(position=1, version="20260225.221405"),  # duplicate
        PipelineVersionItem(position=2, version="20260223.100000"),
    ]
    db = mock_session()

    # WHEN/THEN: an error is raised before any DB changes
    with pytest.raises(CustomBaseError, match="Duplicate version detected"):
        set_pipeline_versions(db=db, versions=versions)

    assert not db.did_commit
    assert not db.did_rollback
    assert len(db.added_items) == 0

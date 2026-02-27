from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.auth import RequiresRole
from app.core.errors import CustomBaseError
from app.data_models.models import PipelineVersionItem, Role
from app.db.schema import PipelineVersion
from app.db.utils import get_db
from app.service.abl import get_or_add_code_version

router = APIRouter()


@router.get("/", response_model=List[PipelineVersionItem])
def get_pipeline_versions(db: Session = Depends(get_db)):
    return db.scalars(
        select(PipelineVersion).order_by(PipelineVersion.position)
    ).all()


@router.put(
    "/",
    response_model=List[PipelineVersionItem],
    dependencies=[Depends(RequiresRole(Role.ADMIN))],
)
def set_pipeline_versions(
    *,
    db: Session = Depends(get_db),
    versions: List[PipelineVersionItem],
):
    if len({v.version for v in versions}) != len(versions):
        raise CustomBaseError("Duplicate version detected")
    try:
        db.execute(delete(PipelineVersion))
        for item in versions:
            code_version = get_or_add_code_version(db, item.version)
            db.add(
                PipelineVersion(
                    code_version_id=code_version.id, position=item.position
                )
            )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return db.scalars(
        select(PipelineVersion).order_by(PipelineVersion.position)
    ).all()

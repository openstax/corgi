from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Events(Base):
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    collection_id = sa.Column(sa.String, index=True)
    status_id = sa.Column(sa.Integer, sa.ForeignKey("status.id"))
    pdf_url = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    status = relationship("Status", back_populates="events")


class Status(Base):
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, index=True)
    updated_at = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow,
                           onupdate=datetime.utcnow, index=True)

    events = relationship("Events", back_populates="status")

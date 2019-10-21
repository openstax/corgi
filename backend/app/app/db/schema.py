from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Events(Base):
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    collection_id = sa.Column(sa.String, index=True)
    status_id = sa.Column(sa.Integer, sa.ForeignKey("status.id"), default=1)
    pdf_url = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    status = relationship("Status", back_populates="events")

    @hybrid_property
    def status_name(self):
        return self.status.name

    @status_name.setter
    def status_name(self, value):
        self.status = value

    @status_name.expression
    def status_name(cls):
        return cls.status

      
class Status(Base):
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, index=True)
    updated_at = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow,
                           onupdate=datetime.utcnow, index=True)

    events = relationship("Events", back_populates="status")

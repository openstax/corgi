from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ContentServers(Base):
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    hostname = sa.Column(sa.String)
    host_url = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    events = relationship("Events", back_populates="content_server")


class Events(Base):
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    collection_id = sa.Column(sa.String, index=True)
    status_id = sa.Column(sa.Integer, sa.ForeignKey("status.id"), default=1)
    pdf_url = sa.Column(sa.String)
    content_server_id = sa.Column(sa.Integer, sa.ForeignKey("content_servers.id"))
    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    status = relationship("Status", back_populates="events", lazy="joined")
    content_server = relationship("ContentServers", back_populates="events", lazy="joined")


class Status(Base):
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, index=True)
    updated_at = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow,
                           onupdate=datetime.utcnow, index=True)

    events = relationship("Events", back_populates="status")

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class JobTypes(Base):
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String, nullable=False)
    display_name = sa.Column(sa.String, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow,
                           index=True)
    updated_at = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    jobs = relationship("Jobs", back_populates="job_type")


class Jobs(Base):
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("user.id"))
    status_id = sa.Column(sa.Integer, sa.ForeignKey("status.id"), default=1)
    job_type_id = sa.Column(sa.Integer, sa.ForeignKey("job_types.id"))
    git_ref = sa.Column(sa.String)
    worker_version = sa.Column(sa.String)
    error_message = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow,
                           index=True)
    updated_at = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    status = relationship("Status", back_populates="jobs", lazy="joined")
    job_type = relationship("JobTypes", back_populates="jobs", lazy="joined")
    user = relationship("User", back_populates="jobs", lazy="joined")
    books = relationship(
        "BookJob",
        back_populates="job",
        lazy="joined",
        order_by="asc(BookJob.book_id)",
    )


class Status(Base):
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, index=True)
    updated_at = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow,
                           onupdate=datetime.utcnow, index=True)

    jobs = relationship("Jobs", back_populates="status")


class Repository(Base):
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String, nullable=False)
    owner = sa.Column(sa.String, nullable=False)

    commits = relationship("Commit", back_populates="repository", lazy="joined")
    users = relationship("UserRepository", back_populates="repository")


class Commit(Base):
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    repository_id = sa.Column(sa.Integer, sa.ForeignKey("repository.id"))
    sha = sa.Column(sa.String, nullable=False)
    timestamp = sa.Column(sa.DateTime, nullable=False)

    repository = relationship("Repository", back_populates="commits", lazy="joined")
    books = relationship("Book", back_populates="commit", lazy="joined")
    # We do not need to store a commit more than once
    __table_args__ = (sa.UniqueConstraint('repository_id', 'sha',
                      name='_repository_commit'),)


class Book(Base):
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    uuid = sa.Column(sa.String(36), index=True, nullable=False)
    commit_id = sa.Column(sa.Integer, sa.ForeignKey("commit.id"), index=True,
                          nullable=False)
    edition = sa.Column(sa.Integer, nullable=False)
    slug = sa.Column(sa.String, nullable=False)
    style = sa.Column(sa.String, nullable=False)

    commit = relationship("Commit", back_populates="books", lazy="joined")
    jobs = relationship("BookJob", back_populates="book")
    __table_args__ = (sa.UniqueConstraint('uuid', 'commit_id',
                      name='_book_to_commit'),)


class User(Base):
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String, nullable=False)
    avatar_url = sa.Column(sa.String, nullable=False)

    jobs = relationship("Jobs", back_populates="user")
    repositories = relationship("UserRepository", back_populates="user")


class BookJob(Base):
    book_id = sa.Column(sa.ForeignKey("book.id"), primary_key=True, index=True)
    job_id = sa.Column(sa.ForeignKey("jobs.id"), primary_key=True, index=True)
    artifact_url = sa.Column(sa.String, nullable=True)
    approved = sa.Column(sa.Boolean, nullable=False, default=False)

    job = relationship("Jobs", back_populates="books", lazy="joined")
    book = relationship("Book", back_populates="jobs", lazy="joined")


class RepositoryPermission(Base):
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String, nullable=False)

    user_repositories = relationship("UserRepository",
                                     back_populates="permission")


class UserRepository(Base):
    user_id = sa.Column(sa.ForeignKey("user.id"), primary_key=True, index=True)
    repository_id = sa.Column(sa.ForeignKey("repository.id"), primary_key=True)
    permission_id = sa.Column(sa.ForeignKey("repository_permission.id"),
                              nullable=False, index=True)

    repository = relationship("Repository", back_populates="users")
    user = relationship("User", back_populates="repositories")
    permission = relationship("RepositoryPermission",
                              back_populates="user_repositories")

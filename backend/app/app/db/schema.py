from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.db.base_class import Base


def utcnow():
    return datetime.now(timezone.utc)


class DateTimeUTC(sa.types.TypeDecorator):
    impl = sa.DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        # If the value does not have a timezone, it is assumed to be utc
        if (
            isinstance(value, datetime)
            and value.tzinfo is not None
            and value.tzinfo.utcoffset(value) is not None
        ):
            # Convert the time to utc (requires timezone), then remove timezone
            # The timezone is implicitly removed when the datetime is stored
            value = value.astimezone(timezone.utc).replace(tzinfo=None)

        return value

    def process_result_value(self, value, dialect):
        # Since we diligently ensured the datetime is stored with utc offset,
        # we can safely force the loaded value to have a utc timezone (if it
        # is a datetime)
        if isinstance(value, datetime):
            value = value.replace(tzinfo=timezone.utc)
        return value


class JobTypes(Base):
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String, nullable=False)
    display_name = sa.Column(sa.String, nullable=False)
    created_at = sa.Column(
        DateTimeUTC,
        nullable=False,
        default=utcnow,
        index=True,
    )
    updated_at = sa.Column(
        DateTimeUTC,
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )

    jobs = relationship("Jobs", back_populates="job_type")


class Jobs(Base):
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("user.id"))
    status_id = sa.Column(sa.Integer, sa.ForeignKey("status.id"), default=1)
    job_type_id = sa.Column(sa.Integer, sa.ForeignKey("job_types.id"))
    git_ref = sa.Column(sa.String)
    worker_version = sa.Column(sa.String)
    error_message = sa.Column(sa.String)
    created_at = sa.Column(
        DateTimeUTC,
        nullable=False,
        default=utcnow,
        index=True,
    )
    updated_at = sa.Column(
        DateTimeUTC,
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )

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
    created_at = sa.Column(DateTimeUTC, default=utcnow, index=True)
    updated_at = sa.Column(
        DateTimeUTC,
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
        index=True,
    )

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
    timestamp = sa.Column(DateTimeUTC, nullable=False)

    repository = relationship(
        "Repository", back_populates="commits", lazy="joined"
    )
    books = relationship("Book", back_populates="commit", lazy="joined")
    # We do not need to store a commit more than once
    __table_args__ = (
        sa.UniqueConstraint("repository_id", "sha", name="_repository_commit"),
    )


class Book(Base):
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    uuid = sa.Column(sa.String(36), index=True, nullable=False)
    commit_id = sa.Column(
        sa.Integer, sa.ForeignKey("commit.id"), index=True, nullable=False
    )
    edition = sa.Column(sa.Integer, nullable=False)
    slug = sa.Column(sa.String, nullable=False)
    style = sa.Column(sa.String, nullable=False)

    commit = relationship("Commit", back_populates="books", lazy="joined")
    jobs = relationship("BookJob", back_populates="book")
    approved_versions = relationship("ApprovedBook", back_populates="book")
    __table_args__ = (
        sa.UniqueConstraint("uuid", "commit_id", name="_book_to_commit"),
    )


class CodeVersion(Base):
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    version = sa.Column(sa.String, nullable=False)
    created_at = sa.Column(DateTimeUTC, default=utcnow, index=True)
    updated_at = sa.Column(
        DateTimeUTC,
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
        index=True,
    )

    approved_versions = relationship(
        "ApprovedBook", back_populates="code_version"
    )


class Consumer(Base):
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String, nullable=False)
    created_at = sa.Column(DateTimeUTC, default=utcnow, index=True)
    updated_at = sa.Column(
        DateTimeUTC,
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
        index=True,
    )

    approved_versions = relationship("ApprovedBook", back_populates="consumer")


class ApprovedBook(Base):
    book_id = sa.Column(sa.ForeignKey("book.id"), index=True, primary_key=True)
    consumer_id = sa.Column(
        sa.ForeignKey("consumer.id"),
        nullable=False,
        index=True,
        primary_key=True,
    )
    code_version_id = sa.Column(
        sa.ForeignKey("code_version.id"),
        nullable=False,
        index=True,
        primary_key=True,
    )
    created_at = sa.Column(DateTimeUTC, default=utcnow, index=True)
    updated_at = sa.Column(
        DateTimeUTC,
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
        index=True,
    )

    book = relationship(
        "Book", back_populates="approved_versions", lazy="joined"
    )
    consumer = relationship(
        "Consumer", back_populates="approved_versions", lazy="joined"
    )
    code_version = relationship(
        "CodeVersion", back_populates="approved_versions", lazy="joined"
    )


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

    job = relationship("Jobs", back_populates="books", lazy="joined")
    book = relationship("Book", back_populates="jobs", lazy="joined")


class RepositoryPermission(Base):
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String, nullable=False)

    user_repositories = relationship(
        "UserRepository", back_populates="permission"
    )


class UserRepository(Base):
    user_id = sa.Column(sa.ForeignKey("user.id"), primary_key=True, index=True)
    repository_id = sa.Column(sa.ForeignKey("repository.id"), primary_key=True)
    permission_id = sa.Column(
        sa.ForeignKey("repository_permission.id"), nullable=False, index=True
    )

    repository = relationship("Repository", back_populates="users")
    user = relationship("User", back_populates="repositories")
    permission = relationship(
        "RepositoryPermission", back_populates="user_repositories"
    )

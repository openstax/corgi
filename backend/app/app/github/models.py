import re
from enum import Enum

from pydantic import BaseModel


def snake_to_camel(s: str):
    return re.sub(r"_[a-z]", lambda match: match.group(0)[-1].upper(), s)


def camel_to_snake(s: str):
    return re.sub(
        r"[a-z][A-Z]",
        lambda match: "_".join(c.lower() for c in match.group(0)),
        s,
    )


class RepositoryPermission(int, Enum):
    ADMIN = 1
    MAINTAIN = 2
    READ = 3
    TRIAGE = 4
    WRITE = 5


class GraphQLModel(BaseModel):
    @classmethod
    def graphql_fields(cls):
        return [snake_to_camel(k) for k in cls.__fields__]

    @classmethod
    def graphql_query(cls):
        return "\n".join(cls.graphql_fields())

    @classmethod
    def from_node(cls, node: dict):
        return cls(**{camel_to_snake(k): v for k, v in node.items()})


class GitHubRepo(GraphQLModel):
    name: str
    database_id: str
    viewer_permission: str
    visibility: str

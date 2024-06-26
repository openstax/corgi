from enum import Enum

from pydantic import BaseModel


class RepositoryPermission(int, Enum):
    ADMIN = 1
    MAINTAIN = 2
    READ = 3
    TRIAGE = 4
    WRITE = 5


class GitHubRepo(BaseModel):
    name: str
    database_id: str
    viewer_permission: str

    @classmethod
    def from_node(cls, node: dict):
        def to_snake_case(s: str):
            ret = []
            for c in s:
                if c.isupper():
                    ret.append("_")
                    ret.append(c.lower())
                else:
                    ret.append(c)
            return "".join(ret)

        return cls(**{to_snake_case(k): v for k, v in node.items()})

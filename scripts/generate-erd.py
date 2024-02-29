from dataclasses import dataclass, field
import logging
from typing import List, NamedTuple

from db.session import Session
from db.schema import *
from sqlalchemy.orm import joinedload


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("generate-erd")


@dataclass
class Field:
    name: str
    type: str


@dataclass
class Entity:
    name: str
    fields: List[Field] = field(default_factory=list)
    self_to_many: List["Entity"] = field(default_factory=list)
    many_to_self: List["Entity"] = field(default_factory=list)


class Relationship(NamedTuple):
    one: str
    many: str


def is_model(obj):
    return hasattr(obj, "__dict__")


def crawl_database(session, cls):
    entities_by_name: dict[str, Entity] = {}
    entities_to_visit = []
    obj = session.query(cls).options(joinedload("*")).first()
    if obj is None:
        raise Exception(
            f"Could not find any records for {cls.__name__} "
            "(ensure your database has data)"
        )
    entities_to_visit.append(obj)

    def new_child(child):
        child_name = child.__class__.__name__
        if child_name not in entities_by_name:
            entities_to_visit.append(child)
        return entities_by_name.setdefault(child_name, Entity(name=child_name))

    while len(entities_to_visit) > 0:
        o = entities_to_visit.pop(0)
        name = o.__class__.__name__
        # Force all lazy joins to be executed and added to session
        # Without this, child entities could be absent from relationships
        for _ in session.query(o.__class__).options(joinedload("*")):
            pass
        entity = entities_by_name.setdefault(name, Entity(name=name))
        for key, value in o.__dict__.items():
            if key.startswith("_"):
                logging.info(f'Skipping private field: {key}')
                continue
            if isinstance(value, list):
                if len(value) < 1:
                    logging.warning(
                        f"Could not map relationship for {key} "
                        "(no instances found)"
                    )
                    continue
                entity.self_to_many.append(new_child(value[0]))
            elif is_model(value):
                entity.many_to_self.append(new_child(value))
            else:
                typ = type(value).__name__ if value is not None else "opt"
                entity.fields.append(Field(name=key, type=typ))
    return entities_by_name


def main():
    with Session() as db:
        entities = crawl_database(db, Jobs)

    relationships = set()
    for name, entity in entities.items():
        if len(entity.self_to_many) > 1:
            logger.warning(
                f"{name} has {len(entity.self_to_many)} "
                "one-to-many relationships (possible fan trap)"
            )
        for e in entity.many_to_self:
            relationships.add(Relationship(one=e.name, many=entity.name))
        for e in entity.self_to_many:
            relationships.add(Relationship(one=entity.name, many=e.name))

    print("```mermaid")
    print("erDiagram")

    for entity in sorted(entities.values(), key=lambda e: e.name):
        print(
            f"    {entity.name} {{"
        )
        fields = sorted(entity.fields, key=lambda f: (len(f.name), f.name))
        print("\n".join(
            f"        {field.type} {field.name}" for field in fields)
        )
        print("    }")

    print(
        "\n".join(
            f'    {relationship.one} ||--|{{ {relationship.many} : ""'
            for relationship in sorted(
                relationships, key=lambda r: (r.many, r.one)
            )
        )
    )
    print("```")


if __name__ == "__main__":
    main()

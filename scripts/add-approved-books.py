from datetime import datetime

from app.db.schema import ApprovedBook, CodeVersion, Consumer
from app.db.session import Session


def main():
    with Session() as db:
        book_id = 1
        consumers = db.query(Consumer).all()
        if not any(c.name == "test" for c in consumers):
            test_consumer = Consumer(name="test", id=len(consumers) + 1)
            db.add(test_consumer)
            db.flush()
            consumers.append(test_consumer)
        code_version = CodeVersion(
            version=datetime.utcnow().strftime("%Y%m%d.%H%M%S")
        )
        db.add(code_version)
        db.flush()
        for consumer in consumers:
            approved_book = ApprovedBook(
                book_id=book_id,
                consumer_id=consumer.id,
                code_version_id=code_version.id
            )
            db.add(approved_book)
        db.commit()


if __name__ == "__main__":
    main()

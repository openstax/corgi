from datetime import datetime

from app.data_models.models import RepositoryGetter
from app.db.schema import Book, Commit, Repository


def test_repository_getter_zero_commits():
    # GIVEN: A repository containing zero commits
    repo = Repository(id=1, name="test")
    repo.commits = []
    # WHEN: The repository getter tries to get books
    # THEN: It returns an empty list instead of the default (None)
    getter = RepositoryGetter(repo)
    books = getter.get("books", None)
    assert books == []


def test_repository_getter_zero_books():
    # GIVEN: A repository containing one commit containing zero books
    repo = Repository(id=1, name="test")
    commit = Commit(
        id=1, timestamp=datetime.fromisoformat("2024-06-05T18:54:16.031Z")
    )
    repo.commits = [commit]
    commit.books = []
    # WHEN: The repository getter tries to get books
    # THEN: It returns an empty list instead of the default (None)
    getter = RepositoryGetter(repo)
    books = getter.get("books", None)
    assert books == []


def test_repository_getter_one_book():
    # GIVEN: A repository containing one commit containing one book
    repo = Repository(id=1, name="test")
    commit = Commit(
        id=1, timestamp=datetime.fromisoformat("2024-06-05T18:54:16.031Z")
    )
    book = Book(slug="test-slug")
    repo.commits = [commit]
    commit.books = [book]
    # WHEN: The repository getter tries to get books
    # THEN: It returns a list of book slugs
    getter = RepositoryGetter(repo)
    books = getter.get("books", None)
    assert books == [book.slug]


def test_repository_getter_multiple_matches():
    # GIVEN: A repository containing two commits containing one or more books each
    repo = Repository(id=1, name="test")
    commit = Commit(
        id=1, timestamp=datetime.fromisoformat("2024-06-05T18:58:16.011Z")
    )
    commit2 = Commit(
        id=2, timestamp=datetime.fromisoformat("2024-06-05T19:03:21.271Z")
    )
    book = Book(slug="test-slug")
    book2 = Book(slug="test-slug-2")
    book3 = Book(slug="test-slug-3")
    commit2.books = [book2, book3]
    commit.books = [book]
    repo.commits = [commit, commit2]
    # WHEN: The repository getter tries to get books
    # THEN: It returns a list of book slugs from the newest commit
    getter = RepositoryGetter(repo)
    books = getter.get("books", None)
    assert books == [b.slug for b in commit2.books]

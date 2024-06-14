import pytest

from app.core import config
from app.data_models.models import BaseApprovedBook, RequestApproveBook
from app.db.schema import ApprovedBook, Book, CodeVersion
from app.service.abl import (
    add_new_entries,
    get_abl_info_database,
    get_or_add_code_version,
    get_rex_book_versions,
)
from tests.unit.conftest import MockAsyncClient


@pytest.mark.parametrize(
    ["query_args"],
    [
        [{}],
        [{"consumer": "test"}],
        [{"repo_name": "test"}],
        [{"version": "a"}],
        [{"code_version": "b"}],
        [{"consumer": "test", "repo_name": "repo-test"}],
        [{"consumer": "test", "code_version": "repo-test"}],
    ],
)
def test_get_abl(query_args, mock_session, snapshot):
    db = mock_session()
    get_abl_info_database(db, **query_args)
    snapshot.assert_match(db.calls_str, "query_get_abl.sql")


def test_get_or_add_code_version(mock_session):
    # GIVEN: The DB does not have the code version
    db = mock_session()
    test_code_version = "a"
    # WHEN: get_or_add_code_version is called
    code_version = get_or_add_code_version(db, test_code_version)
    # THEN: select and insert are called and the code version is added
    assert len(db.calls) == 2
    assert len(db.added_items) == 1
    added_code_version = db.added_items[0]
    assert isinstance(added_code_version, CodeVersion)
    assert added_code_version.version == test_code_version
    assert code_version == added_code_version

    # GIVEN: The DB has the code version
    db = mock_session(lambda *_: [added_code_version])
    # WHEN: get_or_add_code_version is called
    code_version = get_or_add_code_version(db, test_code_version)
    # THEN: db is queried, result is returned, new version is not added
    assert len(db.calls) == 1
    assert len(db.added_items) == 0
    assert code_version.version == test_code_version


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "to_add,to_keep",
    [
        [
            [RequestApproveBook(commit_sha="a", uuid="b", code_version="42")],
            {},
        ],
        [
            [RequestApproveBook(commit_sha="a", uuid="b", code_version="42")],
            {"b": {"defaultVersion": "something"}},
        ],
        [
            [
                RequestApproveBook(commit_sha="a", uuid="b", code_version="42"),
                RequestApproveBook(commit_sha="a", uuid="c", code_version="42"),
            ],
            {"b": {"defaultVersion": "b"}, "c": {"defaultVersion": "c"}},
        ],
    ],
)
async def test_add_new_entries_rex(
    to_add, to_keep, mock_session, mock_http_client, snapshot
):
    def mock_database_logic(session_obj):
        if session_obj.calls:
            last_call = str(session_obj.calls[-1]).replace("\n", "")
            if " FROM consumer " in last_call:
                return [1]
            elif " FROM book " in last_call:
                return [
                    Book(id=i, uuid=entry.uuid, slug="test")
                    for i, entry in enumerate(to_add)
                ]
            elif " FROM approved_book " in last_call:
                return [
                    ApprovedBook(consumer_id=1, book_id=1, code_version_id=1)
                ]

        return []

    db = mock_session(mock_database_logic)
    client: MockAsyncClient = mock_http_client(
        get={config.REX_WEB_RELEASE_URL: {"books": to_keep}}
    )
    await add_new_entries(db, to_add, client)
    assert "authorization" not in client.responses[-1].request.headers
    assert not db.did_rollback
    assert db.did_commit
    # Twice as many because code version is added each time in the test
    assert len(db.added_items) == len(to_add) * 2
    assert isinstance(db.added_items[0], CodeVersion)
    assert isinstance(db.added_items[1], ApprovedBook)
    snapshot.assert_match(db.calls_str, "add_new_entries.sql")


@pytest.mark.parametrize(
    "rex_books,book_uuids,expected",
    [
        [
            {
                "uuid1": {"defaultVersion": "v1"},
                "uuid2": {"defaultVersion": "v1"},
            },
            ["uuid1"],
            [
                BaseApprovedBook(uuid="uuid1", commit_sha="v1"),
            ],
        ],
        [
            {
                "uuid1": {"defaultVersion": "v1"},
                "uuid2": {"defaultVersion": "v1"},
            },
            ["uuid-not-in-release-json"],
            [],
        ],
        [
            {
                "uuid1": {"defaultVersion": "v1"},
                "uuid2": {"defaultVersion": "v1"},
            },
            ["uuid1", "uuid2"],
            [
                BaseApprovedBook(uuid="uuid1", commit_sha="v1"),
                BaseApprovedBook(uuid="uuid2", commit_sha="v1"),
            ],
        ],
        [
            {},
            ["uuid-not-in-release-json"],
            [],
        ],
    ],
)
def test_get_rex_book_versions(rex_books, book_uuids, expected):
    rex_book_versions = get_rex_book_versions(rex_books, book_uuids)
    assert rex_book_versions == expected

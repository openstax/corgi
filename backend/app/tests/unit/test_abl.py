import base64
import json

import pytest

from app.core import config
from app.core.errors import CustomBaseError
from app.data_models.models import BaseApprovedBook, RequestApproveBook
from app.db.schema import ApprovedBook, Book, CodeVersion, Commit
from app.service.abl import (
    add_new_entries,
    get_abl_info_database,
    get_or_add_code_version,
    get_rex_book_versions,
    get_rex_release_version,
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
        # Should delete all with uuid=uuid-book-b because to_keep is empty
        [
            [
                RequestApproveBook(
                    commit_sha="commit1", uuid="uuid-boOk-b", code_version="42"
                )
            ],
            {},
        ],
        # Should delete approved_book2 because added version is new
        [
            [
                RequestApproveBook(
                    commit_sha="commit-new",
                    uuid="UuID-BoOk-A",
                    code_version="42",
                )
            ],
            {"uuid-book-a": {"defaultVersion": "commit1"}},
        ],
        # Should delete approved_book1 and approved_book3 because they are
        # being replaced
        [
            [
                RequestApproveBook(
                    commit_sha="commit1", uuid="uuid-bOok-a", code_version="42"
                ),
                RequestApproveBook(
                    commit_sha="commit3", uuid="uuid-book-B", code_version="42"
                ),
            ],
            {
                "uuid-book-a": {"defaultVersion": "commit1"},
                "uuid-book-b": {"defaultVersion": "commit3"},
            },
        ],
        # Normal case, remove approved_book2
        [
            [
                RequestApproveBook(
                    commit_sha="commit4", uuid="uuid-book-A", code_version="42"
                ),
            ],
            {
                "uuid-book-a": {"defaultVersion": "commit1"},
                "uuid-book-b": {"defaultVersion": "commit3"},
            },
        ],
    ],
)
async def test_add_new_entries_rex(
    to_add, to_keep, mock_session, mock_http_client, snapshot
):
    def mock_database_logic(session_obj):
        book1 = Book(id=1, uuid="uuiD-Book-a", slug="test")
        book2 = Book(id=2, uuid="uuid-book-a", slug="test")
        book3 = Book(id=3, uuid="uuid-boOk-b", slug="test2")
        book1.commit = Commit(id=1, sha="commit1")
        book2.commit = Commit(id=2, sha="commit2")
        book3.commit = Commit(id=3, sha="commit3")
        approved_book1 = ApprovedBook(
            consumer_id=1, book_id=1, code_version_id=1
        )
        approved_book2 = ApprovedBook(
            consumer_id=1, book_id=2, code_version_id=2
        )
        approved_book3 = ApprovedBook(
            consumer_id=1, book_id=3, code_version_id=3
        )
        approved_book1.book = book1
        approved_book2.book = book2
        approved_book3.book = book3
        if session_obj.calls:
            last_call = str(session_obj.calls[-1]).replace("\n", "")
            if " FROM consumer " in last_call:
                return [1]
            elif " FROM book " in last_call:
                params = session_obj.calls[-1].compile().params
                # all uuids and shas used in the query
                lower_params = [
                    v for k, v in params.items() if k.startswith("lower_")
                ]
                # uuids are every other param from 0
                uuids = lower_params[::2]
                # shas are every other param from 1
                # shas = lower_params[1::2]
                return [
                    b
                    for b in (book1, book2, book3)
                    if any(b.uuid.lower() == uuid for uuid in uuids)
                ]
            elif " FROM approved_book " in last_call:
                approved_books = [
                    approved_book1,
                    approved_book2,
                    approved_book3,
                ]
                if " WHERE lower(book.uuid) IN " in last_call:
                    params = session_obj.calls[-1].compile().params
                    uuids = params["lower_1"]
                    approved_books = [
                        ab
                        for ab in approved_books
                        if ab.book.uuid.lower() in uuids
                    ]
                return approved_books

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
    snapshot.assert_match(db.params_str, "add_new_entries_params.json")


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


@pytest.mark.asyncio
async def test_get_rex_release_version(mock_http_client):
    url = "https://api.github.com/repos/openstax/rex-web/contents/src/config.archive-url.json"
    fake_api_response = {
        "content": base64.b64encode(
            json.dumps({"REACT_APP_ARCHIVE": "20240101.000001"}).encode()
        ).decode()
    }

    # GIVEN: A valid response
    mock_client: MockAsyncClient = mock_http_client(
        get={url: fake_api_response}
    )
    # WHEN: A request is made
    version = await get_rex_release_version(mock_client)
    # THEN: We get one call to the http client
    assert len(mock_client.responses) == 1
    # THEN: The user token was not sent
    assert "authorization" not in mock_client.responses[-1].request.headers
    # THEN: The expected version is matched
    assert version == "20240101.000001"

    # GIVEN: An invalid response
    mock_client: MockAsyncClient = mock_http_client(
        get={
            url: {"content": base64.b64encode(json.dumps({}).encode()).decode()}
        }
    )
    # WHEN: A request is made
    # THEN: An error is raised
    with pytest.raises(CustomBaseError) as cbe:
        await get_rex_release_version(mock_client)
    assert cbe.match("Could not find valid REX version")
    # GIVEN: A no response
    mock_client: MockAsyncClient = mock_http_client()
    # WHEN: A request is made
    # THEN: An error is raised
    with pytest.raises(CustomBaseError) as cbe:
        await get_rex_release_version(mock_client)
    assert len(mock_client.responses) == 1
    assert cbe.match("Failed to fetch rex release")

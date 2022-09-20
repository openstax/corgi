abl
    collection
    version
    book

for the management of abl entries:
    query abl entry by job
    query job by abl entry
    add abl entry -> pass json
    update abl entry -> pass json
    remove abl entry by ???

OpenStax is a company that publishes open textbooks

they manage their book content by COLLECTION using github REPOS
they keep track of which books have been accepted for release by means of an
ACCEPTED BOOK LIST
this list organizes books by
REPO NAME
    and lists all VERSIONS for a given REPO under that
    individual VERSIONS contain
        a MINIMUM CODE VERSION they were produced with
        the current EDITION
        the COMMIT SHA identifying the accpeted content state
        and COMMIT METADATA including
            the time the accepted content was COMMIITED AT
            and a list of the BOOKS
            containing their individual
                STYLE
                a UUID uniquely identifying that book
                and the SLUG or book name

when books are "published" the code runs against a REPO, SLUG, VERSION and STYLE
the unique JOB that runs to build them contains information regarding its CODE VERSION

REPOS contain COMMITS
REPOS contain BOOKS

COMMITS have SHAS
             COMMIT TIME

BOOKS have VERSIONS

VERSIONS have COMMITS

VERSIONS contain MIN CODE VERSION
                 EDITION
                 COMMIT SHA
                 


REPOSITORY_NAME
        VERSIONS
            VERSION
                MIN_CODE_VERSION
                EDITION
                COMMIT_SHA
                COMMIT_METADATA
                    COMMIITED_AT
                    BOOKS
                        BOOK
                            STYLE
                            UUID
                            SLUG

# "repository_name": "osbooks-introduction-philosophy",
#         "platforms": ["REX"],
#         "versions": [
#           {
#             "min_code_version": "20220509.174553",
#             "edition": 1,
#             "commit_sha": "ec61644ed9622f84bbfc739bc0c99d1d1a105aac",
#             "commit_metadata": {
#               "committed_at": "2022-06-02T20:21:00+00:00",
#               "books": [
#                 {
#                   "style": "philosophy",
#                   "uuid": "fe58be6f-3b61-4e16-b3b6-db6924f0b2f2",
#                   "slug": "introduction-philosophy"
#                 }
#               ]
#             }
#           }
#         ]
#       }, 



Loop over each repo
take 2 most recent approved jobs
gives us min code from job code
gives us commit sha
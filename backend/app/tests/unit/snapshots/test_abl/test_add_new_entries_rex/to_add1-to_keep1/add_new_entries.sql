SELECT book.id, book.uuid, book.commit_id, book.edition, book.slug, book.style 
FROM book JOIN commit ON commit.id = book.commit_id 
WHERE book.uuid = :uuid_1 AND commit.sha = :sha_1

SELECT consumer.id 
FROM consumer 
WHERE consumer.name = :name_1

SELECT approved_book.book_id, approved_book.consumer_id, approved_book.code_version_id, approved_book.created_at, approved_book.updated_at 
FROM approved_book JOIN book ON book.id = approved_book.book_id JOIN commit ON commit.id = book.commit_id 
WHERE book.uuid IN (__[POSTCOMPILE_uuid_1]) AND approved_book.consumer_id = :consumer_id_1

DELETE FROM approved_book WHERE approved_book.consumer_id = :consumer_id_1 AND approved_book.book_id = :book_id_1 AND approved_book.code_version_id = :code_version_id_1

SELECT code_version.id, code_version.version, code_version.created_at, code_version.updated_at 
FROM code_version 
WHERE code_version.version = :version_1

INSERT INTO CodeVersion ...

INSERT OR UPDATE INTO ApprovedBook ...
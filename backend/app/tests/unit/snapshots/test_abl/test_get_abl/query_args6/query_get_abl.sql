SELECT approved_book.book_id, approved_book.consumer_id, approved_book.code_version_id, approved_book.created_at, approved_book.updated_at 
FROM approved_book JOIN consumer ON consumer.id = approved_book.consumer_id JOIN code_version ON code_version.id = approved_book.code_version_id 
WHERE consumer.name = :name_1 AND code_version.version <= :version_1
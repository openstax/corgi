SELECT approved_book.book_id, approved_book.consumer_id, approved_book.code_version_id, approved_book.created_at, approved_book.updated_at 
FROM approved_book JOIN book ON book.id = approved_book.book_id JOIN commit ON commit.id = book.commit_id JOIN repository ON repository.id = commit.repository_id 
WHERE repository.name = :name_1
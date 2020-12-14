import sys
import json
from pathlib import Path
from datetime import datetime
import boto3
import botocore


def main():
    feed_json = Path(sys.argv[1]).resolve(strict=True)
    code_version = sys.argv[2]
    queue_state_bucket = sys.argv[3]
    queue_filename = sys.argv[4]
    max_books_per_run = int(sys.argv[5])
    state_prefix = sys.argv[6]

    with open(feed_json, 'r') as feed_file:
        feed_data = json.load(feed_file)

    s3_client = boto3.client('s3')
    books_queued = 0

    # Iterate through feed and check for a book that is not completed based
    # upon existence of a {code_version}/.{collection_id}@{version}.complete
    # file in S3 bucket. If the book is not complete, check pending and retry
    # states to see whether or not it has errored or timed out too many times
    # to be queued again.

    for book in feed_data:
        # Check for loop exit condition
        if books_queued >= max_books_per_run:
            break

        book_identifier = book.get('slug', book.get('collection_id'))

        book_prefix = \
            f".{state_prefix}.{book_identifier}@{book['version']}"

        complete_filename = f"{book_prefix}.complete"
        complete_key = f"{code_version}/{complete_filename}"
        try:
            print(f"Checking for s3://{queue_state_bucket}/{complete_key}")
            s3_client.head_object(
                Bucket=queue_state_bucket,
                Key=complete_key
            )
            # Book is complete, move along to next book
            continue
        except botocore.exceptions.ClientError as error:
            error_code = error.response['Error']['Code']
            if error_code != '404':
                # Not an expected 404 error
                raise
            # Otherwise, book is not complete and we check other states

        # These states are order-dependant.
        # i.e. only move to retry if pending passes through
        for state in ['pending', 'retry']:
            state_filename = f"{book_prefix}.{state}"
            state_key = f"{code_version}/{state_filename}"
            try:
                print(f"Checking for s3://{queue_state_bucket}/{state_key}")
                s3_client.head_object(
                    Bucket=queue_state_bucket,
                    Key=state_key
                )
            except botocore.exceptions.ClientError as error:
                error_code = error.response['Error']['Code']
                if error_code == '404':
                    print(f"Found feed entry to build: {book}")
                    s3_client.put_object(
                        Bucket=queue_state_bucket,
                        Key=queue_filename,
                        Body=json.dumps(book)
                    )
                    # Mark state to not be entered again
                    s3_client.put_object(
                        Bucket=queue_state_bucket,
                        Key=state_key,
                        Body=datetime.now().astimezone().isoformat(
                            timespec='seconds'
                        )
                    )
                    books_queued += 1
                    # Book was queued, don't try to queue it again
                    break
                else:
                    # Not an expected 404 error
                    raise

    print(f"Queued {books_queued} books")


if __name__ == "__main__":
    main()

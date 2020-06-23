import sys
import json
from pathlib import Path
import boto3
import botocore

def main():
    feed_json = Path(sys.argv[1]).resolve(strict=True)
    code_version = sys.argv[2]
    queue_state_bucket = sys.argv[3]
    queue_filename = sys.argv[4]
    max_books_per_run = int(sys.argv[5])

    with open(feed_json, 'r') as feed_file:
        feed_data = json.load(feed_file)

    s3_client = boto3.client('s3')
    books_queued = 0

    # Iterate through feed and check for a book that is not completed based
    # upon the existence of a {code_version}/.{collection_id}@{version}.complete
    # file in S3 bucket
    for book in feed_data:
        # Check for loop exit condition
        if books_queued >= max_books_per_run:
            break

        complete_filename = \
            f".{book['collection_id']}@{book['version']}.complete"
        bucket_key = f"{code_version}/{complete_filename}"

        try:
            print(f"Checking for s3://{queue_state_bucket}/{bucket_key}")
            s3_client.head_object(
                Bucket=queue_state_bucket,
                Key=bucket_key
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
                books_queued += 1
            else:
                # Not an expected 404 error
                raise

    print(f"Queued {books_queued} books")

if __name__ == "__main__":
    main()

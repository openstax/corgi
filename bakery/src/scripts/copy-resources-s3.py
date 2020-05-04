import concurrent.futures
import boto3
import boto3.session
import botocore
import json
import os
import sys
from pathlib import Path

MAX_THREAD_WORKERS = 10


def slash_join(*args):
    """ join url parts safely """
    return "/".join(arg.strip("/") for arg in args)


def s3_md5sum(s3_client, bucket_name, resource_name):
    """ get (special) md5 of S3 resource or None when not existing """
    try:
        md5sum = s3_client.head_object(
            Bucket=bucket_name,
            Key=resource_name
        )['ETag']
    except botocore.exceptions.ClientError:
        md5sum = None
        pass
    return md5sum


def upload_s3(aws_key, aws_secret, filename, bucket, key, content_type):
    """ upload s3 process for ThreadPoolExecutor """
    # use session for multithreading according to
    # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/resources.html?highlight=multithreading#multithreading-multiprocessing
    session = boto3.session.Session()
    s3_client = session.client(
        's3', aws_access_key_id=aws_key, aws_secret_access_key=aws_secret)
    print('Uploading ' + key)
    s3_client.upload_file(
        Filename=filename,
        Bucket=bucket,
        Key=key,
        ExtraArgs={
            "ContentType": content_type
        }
    )
    return key


def upload(in_dir, bucket, bucket_folder):
    """ upload resource and resource json to S3 """
    aws_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')

    # environment variables mandatory for ThreadPoolExecutor
    if aws_key is None or aws_secret is None:
        raise EnvironmentError(
            'Failed because AWS_ACCESS_KEY_ID and/or AWS_SECRET_ACCESS_KEY environment variable missing.')

    # session for s3_md5sum
    session = boto3.session.Session()
    s3_client = session.client(
        's3',
        aws_access_key_id=aws_key,
        aws_secret_access_key=aws_secret
    )

    sha1_filepattern = '?' * 40  # sha1 hexdigest as 40 characters

    # upload to s3 async with ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREAD_WORKERS) as executor:
        s3_futures = []
        for resource in Path(in_dir).glob(sha1_filepattern):
            input_file = str(resource)
            input_metadata_file = input_file + '.json'
            output_s3 = slash_join(bucket_folder, os.path.basename(input_file))
            output_s3_metadata = slash_join(bucket_folder,
                                            os.path.basename(input_file) + '-unused.json')

            try:
                with open(input_metadata_file) as json_file:
                    data = json.load(json_file)
                    # if file not existing (compare special AWS md5) then upload it
                    # note: Theoretically s3_md5sum could be itself also in a threadpool
                    #       which generates new uploads in a threadpool.
                    #       In my opinion the slight speed increase is not worth
                    #       the additional complexity.
                    if data['s3_md5'] != s3_md5sum(s3_client, bucket, output_s3):

                        # upload metadata first (because this is not checked)
                        s3_futures.append(
                            executor.submit(
                                upload_s3,
                                aws_key=aws_key,
                                aws_secret=aws_secret,
                                filename=input_metadata_file,
                                bucket=bucket,
                                key=output_s3_metadata,
                                content_type='application/json')
                        )

                        # upload resource file last (existence/md5 is checked)
                        s3_futures.append(
                            executor.submit(
                                upload_s3,
                                aws_key=aws_key,
                                aws_secret=aws_secret,
                                filename=input_file,
                                bucket=bucket,
                                key=output_s3,
                                content_type=data['mime_type'])
                        )

                    else:
                        print('File existing ' + output_s3)
            except FileNotFoundError as e:
                print('No metadata found: ' + str(e))
                exit(1)
    for future in concurrent.futures.as_completed(s3_futures):
        s3_futures.remove(future)
    print('FINISHED UPLOADING!')


def main():
    in_dir = Path(sys.argv[1]).resolve(strict=True)
    bucket = sys.argv[2]
    bucket_folder = sys.argv[3]
    upload(in_dir, bucket, bucket_folder)


if __name__ == "__main__":
    main()

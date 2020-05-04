import concurrent.futures
import boto3
import boto3.session
import botocore
import json
import os
import sys
import traceback
from pathlib import Path

MAX_THREAD_CHECK_S3 = 20
MAX_THREAD_UPLOAD_S3 = 20


class ThreadPoolExecutorStackTraced(concurrent.futures.ThreadPoolExecutor):
    # Stack Traced ThreadPoolExecutor for better error messages on exceptions on Threads
    # https://stackoverflow.com/a/24457608/756056

    def submit(self, fn, *args, **kwargs):
        """Submits the wrapped function instead of `fn`"""

        return super(ThreadPoolExecutorStackTraced, self).submit(
            self._function_wrapper, fn, *args, **kwargs)

    def _function_wrapper(self, fn, *args, **kwargs):
        """Wraps `fn` in order to preserve the traceback of any kind of
        raised exception

        """
        try:
            return fn(*args, **kwargs)
        except Exception:
            # Creates an exception of the same type with the traceback as message
            raise sys.exc_info()[0](traceback.format_exc())


def slash_join(*args):
    """ join url parts safely """
    return "/".join(arg.strip("/") for arg in args)


def check_s3_existence(aws_key, aws_secret, bucket, resource):
    """ check if resource is already existing or needs uploading """
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

    try:
        upload_resource = None
        with open(resource['input_metadata_file']) as json_file:
            data = json.load(json_file)

            session = boto3.session.Session()
            s3_client = session.client(
                's3',
                aws_access_key_id=aws_key,
                aws_secret_access_key=aws_secret)

            if data['s3_md5'] != s3_md5sum(s3_client, bucket, resource['output_s3']):
                upload_resource = resource
                upload_resource['mime_type'] = data['mime_type']
        return upload_resource
    except FileNotFoundError as e:
        print('Error: No metadata json found!')
        raise(e)


def upload_s3(aws_key, aws_secret, filename, bucket, key, content_type):
    """ upload s3 process for ThreadPoolExecutor """
    # use session for multithreading according to
    # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/resources.html?highlight=multithreading#multithreading-multiprocessing
    session = boto3.session.Session()
    s3_client = session.client(
        's3', aws_access_key_id=aws_key, aws_secret_access_key=aws_secret)
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

    sha1_filepattern = '?' * 40  # sha1 hexdigest as 40 characters

    # upload to s3 async with ThreadPoolExecutor
    # with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREAD_WORKERS) as executor:

    all_resources = []
    for sha1filename in Path(in_dir).glob(sha1_filepattern):
        resource = {}
        resource['bucket'] = bucket
        resource['input_file'] = str(sha1filename)
        resource['input_metadata_file'] = resource['input_file'] + '.json'
        resource['output_s3'] = slash_join(
            bucket_folder, os.path.basename(resource['input_file']))
        resource['output_s3_metadata'] = slash_join(bucket_folder,
                                                    os.path.basename(resource['input_file']) + '-unused.json')
        all_resources.append(resource)

    upload_resources = []
    check_futures = []
    with ThreadPoolExecutorStackTraced(max_workers=MAX_THREAD_CHECK_S3) as executor:
        print('Checking which files to upload ', end='', flush=True)
        for resource in all_resources:
            check_futures.append(
                executor.submit(
                    check_s3_existence,
                    aws_key=aws_key,
                    aws_secret=aws_secret,
                    bucket=bucket,
                    resource=resource)
            )
        for future in concurrent.futures.as_completed(check_futures):
            try:
                resource = future.result()
                if resource is not None:
                    upload_resources.append(resource)
                    print('.', end='', flush=True)
                else:
                    print('x', end='', flush=True)
                check_futures.remove(future)
            except Exception as e:
                print(e)
                # stop all threads on error now
                executor._threads.clear()
                concurrent.futures.thread._threads_queues.clear()
                sys.exit(1)
    print()
    print('{} resources need uploading.'.format(len(upload_resources)))

    uploadcount = 0
    upload_futures = []
    with ThreadPoolExecutorStackTraced(max_workers=MAX_THREAD_UPLOAD_S3) as executor:
        print('Uploading to S3 ', end='', flush=True)
        for resource in upload_resources:
            # upload metadata first (because this is not checked)
            upload_futures.append(
                executor.submit(
                    upload_s3,
                    aws_key=aws_key,
                    aws_secret=aws_secret,
                    filename=resource['input_metadata_file'],
                    bucket=bucket,
                    key=resource['output_s3_metadata'],
                    content_type='application/json')
            )
            # upload resource file last (existence/md5 is checked)
            upload_futures.append(
                executor.submit(
                    upload_s3,
                    aws_key=aws_key,
                    aws_secret=aws_secret,
                    filename=resource['input_file'],
                    bucket=bucket,
                    key=resource['output_s3'],
                    content_type=resource['mime_type'])
            )
        for future in concurrent.futures.as_completed(upload_futures):
            try:
                if (future.result()):
                    uploadcount = uploadcount + 1
                    print('.', end='', flush=True)
                upload_futures.remove(future)
            except Exception as e:
                print(e)
                # stop all threads on error now
                executor._threads.clear()
                concurrent.futures.thread._threads_queues.clear()
                sys.exit(1)
    uploadcount = int(uploadcount / 2)  # divide by 2 because of json metadata
    print()
    print('{} resources uploaded.'.format(uploadcount))
    if (uploadcount) != len(upload_resources):
        print('ERROR: Uploaded counted and needed to upload mismatch: {} != {}'.format(
            uploadcount, len(upload_resources)))
        sys.exit(1)
    print('FINISHED uploading resources.')


def main():
    in_dir = Path(sys.argv[1]).resolve(strict=True)
    bucket = sys.argv[2]
    bucket_folder = sys.argv[3]
    upload(in_dir, bucket, bucket_folder)


if __name__ == "__main__":
    main()

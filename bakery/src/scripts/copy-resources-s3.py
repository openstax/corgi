import boto3
import botocore
import json
import os
import sys
from urllib.parse import urljoin
from pathlib import Path


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


def upload(in_dir, bucket, bucket_folder):
    """ upload resource and resource json to S3 """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

    sha1_filepattern = '?' * 40 # sha1 hexdigest as 40 characters

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
                if data['s3_md5'] != s3_md5sum(s3_client, bucket, output_s3):
                    print('Uploading ' + output_s3_metadata)
                    # first upload metadata
                    s3_client.upload_file(
                        Filename=input_metadata_file,
                        Bucket=bucket,
                        Key=output_s3_metadata,
                        ExtraArgs={
                            "ContentType": 'application/json'
                        }
                    )
                    print('Uploading ' + output_s3)
                    # upload resource file
                    s3_client.upload_file(
                        Filename=input_file,
                        Bucket=bucket,
                        Key=output_s3,
                        ExtraArgs={
                            "ContentType": data['mime_type']
                        }
                    )
                else:
                    print('File existing ' + output_s3)
        except FileNotFoundError as e:
            print('No metadata found: ' + str(e))
            exit(1)


def main():
    in_dir = Path(sys.argv[1]).resolve(strict=True)
    bucket = sys.argv[2]
    bucket_folder = sys.argv[3]
    upload(in_dir, bucket, bucket_folder)

if __name__ == "__main__":
    main()

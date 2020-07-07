"""
Create an s3 bucket configured for static website hosting

It assumes you have configured your aws credentials properly in the ~/.aws/config to authorize the requests

Arguments:
    bucket_name: The name of the bucket to be created. It must be a unique name

Example::

    python3 scripts/http_bucket.py my.unique_bucket.com
"""
import boto3
import json
import sys

s3 = boto3.client('s3')

bucket_name = sys.argv[1]

# Create the bucket
bucket = s3.create_bucket(Bucket=bucket_name)

# Enable static website hosting
s3.put_bucket_website(
    Bucket=bucket_name,
    WebsiteConfiguration={
        "IndexDocument": {
            "Suffix": "index.html",
        },
    },
)

# Add Bucket Policy
policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                f'arn:aws:s3:::{bucket_name}/*',
            ]
        }
    ]
}

s3.put_bucket_policy(
    Bucket=bucket_name,
    Policy=json.dumps(policy),
)

print("done!")

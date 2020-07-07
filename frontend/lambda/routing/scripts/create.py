"""
A python script to create and deploy the lambda function
It will download all of the dependencies, create the zip file, and create the lambda
function in aws using boto3
It should be run from the root directory of this lambda function

Parameters:
    role: The role for the lambda function
    domain_name: A CNAME Alias associated with a cloudfront distribution that
        can be used to find the correct cloudfront distribution

Example:
    python3 scripts/create.py \
        arn:aws:iam::499531146673:role/cloudfront_redirect_handler_role \
        my.domain.com
"""
import boto3
import sys
from build_package import build_package

FUNCTION_NAME = "DefaultCloudfrontRedirectTest"
lambda_client = boto3.client('lambda', region_name='us-east-1')
cloudfront = boto3.client('cloudfront')

role = sys.argv[1]
domain_name = sys.argv[2]

# Compile the function
encoded_zip_file = build_package()

# Create lambda function
lambda_resp = lambda_client.create_function(
    FunctionName=FUNCTION_NAME,
    Runtime="python3.7",
    Handler="lambda_function.handler",
    Publish=True,
    Role=role,
    Code={
        "ZipFile": encoded_zip_file,
    },
    Timeout=10,
)
version_resp = lambda_client.publish_version(FunctionName=FUNCTION_NAME)

# Associate with the cloudfront distribution
distributions = cloudfront.list_distributions()['DistributionList']['Items']
try:
    distribution = [c for c in distributions if domain_name in c['Aliases']['Items']][0]
    config = cloudfront.get_distribution_config(Id=distribution['Id'])
except IndexError:
    print("Could not find cloudfront distribution")
    raise IndexError

config['DistributionConfig']['DefaultCacheBehavior']['LambdaFunctionAssociations'] = {
    'Quantity': 1,
    'Items': [
        {
            'LambdaFunctionARN': version_resp['FunctionArn'],
            'EventType': 'origin-request',
            'IncludeBody': False,
        },
    ],
}

cloudfront.update_distribution(
    Id=distribution['Id'],
    IfMatch=config['ETag'],
    DistributionConfig=config['DistributionConfig'],
)
print('done')

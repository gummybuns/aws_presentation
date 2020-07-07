"""Create a Cloudfront Distribution

It will also associate the cloudfront distribution in S3 as an Alias A record
to the specified domain_name

Parameters:
    domain_name: The name of both the bucket and the url of the website we are creating
    certificate_domain_name: The string that identifies the ssl cert in ACM that
        will be used for the the distribution. It could be the domain_name or
        maybe something like *.example.com
    hosted_zone: the name of the hosted zone to associate in s3
"""
import boto3
import sys
import uuid

# BOTO3 HELPERS
cloudfront = boto3.client('cloudfront')
acm = boto3.client('acm')
route53 = boto3.client('route53')

# BUILT PARAMETERS
domain_name = sys.argv[1]
record_name = f'{domain_name}.'
certificate_domain_name = sys.argv[2]
hosted_zone = f'{sys.argv[3]}.'
origin_id = f'{domain_name}_origin'

# CONSTANTS
CLOUDFRONT_HOSTED_ZONE_ID = 'Z2FDTNDATAQYW2'

# Find the hosted zone
zones = route53.list_hosted_zones()['HostedZones']
try:
    zone = [z for z in zones if z['Name'] == hosted_zone][0]
except IndexError:
    print("Must create zone first")
    raise IndexError

# Find the SSL Certificate
certificates = acm.list_certificates(CertificateStatuses=['ISSUED'])['CertificateSummaryList']
try:
    certificate = [c for c in certificates if c['DomainName'] == certificate_domain_name][0]
except IndexError:
    print("Could not find certificate by domain name")
    raise IndexError

# Create the Distribution
distribution = cloudfront.create_distribution(
    DistributionConfig={
        'CallerReference': str(uuid.uuid4()),
        'Aliases': {
            'Quantity': 1,
            'Items': [
                domain_name,
            ],
        },
        'Origins': {
            'Quantity': 1,
            'Items': [
                {
                    'Id': origin_id,
                    'OriginPath': '',
                    'DomainName': f'{domain_name}.s3-website-us-east-1.amazonaws.com',
                    'ConnectionAttempts': 3,
                    'ConnectionTimeout': 10,
                    'CustomHeaders': {
                        'Quantity': 0,
                    },
                    'CustomOriginConfig': {
                        'HTTPPort': 80,
                        'HTTPSPort': 443,
                        'OriginProtocolPolicy': 'http-only',
                        'OriginReadTimeout': 30,
                        'OriginSslProtocols': {
                            'Quantity': 3,
                            'Items': [ 'TLSv1', 'TLSv1.1', 'TLSv1.2'],
                        },
                    },
                }
            ],
        },
        'DefaultCacheBehavior': {            
            'TargetOriginId': origin_id,
            'ForwardedValues': {
                'QueryString': False,
                'Cookies': {
                    'Forward': 'none',
                },
            },
            'TrustedSigners': {
                'Enabled': False,
                'Quantity': 0,
            },
            'ViewerProtocolPolicy': 'redirect-to-https',
            'MinTTL': 0,
            'DefaultTTL': 86400,
            'MaxTTL': 31536000,
            'AllowedMethods': {
                'Quantity': 2,
                'Items': ['GET', 'HEAD'],
                'CachedMethods': {
                    'Quantity': 2,
                    'Items': ['GET', 'HEAD'],
                },
            },
        },
        'Comment': '',
        'Enabled': True,
        'ViewerCertificate': {
            'CloudFrontDefaultCertificate': False,
            'ACMCertificateArn': certificate['CertificateArn'],
            'SSLSupportMethod': 'sni-only',
        },
    },
)['Distribution']

resp = route53.change_resource_record_sets(
    HostedZoneId=zone['Id'],
    ChangeBatch={
        'Comment': 'Add new record for bucket',
        'Changes': [
            {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': record_name,
                    'Type': 'A',
                    'AliasTarget': {
                        'HostedZoneId': CLOUDFRONT_HOSTED_ZONE_ID,
                        'DNSName': distribution['DomainName'],
                        'EvaluateTargetHealth': False,
                    },
                },
            },
        ],
    },
)

print('DONE')

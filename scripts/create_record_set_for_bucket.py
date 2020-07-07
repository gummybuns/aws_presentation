import boto3
import sys

route53 = boto3.client('route53')

hosted_zone = f'{sys.argv[1]}.'
record_name = f'{sys.argv[2]}.'

# See https://docs.aws.amazon.com/general/latest/gr/s3.html#s3_website_region_endpoints
ALIAS_ZONE_ID = 'Z3AQBSTGFYJSTF'
DNSNAME = 's3-website-us-east-1.amazonaws.com'

zones = route53.list_hosted_zones()['HostedZones']
try:
    zone = [z for z in zones if z['Name'] == hosted_zone][0]
except IndexError:
    print("Must create zone first")
    raise IndexError

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
                        'HostedZoneId': ALIAS_ZONE_ID,
                        'DNSName': DNSNAME,
                        'EvaluateTargetHealth': False,
                    },
                },
            },
        ],
    },
)

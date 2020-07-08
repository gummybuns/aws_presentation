"""
Create the record set for a the S3 Bucket

It will throw an error if the domain name doesnt match a hosted zone. I took
some shortcuts making this script. First - it only works for US-East-1 region.
This is because every region has a different ALIAS_ZONE_ID and corresponding
DNSNAME. I took a shortcut to assume us-east-1 because i was lazy.

Arguments:
    hosted_zone - the root domain name
    record_name - the domain/subdomain to be added

Example::

    python3 scripts/create_record_set_for_bucket.py \
            realzacbrown.com \
            test.realzacbrown.com
"""
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

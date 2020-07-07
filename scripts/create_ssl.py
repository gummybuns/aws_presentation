import boto3
import sys
from time import sleep

acm = boto3.client('acm')
route53 = boto3.client('route53')

domain_name = sys.argv[1]
hosted_zone_name = f'{sys.argv[2]}.'

# Find the hosted zone
zones = route53.list_hosted_zones()['HostedZones']
try:
    zone = [z for z in zones if z['Name'] == hosted_zone_name][0]
except IndexError:
    print("Must create zone first")
    raise IndexError

# Generate the Certificate
resp = acm.request_certificate(
    DomainName=domain_name,
    ValidationMethod="DNS")
arn = resp['CertificateArn']
print('Created Certificate')

# artificially wait for the certificate to be ready
sleep(5)
certificate = acm.describe_certificate(CertificateArn=arn)['Certificate']
resource_record = certificate['DomainValidationOptions'][0]['ResourceRecord']

# Add the verification records to the zone
resp = route53.change_resource_record_sets(
    HostedZoneId=zone['Id'],
    ChangeBatch={
        'Comment': 'verify ssl cert',
        'Changes': [
            {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': resource_record['Name'],
                    'Type': resource_record['Type'],
                    'TTL': 3600,
                    'ResourceRecords': [
                        {
                            'Value': resource_record['Value'],
                        },
                    ],
                },
            },
        ],
    },
)
print('Added records to route 53')

check = acm.describe_certificate(CertificateArn=arn)['Certificate']
while check['DomainValidationOptions'][0]['ValidationStatus'] == 'PENDING_VALIDATION':
    print('verifying...')
    sleep(10)
    check = acm.describe_certificate(CertificateArn=arn)['Certificate']

print('done')

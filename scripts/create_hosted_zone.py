"""
Create a Hosted Zone in Route53

It prints out the NS records for you to put in your DNS Provider. If there
already exists a zone with that domain, it will print out the NS records
regardless

Arguments:
    domain_name: The name root domain name you want in Route53

Example::

    python3 scripts/create_hosted_zone.py myuniquedomain.com
"""
import boto3
import uuid
import sys

route53 = boto3.client('route53')

domain_name = f'{sys.argv[1]}.'

# Find or create the hosted zone
zones = route53.list_hosted_zones()['HostedZones']
try:
    new_zone = [z for z in zones if z['Name'] == domain_name][0]
except IndexError:
    resp = route53.create_hosted_zone(Name=domain_name, CallerReference=str(uuid.uuid4()))
    new_zone = resp['HostedZone']

# Print out the ns records of the wumbomail zone
records = route53.list_resource_record_sets(HostedZoneId=new_zone['Id'])['ResourceRecordSets']
ns = [r for r in records if r['Type'] == 'NS'][0]
print(f'\nSet these in your DNS NameServer for {domain_name}')
for r in ns['ResourceRecords']:
    print(r['Value'][:-1]) # once again aws adds a period we dont want in our dns
print('done!')

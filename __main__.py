import pulumi
import pulumi_linode as linode
from linode_domain_maker import makeLinodeDomain

tags = ['pulumi']
email = 'example@email.com'

# Host Linode configuration
host = linode.Instance('host_linode', label='pulumi-linode',
                       type='g6-nanode-1', region='us-east',
                       image='linode/ubuntu18.04', tags=tags)

# Generate list of domain names
with open('domains.txt') as f:
    domain_names = f.read().splitlines()

# Create domains and domain records
zone = {}
records = {}
for domain in domain_names:
    makeLinodeDomain(host.ip_address, domain, zone, records, email, tags)
    pulumi.export("Linode domain zone created for '%s' with basic A records "
                  "targeting" % domain, host.ip_address)

pulumi.export('host_linode created with public IPv4: ', host.ip_address)

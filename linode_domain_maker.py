import pulumi_linode as linode


def makeLinodeDomain(ipv4, domain, zone_dict, record_dict, soa_email, tags):
    """Generates Pulumi/Linode resources to create a domain zone with basic
    A records for a domain and its 'www' subdomain, and stores these resources
    in appropriate dictionaries."""

    zone_dict[domain] = linode.Domain(domain+'-zone', domain=domain,
                                      type='master', soa_email=soa_email,
                                      tags=tags)
    makeLinodeDomainRecord(ipv4, zone_dict[domain], domain, '', record_dict)
    makeLinodeDomainRecord(ipv4, zone_dict[domain], domain, 'www', record_dict)


def makeLinodeDomainRecord(ipv4, domain_resource, domain, sub, record_dict):
    """Generates Pulumi/Linode resources to create an A record for the domain
    zone corresponding to a domain zone ID
    (see https://developers.linode.com/api/docs/v4#operation/getDomain)."""

    if sub == '':
        record = domain + '-A'
    else:
        record = sub + '.' + domain + '-A'
    record_dict[record] = linode.DomainRecord(record,
                                              name=sub,
                                              record_type='A',
                                              domain_id=domain_resource.id,
                                              target=ipv4)

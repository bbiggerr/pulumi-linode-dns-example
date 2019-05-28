# Getting Started with Pulumi + Linode

Linode is now available on [Pulumi](https://www.pulumi.com/), an infrastructure as software solution that allows provisioning of cloud resources for several coding languages. This thread contains helpful resources for using Pulumi with Linode. Feel free to comment on this thread with comments and questions.

## Helpful Resources

* [Pulumi QuickStart](https://pulumi.io/quickstart)
* [Pulumi Concepts](https://pulumi.io/reference/concepts.html)
* [Pulumi App](https://app.pulumi.com)
* [Pulumi Slack Channel](https://slack.pulumi.io/)
* [Linode Provider](https://pulumi.io/reference/pkg/index.html)
  * [Go](https://godoc.org/github.com/pulumi/pulumi-linode#Provider) <!-- not that useful, follow links to file level comments -->
  * [Node.js](https://pulumi.io/reference/pkg/nodejs/@pulumi/linode/index.html)
  * [Python](https://pulumi.io/reference/pkg/python/pulumi_linode/index.html) <!-- awaiting a fix -->

## Getting Started

Here's a simple guide to get started with provisioning Linode resources using Pulumi:

1. [Install Pulumi](https://pulumi.io/quickstart/install.html)
1. Run `pulumi new` in your project directory and follow the configuration prompts.
    * Select the `linode-` option with your preferred language:
      * linode-go
      * linode-javascript
      * linode-python
      * linode-typescript
    * You'll be prompted to enter your Linode API token, so be sure to [create a token](https://www.linode.com/docs/platform/api/getting-started-with-the-linode-api/#create-an-api-token) with appropriate read/write permissions.
1. Your project folder will now have the minimal configuration required to create a Linode. The `Pulumi.yaml` file contains the selected runtime and depending on the chosen language the project code can be found in either a `index.ts`, `index.js`, `main.go`, or `__main__.py` file.
1. Run `pulumi up` to run the default project code and provision a Linode (confirm or cancel after reviewing projected changes), or continue by adjusting the files according to your project.
1. Your project and its resources are available for review 

## Helpful Tips and Practices

Here are some helpful practices to keep in mind when using Pulumi:

### Use Tags

Once a Pulumi project is created and resources are provisioned, take care to make changes to those resources from within Pulumi to avoid future conflicts. Accordingly, it's good practice to apply Linode Manager tags to resources created through Pulumi.

### Bring Down and Remove Projects

You can remove resources with the following command:

```nohighlight
pulumi destroy
```

Your project will remain under your account (and viewable in the [Pulumi App](https://app.pulumi.com)) until it is removed with the following command:

```nohighlight
pulumi stack rm $project
```

Be sure to remove your project before deleting any project files and directories. 

## Example Project: DNS Controller in Python

Managing many domains using Linode's [DNS Manager](https://www.linode.com/docs/platform/manager/dns-manager/) can quickly become cumbersome. Pulumi can be used to efficiently control your DNS Manager zones and records.

Suppose you have a list of domains you want to point to a Linode titled `domains.txt`, located in your Pulumi project folder, and which contains the following:

```nohighlight
domain1.com
domain2.com
domain3.com
```

You could first create a file in your project folder to hold functions associated with creating Pulumi/Linode resources. Here is an example of such a file, titled `linode_domain_maker.py`:

```python
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

```

Then, using the following example `__main__.py`, running `pulumi up` will create a host Linode, domain records which point to its public IPv4 address for each domain in the file, and apply tags to all of these resources for organization and tracking:

```python
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

```

If domains are later removed or added to the file, running `pulumi up` again will project the resultant resource changes, then add or remove records as required after the changes are confirmed. You can find all of the files of this example project [here](https://github.com/bbiggerr/pulumi-linode-dns-example).


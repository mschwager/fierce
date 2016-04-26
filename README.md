# Fierce

Fierce is a `DNS` reconnaissance tool for locating non-contiguous IP space.

Useful links:

* [Domain Name System (DNS)](https://en.wikipedia.org/wiki/Domain_Name_System)
  * [Domain Names - Concepts and Facilities](https://tools.ietf.org/html/rfc1034)
  * [Domain Names - Implementation and Specification](https://tools.ietf.org/html/rfc1035)
  * [Threat Analysis of the Domain Name System (DNS)](https://tools.ietf.org/html/rfc3833)
* [Name Servers (NS)](https://en.wikipedia.org/wiki/Domain_Name_System#Name_servers)
* [State of Authority Record (SOA)](https://en.wikipedia.org/wiki/List_of_DNS_record_types#SOA)
* [Zone Transfer](https://en.wikipedia.org/wiki/DNS_zone_transfer)
  * [DNS Zone Transfer Protocol (AXFR)](https://tools.ietf.org/html/rfc5936)
  * [Incremental Zone Transfer in DNS (IXFR)](https://tools.ietf.org/html/rfc1995)
* [Wildcard DNS Record](https://en.wikipedia.org/wiki/Wildcard_DNS_record)

# Overview

First things first, `fierce` was originally written by RSnake and the guys over
at http://ha.ckers.org/. All credit for the original idea goes to RSnake. This
is a conversion to Python to simplify and modernize the codebase. My hope is
that the community will find it useful, help improve upon it, and learn
something new in the process.

The original description was very apt, so I'll include it here:

> Fierce is a semi-lightweight scanner that helps locate non-contiguous
> IP space and hostnames against specified domains. It's really meant
> as a pre-cursor to nmap, unicornscan, nessus, nikto, etc, since all 
> of those require that you already know what IP space you are looking 
> for. This does not perform exploitation and does not scan the whole 
> internet indiscriminately. It is meant specifically to locate likely 
> targets both inside and outside a corporate network. Because it uses 
> DNS primarily you will often find mis-configured networks that leak 
> internal address space. That's especially useful in targeted malware.

# Installing

```
$ pip install git+https://github.com/mschwager/fierce
```

OR

```
$ git clone https://github.com/mschwager/fierce.git
$ pip install -r requirements.txt
```

# Using

Let's start with something basic:

```
$ fierce --domain google.com --subdomains accounts admin ads --traverse 1
NS: ns2.google.com. ns3.google.com. ns4.google.com. ns1.google.com.
SOA: ns4.google.com. (216.239.38.10)
Zone: failure
Wildcard: failure
Found: accounts.google.com (172.217.0.109)
Nearby:
{'172.217.0.108': 'ord08s11-in-f12.1e100.net.',
 '172.217.0.109': 'ord08s11-in-f13.1e100.net.',
 '172.217.0.110': 'ord08s11-in-f14.1e100.net.'}
Found: admin.google.com (206.181.8.241)
Found: ads.google.com (206.181.8.241)
```

We can filter our nearby searching by specifying `--search`. This allows us
to consider nearby alias domains. For example, if we're looking at
`facebook.com` we may also consider `fb.net` and `fb.com`:

```
$ fierce --domain facebook.com --subdomains admin --traverse 10 --search fb.com fb.net
```

We can exchange speed for breadth with the `--wide` flag which will look for
nearby domains on all IPs on the Class C of a matching domain:

```
$ fierce --domain facebook.com --wide
```

Zone transfers are rare these days, but they give us the keys to the DNS castle.
[zonetransfer.me](https://digi.ninja/projects/zonetransferme.php) is a very
useful service for testing for and learning about zone transfers:

```
$ fierce --domain zonetransfer.me
NS: nsztm2.digi.ninja. nsztm1.digi.ninja.
SOA: nsztm1.digi.ninja. (81.4.108.41)
Zone: success
{<DNS name @>: '@ 7200 IN SOA nsztm1.digi.ninja. robin.digi.ninja. 2014101603 '
               '172800 900 1209600 3600\n'
...
```

To save the results to a file for later use we can simply redirect output:

```
$ fierce --domain zonetransfer.me > output.txt
```

Internal networks will often have large blocks of contiguous IP space assigned.
We can scan those as well:

```
$ fierce --dns-servers 10.0.0.1 --range 10.0.0.0/24
```

Check out `--help` for further information:

```
$ fierce --help
```

# TODO

* Implement `connect` functionality
* Provide multiprocessing capabilities

# Fierce

[![CI](https://github.com/mschwager/fierce/actions/workflows/ci.yml/badge.svg)](https://github.com/mschwager/fierce/actions/workflows/ci.yml)
[![Python Versions](https://img.shields.io/pypi/pyversions/fierce.svg)](https://img.shields.io/pypi/pyversions/fierce.svg)
[![PyPI Version](https://img.shields.io/pypi/v/fierce.svg)](https://img.shields.io/pypi/v/fierce.svg)

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

First, credit where credit is due, `fierce` was
[originally written](https://github.com/mschwager/fierce/blob/master/scripts/fierce.pl)
by RSnake along with others at http://ha.ckers.org/. This is simply a
conversion to Python 3 to simplify and modernize the codebase.

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
$ python -m pip install fierce
$ fierce -h
```

OR

```
$ git clone https://github.com/mschwager/fierce.git
$ cd fierce
$ python -m pip install dnspython==1.16.0
$ python fierce/fierce.py -h
```

# Using

Let's start with something basic:

```
$ fierce --domain google.com --subdomains accounts admin ads
```

Traverse IPs near discovered domains to search for contiguous blocks with the
`--traverse` flag:

```
$ fierce --domain facebook.com --subdomains admin --traverse 10
```

Limit nearby IP traversal to certain domains with the `--search` flag:

```
$ fierce --domain facebook.com --subdomains admin --search fb.com fb.net
```

Attempt an `HTTP` connection on domains discovered with the `--connect` flag:

```
$ fierce --domain stackoverflow.com --subdomains mail --connect
```

Exchange speed for breadth with the `--wide` flag, which looks for nearby
domains on all IPs of the [/24](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing#IPv4_CIDR_blocks)
of a discovered domain:

```
$ fierce --domain facebook.com --wide
```

Zone transfers are rare these days, but they give us the keys to the DNS castle.
[zonetransfer.me](https://digi.ninja/projects/zonetransferme.php) is a very
useful service for testing for and learning about zone transfers:

```
$ fierce --domain zonetransfer.me
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

# Developing

First, install [`poetry`](https://python-poetry.org/docs/#installation) and development packages:

```
$ poetry install --with dev
```

## Testing

```
$ poetry run pytest
```

## Linting

```
$ poetry run flake8
```

## Coverage

```
$ poetry run pytest --cov
```

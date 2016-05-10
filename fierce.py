#!/usr/bin/env python3

import argparse
import functools
import http.client
import ipaddress
import os
import pprint
import random
import socket
import time

import dns.name
import dns.query
import dns.resolver
import dns.reversename
import dns.zone

def find_subdomain_list_file(filename):
    # First check the list directory relative to where we are. This
    # will typically happen if they simply cloned the Github repository
    filename_path = os.path.join(os.path.dirname(__file__), "lists", filename)
    if os.path.exists(filename_path):
        return os.path.abspath(filename_path)

    try:
        import pkg_resources
    except ImportError:
        return filename

    # If the relative check failed then attempt to find the list file
    # in the pip package directory. This will typically happen on pip package
    # installs (duh)
    #
    # Here's how pip itself handles this:
    #
    #     https://github.com/pypa/pip/blob/master/pip/commands/show.py
    #
    try:
        fierce = pkg_resources.get_distribution('fierce')
    except pkg_resources.DistributionNotFound:
        return filename

    if isinstance(fierce, pkg_resources.Distribution):
        paths = []
        if fierce.has_metadata('RECORD'):
            lines = fierce.get_metadata_lines('RECORD')
            paths = [l.split(',')[0] for l in lines]
            paths = [os.path.join(fierce.location, p) for p in paths]
        elif fierce.has_metadata('installed-files.txt'):
            lines = fierce.get_metadata_lines('installed-files.txt')
            paths = [l for l in lines]
            paths = [os.path.join(fierce.egg_info, p) for p in paths]

        for p in paths:
            if filename == os.path.basename(p):
                return p

    # If we couldn't find anything just return the original list file
    return filename

def head_request(url):
    conn = http.client.HTTPConnection(url)

    try:
        conn.request("HEAD", "/")
    except socket.gaierror:
        return []

    resp = conn.getresponse()
    conn.close()

    return resp.getheaders()

def concatenate_subdomains(domain, subdomains):
    result = dns.name.Name(tuple(subdomains) + domain.labels)

    if not result.is_absolute():
        result = result.concatenate(dns.name.root)

    return result

def query(resolver, domain, record_type='A'):
    try:
        resp = resolver.query(domain, record_type, raise_on_no_answer=False)
        if resp.response.answer:
            return resp

        # If we don't receive an answer from our current resolver let's
        # assume we received information on nameservers we can use and
        # perform the same query with those nameservers
        if resp.response.additional and resp.response.authority:
            ns = [
                rdata.address
                for additionals in resp.response.additional
                for rdata in additionals.items
            ]
            resolver.nameservers = ns
            return query(resolver, domain, record_type)

        return None
    except (dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
        return None

def reverse_query(resolver, ip):
    return query(resolver, dns.reversename.from_address(ip), record_type='PTR')

def zone_transfer(address, domain):
    try:
        return dns.zone.from_xfr(dns.query.xfr(address, domain))
    except (ConnectionResetError, dns.exception.FormError):
        return None

def get_class_c_network(ip):
    ip = int(ip)
    floored = ipaddress.ip_address(ip - (ip % (2**8)))
    class_c = ipaddress.IPv4Network('{}/24'.format(floored))

    return class_c

def traverse_expander(ip, n=5):
    class_c = get_class_c_network(ip)

    result = [ipaddress.IPv4Address(ip + i) for i in range(-n, n + 1)]
    result = [i for i in result if i in class_c]

    return result

def wide_expander(ip):
    class_c = get_class_c_network(ip)

    result = list(class_c)

    return result

def search_filter(domains, address):
    return any(domain in address for domain in domains)

def find_nearby(resolver, ips, filter_func=None):
    reversed_ips = {str(i): reverse_query(resolver, str(i)) for i in ips}
    reversed_ips = {k: v for k, v in reversed_ips.items() if v is not None}

    if filter_func:
        reversed_ips = {k: v for k, v in reversed_ips.items() if filter_func(v[0].to_text())}

    if not reversed_ips:
        return

    print("Nearby:")
    pprint.pprint({k: v[0].to_text() for k, v in reversed_ips.items()})

def fierce(**kwargs):
    resolver = dns.resolver.Resolver()

    nameservers = None
    if kwargs.get('dns_servers'):
        nameservers = kwargs['dns_servers']
    elif kwargs.get('dns_file'):
        nameservers = [ns.strip() for ns in open(kwargs["dns_file"]).readlines()]

    if nameservers:
        resolver.nameservers = nameservers

    if kwargs.get("range"):
        internal_range = ipaddress.IPv4Network(kwargs.get("range"))
        find_nearby(resolver, list(internal_range))

    if not kwargs.get("domain"):
        return

    domain = dns.name.from_text(kwargs['domain'])
    if not domain.is_absolute():
        domain = domain.concatenate(dns.name.root)

    ns = query(resolver, domain, record_type='NS')
    domain_name_servers = [n.to_text() for n in ns]
    print("NS: {}".format(" ".join(domain_name_servers)))

    soa = query(resolver, domain, record_type='SOA')
    soa_mname = soa[0].mname
    master = query(resolver, soa_mname, record_type='A')
    master_address = master[0].address
    print("SOA: {} ({})".format(soa_mname, master_address))

    zone = zone_transfer(master_address, domain)
    print("Zone: {}".format("success" if zone else "failure"))
    if zone:
        pprint.pprint({k: v.to_text(k) for k, v in zone.items()})
        return

    random_subdomain = str(random.randint(1e10, 1e11))
    random_domain = concatenate_subdomains(domain, [random_subdomain])
    wildcard = query(resolver, random_domain, record_type='A')
    print("Wildcard: {}".format("success" if wildcard else "failure"))

    if kwargs.get('subdomains'):
        subdomains = kwargs["subdomains"]
    else:
        subdomains = [sd.strip() for sd in open(kwargs["subdomain_file"]).readlines()]

    visited = set()

    for subdomain in subdomains:
        url = concatenate_subdomains(domain, [subdomain])
        record = query(resolver, url, record_type='A')

        if record is None:
            continue

        ip = ipaddress.IPv4Address(record[0].address)
        print("Found: {} ({})".format(url, ip))

        if kwargs.get('connect') and not ip.is_private:
            headers = head_request(str(ip))
            if headers:
                print("HTTP connected:")
                pprint.pprint(headers)

        if kwargs.get("wide"):
            ips = wide_expander(ip)
        elif kwargs.get("traverse"):
            ips = traverse_expander(ip, kwargs["traverse"])
        else:
            continue

        filter_func = None
        if kwargs.get("search"):
            filter_func = functools.partial(search_filter, kwargs["search"])

        ips = set(ips) - set(visited)
        visited |= ips

        find_nearby(resolver, ips, filter_func=filter_func)

        if kwargs.get("delay"):
            time.sleep(kwargs["delay"])

def parse_args():
    p = argparse.ArgumentParser(description=
        '''
        A DNS reconnaissance tool for locating non-contiguous IP space.
        ''', formatter_class=argparse.RawTextHelpFormatter)

    p.add_argument('--domain', action='store',
        help='domain name to test')
    p.add_argument('--connect', action='store_true',
        help='attempt HTTP connection to non-RFC 1918 hosts')
    p.add_argument('--wide', action='store_true',
        help='scan entire class c of discovered records')
    p.add_argument('--traverse', action='store', type=int, default=5,
        help='scan IPs near discovered records, this won\'t enter adjacent class c\'s')
    p.add_argument('--search', action='store', nargs='+',
        help='filter on these domains when expanding lookup')
    p.add_argument('--range', action='store',
        help='scan an internal IP range, use cidr notation')
    p.add_argument('--delay', action='store', type=float, default=None,
        help='time to wait between lookups')

    subdomain_group = p.add_mutually_exclusive_group()
    subdomain_group.add_argument('--subdomains', action='store', nargs='+',
        help='use these subdomains')
    subdomain_group.add_argument('--subdomain-file', action='store',
        default="default.txt",
        help='use subdomains specified in this file (one per line)')

    dns_group = p.add_mutually_exclusive_group()
    dns_group.add_argument('--dns-servers', action='store', nargs='+',
        help='use these dns servers for reverse lookups')
    dns_group.add_argument('--dns-file', action='store',
        help='use dns servers specified in this file for reverse lookups (one per line)')

    args = p.parse_args()

    # Attempt to intelligently find the subdomain list depending on
    # how this library was installed.
    if args.subdomain_file and not os.path.exists(args.subdomain_file):
        args.subdomain_file = find_subdomain_list_file(args.subdomain_file)

    return args

def main():
    args = parse_args()

    fierce(**vars(args))

if __name__ == "__main__":
    main()

#!/usr/bin/env python

import os
import textwrap
import unittest

import dns.resolver

from pyfakefs import fake_filesystem_unittest

from fierce import fierce


class TestFilesystem(fake_filesystem_unittest.TestCase):

    def setUp(self):
        self.setUpPyfakefs()

    def tearDown(self):
        # It is no longer necessary to add self.tearDownPyfakefs()
        pass

    def test_update_resolver_nameservers_empty_no_file(self):
        nameserver_filename = None
        nameservers = []

        resolver = dns.resolver.Resolver()

        expected = resolver.nameservers

        result = fierce.update_resolver_nameservers(
            resolver,
            nameservers,
            nameserver_filename
        )

        assert expected == result.nameservers

    def test_update_resolver_nameservers_single_nameserver_no_file(self):
        nameserver_filename = None
        nameservers = ['192.168.1.1']

        resolver = dns.resolver.Resolver()

        result = fierce.update_resolver_nameservers(
            resolver,
            nameservers,
            nameserver_filename
        )

        expected = nameservers
        assert expected == result.nameservers

    def test_update_resolver_nameservers_multiple_nameservers_no_file(self):
        nameserver_filename = None
        nameservers = ['192.168.1.1', '192.168.1.2']

        resolver = dns.resolver.Resolver()

        result = fierce.update_resolver_nameservers(
            resolver,
            nameservers,
            nameserver_filename
        )

        expected = nameservers
        assert expected == result.nameservers

    def test_update_resolver_nameservers_no_nameserver_use_file(self):
        nameserver_filename = os.path.join("directory", "nameservers")
        nameservers = []
        contents = textwrap.dedent("""
        nameserver1
        nameserver2
        nameserver3
        """.strip())

        self.fs.create_file(
            nameserver_filename,
            contents=contents
        )

        resolver = dns.resolver.Resolver()

        result = fierce.update_resolver_nameservers(
            resolver,
            nameservers,
            nameserver_filename
        )

        expected = contents.split()
        assert expected == result.nameservers

    def test_update_resolver_nameservers_prefer_nameservers_over_file(self):
        nameserver_filename = os.path.join("directory", "nameservers")
        nameservers = ['192.168.1.1', '192.168.1.2']
        contents = textwrap.dedent("""
        nameserver1
        nameserver2
        nameserver3
        """.strip())

        self.fs.create_file(
            nameserver_filename,
            contents=contents
        )

        resolver = dns.resolver.Resolver()

        result = fierce.update_resolver_nameservers(
            resolver,
            nameservers,
            nameserver_filename
        )

        expected = nameservers
        assert expected == result.nameservers

    def test_get_subdomains_empty_no_file(self):
        subdomain_filename = None
        subdomains = []

        result = fierce.get_subdomains(
            subdomains,
            subdomain_filename
        )

        expected = subdomains
        assert expected == result

    def test_get_subdomains_single_subdomain_no_file(self):
        subdomain_filename = None
        subdomains = ['subdomain.domain.com']

        result = fierce.get_subdomains(
            subdomains,
            subdomain_filename
        )

        expected = subdomains
        assert expected == result

    def test_get_subdomains_multiple_subdomains_no_file(self):
        subdomain_filename = None
        subdomains = ['192.168.1.1', '192.168.1.2']

        result = fierce.get_subdomains(
            subdomains,
            subdomain_filename
        )

        expected = subdomains
        assert expected == result

    def test_get_subdomains_no_subdomains_use_file(self):
        subdomain_filename = os.path.join("directory", "subdomains")
        subdomains = []
        contents = textwrap.dedent("""
        sd1.domain.com
        sd2.domain.com
        sd3.domain.com
        """.strip())

        self.fs.create_file(
            subdomain_filename,
            contents=contents
        )

        result = fierce.get_subdomains(
            subdomains,
            subdomain_filename
        )

        expected = contents.split()
        assert expected == result

    def test_get_subdomains_prefer_subdomains_over_file(self):
        subdomain_filename = os.path.join("directory", "subdomains")
        subdomains = ['192.168.1.1', '192.168.1.2']
        contents = textwrap.dedent("""
        sd1.domain.com
        sd2.domain.com
        sd3.domain.com
        """.strip())

        self.fs.create_file(
            subdomain_filename,
            contents=contents
        )

        result = fierce.get_subdomains(
            subdomains,
            subdomain_filename
        )

        expected = subdomains
        assert expected == result


if __name__ == "__main__":
    unittest.main()

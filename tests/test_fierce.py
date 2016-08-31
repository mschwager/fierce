#!/usr/bin/env python

import ipaddress
import unittest

import dns.name

import fierce


class TestFierce(unittest.TestCase):

    def test_concatenate_subdomains_empty(self):
        domain = dns.name.from_text("example.com.")
        subdomains = []

        result = fierce.concatenate_subdomains(domain, subdomains)
        expected = dns.name.from_text("example.com.")

        self.assertEqual(expected, result)

    def test_concatenate_subdomains_single_subdomain(self):
        domain = dns.name.from_text("example.com.")
        subdomains = ["sd1"]

        result = fierce.concatenate_subdomains(domain, subdomains)
        expected = dns.name.from_text("sd1.example.com.")

        self.assertEqual(expected, result)

    def test_concatenate_subdomains_multiple_subdomains(self):
        domain = dns.name.from_text("example.com.")
        subdomains = ["sd1", "sd2"]

        result = fierce.concatenate_subdomains(domain, subdomains)
        expected = dns.name.from_text("sd1.sd2.example.com.")

        self.assertEqual(expected, result)

    def test_concatenate_subdomains_makes_root(self):
        # Domain is missing '.' at the end
        domain = dns.name.from_text("example.com")
        subdomains = []

        result = fierce.concatenate_subdomains(domain, subdomains)
        expected = dns.name.from_text("example.com.")

        self.assertEqual(expected, result)

    def test_concatenate_subdomains_single_sub_subdomain(self):
        domain = dns.name.from_text("example.com.")
        subdomains = ["sd1.sd2"]

        result = fierce.concatenate_subdomains(domain, subdomains)
        expected = dns.name.from_text("sd1.sd2.example.com.")

        self.assertEqual(expected, result)

    def test_concatenate_subdomains_multiple_sub_subdomain(self):
        domain = dns.name.from_text("example.com.")
        subdomains = ["sd1.sd2", "sd3.sd4"]

        result = fierce.concatenate_subdomains(domain, subdomains)
        expected = dns.name.from_text("sd1.sd2.sd3.sd4.example.com.")

        self.assertEqual(expected, result)

    def test_traverse_expander_basic(self):
        ip = ipaddress.IPv4Address('192.168.1.1')
        expand = 1

        result = fierce.traverse_expander(ip, expand)
        expected = [
            ipaddress.IPv4Address('192.168.1.0'),
            ipaddress.IPv4Address('192.168.1.1'),
            ipaddress.IPv4Address('192.168.1.2'),
        ]

        self.assertEqual(expected, result)

    def test_traverse_expander_no_cross_lower_boundary(self):
        ip = ipaddress.IPv4Address('192.168.1.1')
        expand = 2

        result = fierce.traverse_expander(ip, expand)
        expected = [
            ipaddress.IPv4Address('192.168.1.0'),
            ipaddress.IPv4Address('192.168.1.1'),
            ipaddress.IPv4Address('192.168.1.2'),
            ipaddress.IPv4Address('192.168.1.3'),
        ]

        self.assertEqual(expected, result)

    def test_traverse_expander_no_cross_upper_boundary(self):
        ip = ipaddress.IPv4Address('192.168.1.254')
        expand = 2

        result = fierce.traverse_expander(ip, expand)
        expected = [
            ipaddress.IPv4Address('192.168.1.252'),
            ipaddress.IPv4Address('192.168.1.253'),
            ipaddress.IPv4Address('192.168.1.254'),
            ipaddress.IPv4Address('192.168.1.255'),
        ]

        self.assertEqual(expected, result)

    def test_wide_expander_basic(self):
        ip = ipaddress.IPv4Address('192.168.1.50')

        result = fierce.wide_expander(ip)

        expected = [
            ipaddress.IPv4Address('192.168.1.{}'.format(i))
            for i in range(256)
        ]

        self.assertEqual(expected, result)

    def test_wide_expander_lower_boundary(self):
        ip = ipaddress.IPv4Address('192.168.1.0')

        result = fierce.wide_expander(ip)

        expected = [
            ipaddress.IPv4Address('192.168.1.{}'.format(i))
            for i in range(256)
        ]

        self.assertEqual(expected, result)

    def test_wide_expander_upper_boundary(self):
        ip = ipaddress.IPv4Address('192.168.1.255')

        result = fierce.wide_expander(ip)

        expected = [
            ipaddress.IPv4Address('192.168.1.{}'.format(i))
            for i in range(256)
        ]

        self.assertEqual(expected, result)


if __name__ == "__main__":
    unittest.main()

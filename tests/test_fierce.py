#!/usr/bin/env python

import ipaddress
import unittest
import unittest.mock

import dns.name
import dns.resolver

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

    def test_concatenate_subdomains_fqdn_subdomain(self):
        domain = dns.name.from_text("example.")
        subdomains = ["sd1.sd2."]

        result = fierce.concatenate_subdomains(domain, subdomains)
        expected = dns.name.from_text("sd1.sd2.example.")

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

    def test_recursive_query_basic_failure(self):
        resolver = dns.resolver.Resolver()
        domain = dns.name.from_text('example.com.')
        record_type = 'NS'

        with unittest.mock.patch.object(fierce, 'query', return_value=None) as mock_method:
            result = fierce.recursive_query(resolver, domain, record_type=record_type)

        expected = [
            unittest.mock.call(resolver, 'example.com.', record_type),
            unittest.mock.call(resolver, 'com.', record_type),
            unittest.mock.call(resolver, '', record_type),
        ]

        mock_method.assert_has_calls(expected)
        self.assertIs(result, None)

    def test_recursive_query_long_domain_failure(self):
        resolver = dns.resolver.Resolver()
        domain = dns.name.from_text('sd1.sd2.example.com.')
        record_type = 'NS'

        with unittest.mock.patch.object(fierce, 'query', return_value=None) as mock_method:
            result = fierce.recursive_query(resolver, domain, record_type=record_type)

        expected = [
            unittest.mock.call(resolver, 'sd1.sd2.example.com.', record_type),
            unittest.mock.call(resolver, 'sd2.example.com.', record_type),
            unittest.mock.call(resolver, 'example.com.', record_type),
            unittest.mock.call(resolver, 'com.', record_type),
            unittest.mock.call(resolver, '', record_type),
        ]

        mock_method.assert_has_calls(expected)
        self.assertIs(result, None)

    def test_recursive_query_basic_success(self):
        resolver = dns.resolver.Resolver()
        domain = dns.name.from_text('example.com.')
        record_type = 'NS'
        good_response = unittest.mock.MagicMock()
        side_effect = [
            None,
            good_response,
            None,
        ]

        with unittest.mock.patch.object(fierce, 'query', side_effect=side_effect) as mock_method:
            result = fierce.recursive_query(resolver, domain, record_type=record_type)

        expected = [
            unittest.mock.call(resolver, 'example.com.', record_type),
            unittest.mock.call(resolver, 'com.', record_type),
        ]

        mock_method.assert_has_calls(expected)
        self.assertEqual(result, good_response)


if __name__ == "__main__":
    unittest.main()

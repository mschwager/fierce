#!/usr/bin/env python

import ipaddress
import io
import os
import textwrap
import unittest
import unittest.mock

import dns.exception
import dns.name
import dns.resolver

from pyfakefs import fake_filesystem_unittest

from fierce import fierce


# Simply getting a dns.resolver.Answer with a specific result was
# more difficult than I'd like, let's just go with this less than
# ideal approach for now
class MockAnswer(object):
    def __init__(self, response):
        self.response = response

    def to_text(self):
        return self.response


class TestFierce(unittest.TestCase):

    def test_concatenate_subdomains_empty(self):
        domain = dns.name.from_text("example.com.")
        subdomains = []

        result = fierce.concatenate_subdomains(domain, subdomains)
        expected = dns.name.from_text("example.com.")

        assert expected == result

    def test_concatenate_subdomains_single_subdomain(self):
        domain = dns.name.from_text("example.com.")
        subdomains = ["sd1"]

        result = fierce.concatenate_subdomains(domain, subdomains)
        expected = dns.name.from_text("sd1.example.com.")

        assert expected == result

    def test_concatenate_subdomains_multiple_subdomains(self):
        domain = dns.name.from_text("example.com.")
        subdomains = ["sd1", "sd2"]

        result = fierce.concatenate_subdomains(domain, subdomains)
        expected = dns.name.from_text("sd1.sd2.example.com.")

        assert expected == result

    def test_concatenate_subdomains_makes_root(self):
        # Domain is missing '.' at the end
        domain = dns.name.from_text("example.com")
        subdomains = []

        result = fierce.concatenate_subdomains(domain, subdomains)
        expected = dns.name.from_text("example.com.")

        assert expected == result

    def test_concatenate_subdomains_single_sub_subdomain(self):
        domain = dns.name.from_text("example.com.")
        subdomains = ["sd1.sd2"]

        result = fierce.concatenate_subdomains(domain, subdomains)
        expected = dns.name.from_text("sd1.sd2.example.com.")

        assert expected == result

    def test_concatenate_subdomains_multiple_sub_subdomain(self):
        domain = dns.name.from_text("example.com.")
        subdomains = ["sd1.sd2", "sd3.sd4"]

        result = fierce.concatenate_subdomains(domain, subdomains)
        expected = dns.name.from_text("sd1.sd2.sd3.sd4.example.com.")

        assert expected == result

    def test_concatenate_subdomains_fqdn_subdomain(self):
        domain = dns.name.from_text("example.")
        subdomains = ["sd1.sd2."]

        result = fierce.concatenate_subdomains(domain, subdomains)
        expected = dns.name.from_text("sd1.sd2.example.")

        assert expected == result

    def test_default_expander(self):
        ip = ipaddress.IPv4Address('192.168.1.1')

        result = fierce.default_expander(ip)
        expected = [
            ipaddress.IPv4Address('192.168.1.1'),
        ]

        assert expected == result

    def test_traverse_expander_basic(self):
        ip = ipaddress.IPv4Address('192.168.1.1')
        expand = 1

        result = fierce.traverse_expander(ip, expand)
        expected = [
            ipaddress.IPv4Address('192.168.1.0'),
            ipaddress.IPv4Address('192.168.1.1'),
            ipaddress.IPv4Address('192.168.1.2'),
        ]

        assert expected == result

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

        assert expected == result

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

        assert expected == result

    # Upper and lower bound tests are to avoid reintroducing out of
    # bounds error from IPv4Address. (no_cross_*_boundary tests won't
    # necessarily cover this; GitHub issue #29)

    def test_traverse_expander_lower_bound_regression(self):
        ip = ipaddress.IPv4Address('0.0.0.1')
        expand = 2

        result = fierce.traverse_expander(ip, expand)
        expected = [
            ipaddress.IPv4Address('0.0.0.0'),
            ipaddress.IPv4Address('0.0.0.1'),
            ipaddress.IPv4Address('0.0.0.2'),
            ipaddress.IPv4Address('0.0.0.3')
        ]
        assert expected == result

    def test_traverse_expander_upper_bound_regression(self):
        ip = ipaddress.IPv4Address('255.255.255.254')
        expand = 2

        result = fierce.traverse_expander(ip, expand)
        expected = [
            ipaddress.IPv4Address('255.255.255.252'),
            ipaddress.IPv4Address('255.255.255.253'),
            ipaddress.IPv4Address('255.255.255.254'),
            ipaddress.IPv4Address('255.255.255.255')
        ]
        assert expected == result

    def test_wide_expander_basic(self):
        ip = ipaddress.IPv4Address('192.168.1.50')

        result = fierce.wide_expander(ip)

        expected = [
            ipaddress.IPv4Address('192.168.1.{}'.format(i))
            for i in range(256)
        ]

        assert expected == result

    def test_wide_expander_lower_boundary(self):
        ip = ipaddress.IPv4Address('192.168.1.0')

        result = fierce.wide_expander(ip)

        expected = [
            ipaddress.IPv4Address('192.168.1.{}'.format(i))
            for i in range(256)
        ]

        assert expected == result

    def test_wide_expander_upper_boundary(self):
        ip = ipaddress.IPv4Address('192.168.1.255')

        result = fierce.wide_expander(ip)

        expected = [
            ipaddress.IPv4Address('192.168.1.{}'.format(i))
            for i in range(256)
        ]

        assert expected == result

    def test_range_expander(self):
        ip = '192.168.1.0/31'

        result = fierce.range_expander(ip)

        expected = [
            ipaddress.IPv4Address('192.168.1.0'),
            ipaddress.IPv4Address('192.168.1.1'),
        ]

        assert expected == result

    def test_recursive_query_basic_failure(self):
        resolver = dns.resolver.Resolver()
        domain = dns.name.from_text('example.com.')
        record_type = 'NS'

        with unittest.mock.patch.object(fierce, 'query', return_value=None) as mock_method:
            result = fierce.recursive_query(resolver, domain, record_type=record_type)

        expected = [
            unittest.mock.call(resolver, 'example.com.', record_type, tcp=False),
            unittest.mock.call(resolver, 'com.', record_type, tcp=False),
            unittest.mock.call(resolver, '', record_type, tcp=False),
        ]

        mock_method.assert_has_calls(expected)
        assert result is None

    def test_recursive_query_long_domain_failure(self):
        resolver = dns.resolver.Resolver()
        domain = dns.name.from_text('sd1.sd2.example.com.')
        record_type = 'NS'

        with unittest.mock.patch.object(fierce, 'query', return_value=None) as mock_method:
            result = fierce.recursive_query(resolver, domain, record_type=record_type)

        expected = [
            unittest.mock.call(resolver, 'sd1.sd2.example.com.', record_type, tcp=False),
            unittest.mock.call(resolver, 'sd2.example.com.', record_type, tcp=False),
            unittest.mock.call(resolver, 'example.com.', record_type, tcp=False),
            unittest.mock.call(resolver, 'com.', record_type, tcp=False),
            unittest.mock.call(resolver, '', record_type, tcp=False),
        ]

        mock_method.assert_has_calls(expected)
        assert result is None

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
            unittest.mock.call(resolver, 'example.com.', record_type, tcp=False),
            unittest.mock.call(resolver, 'com.', record_type, tcp=False),
        ]

        mock_method.assert_has_calls(expected)
        assert result == good_response

    def test_query_nxdomain(self):
        resolver = dns.resolver.Resolver()
        domain = dns.name.from_text('example.com.')

        with unittest.mock.patch.object(resolver, 'query', side_effect=dns.resolver.NXDOMAIN()):
            result = fierce.query(resolver, domain)

        assert result is None

    def test_query_no_nameservers(self):
        resolver = dns.resolver.Resolver()
        domain = dns.name.from_text('example.com.')

        with unittest.mock.patch.object(resolver, 'query', side_effect=dns.resolver.NoNameservers()):
            result = fierce.query(resolver, domain)

        assert result is None

    def test_query_timeout(self):
        resolver = dns.resolver.Resolver()
        domain = dns.name.from_text('example.com.')

        with unittest.mock.patch.object(resolver, 'query', side_effect=dns.exception.Timeout()):
            result = fierce.query(resolver, domain)

        assert result is None

    def test_zone_transfer_connection_error(self):
        address = 'test'
        domain = dns.name.from_text('example.com.')

        with unittest.mock.patch.object(fierce.dns.zone, 'from_xfr', side_effect=ConnectionError()):
            result = fierce.zone_transfer(address, domain)

        assert result is None

    def test_zone_transfer_eof_error(self):
        address = 'test'
        domain = dns.name.from_text('example.com.')

        with unittest.mock.patch.object(fierce.dns.zone, 'from_xfr', side_effect=EOFError()):
            result = fierce.zone_transfer(address, domain)

        assert result is None

    def test_zone_transfer_timeout_error(self):
        address = 'test'
        domain = dns.name.from_text('example.com.')

        with unittest.mock.patch.object(fierce.dns.zone, 'from_xfr', side_effect=TimeoutError()):
            result = fierce.zone_transfer(address, domain)

        assert result is None

    def test_zone_transfer_form_error(self):
        address = 'test'
        domain = dns.name.from_text('example.com.')

        with unittest.mock.patch.object(fierce.dns.zone, 'from_xfr', side_effect=dns.exception.FormError()):
            result = fierce.zone_transfer(address, domain)

        assert result is None

    def test_find_nearby_empty(self):
        resolver = 'unused'
        ips = []

        result = fierce.find_nearby(resolver, ips)
        expected = {}

        assert expected == result

    def test_find_nearby_basic(self):
        resolver = 'unused'
        ips = [
            ipaddress.IPv4Address('192.168.1.0'),
            ipaddress.IPv4Address('192.168.1.1'),
        ]
        side_effect = [
            [MockAnswer('sd1.example.com.')],
            [MockAnswer('sd2.example.com.')],
        ]

        with unittest.mock.patch.object(fierce, 'reverse_query', side_effect=side_effect):
            result = fierce.find_nearby(resolver, ips)

        expected = {
            '192.168.1.0': 'sd1.example.com.',
            '192.168.1.1': 'sd2.example.com.',
        }

        assert expected == result

    def test_find_nearby_filter_func(self):
        resolver = 'unused'
        ips = [
            ipaddress.IPv4Address('192.168.1.0'),
            ipaddress.IPv4Address('192.168.1.1'),
        ]
        side_effect = [
            [MockAnswer('sd1.example.com.')],
            [MockAnswer('sd2.example.com.')],
        ]

        def filter_func(reverse_result):
            return reverse_result == 'sd1.example.com.'

        with unittest.mock.patch.object(fierce, 'reverse_query', side_effect=side_effect):
            result = fierce.find_nearby(resolver, ips, filter_func=filter_func)

        expected = {
            '192.168.1.0': 'sd1.example.com.',
        }

        assert expected == result

    def test_print_subdomain_result_basic(self):
        url = 'example.com'
        ip = '192.168.1.0'

        with io.StringIO() as stream:
            fierce.print_subdomain_result(url, ip, stream=stream)
            result = stream.getvalue()

        expected = 'Found: example.com (192.168.1.0)\n'

        assert expected == result

    def test_print_subdomain_result_nearby(self):
        url = 'example.com'
        ip = '192.168.1.0'
        nearby = {'192.168.1.1': 'nearby.com'}

        with io.StringIO() as stream:
            fierce.print_subdomain_result(url, ip, nearby=nearby, stream=stream)
            result = stream.getvalue()

        expected = textwrap.dedent('''
            Found: example.com (192.168.1.0)
            Nearby:
            {'192.168.1.1': 'nearby.com'}
        ''').lstrip()

        assert expected == result

    def test_print_subdomain_result_http_header(self):
        url = 'example.com'
        ip = '192.168.1.0'
        http_connection_headers = {'HTTP HEADER': 'value'}

        with io.StringIO() as stream:
            fierce.print_subdomain_result(
                url,
                ip,
                http_connection_headers=http_connection_headers,
                stream=stream
            )
            result = stream.getvalue()

        expected = textwrap.dedent('''
            Found: example.com (192.168.1.0)
            HTTP connected:
            {'HTTP HEADER': 'value'}
        ''').lstrip()

        assert expected == result

    def test_print_subdomain_result_both(self):
        url = 'example.com'
        ip = '192.168.1.0'
        http_connection_headers = {'HTTP HEADER': 'value'}
        nearby = {'192.168.1.1': 'nearby.com'}

        with io.StringIO() as stream:
            fierce.print_subdomain_result(
                url,
                ip,
                http_connection_headers=http_connection_headers,
                nearby=nearby,
                stream=stream
            )
            result = stream.getvalue()

        expected = textwrap.dedent('''
            Found: example.com (192.168.1.0)
            HTTP connected:
            {'HTTP HEADER': 'value'}
            Nearby:
            {'192.168.1.1': 'nearby.com'}
        ''').lstrip()

        assert expected == result

    def test_unvisited_closure_empty(self):
        unvisited = fierce.unvisited_closure()
        ips = set()

        result = unvisited(ips)
        expected = set()

        assert expected == result

    def test_unvisited_closure_empty_intersection(self):
        unvisited = fierce.unvisited_closure()

        unvisited(set([1, 2, 3]))
        result = unvisited(set([4, 5, 6]))
        expected = set([4, 5, 6])

        assert expected == result

    def test_unvisited_closure_overlapping_intersection(self):
        unvisited = fierce.unvisited_closure()

        unvisited(set([1, 2, 3]))
        result = unvisited(set([2, 3, 4]))
        expected = set([4])

        assert expected == result

    def test_search_filter_empty(self):
        domains = []
        address = 'test.example.com'

        result = fierce.search_filter(domains, address)

        assert not result

    def test_search_filter_true(self):
        domains = ['example.com']
        address = 'test.example.com'

        result = fierce.search_filter(domains, address)

        assert result

    def test_search_filter_false(self):
        domains = ['not.com']
        address = 'test.example.com'

        result = fierce.search_filter(domains, address)

        assert not result


class TestArgumentParsing(fake_filesystem_unittest.TestCase):

    def test_parse_args_basic(self):
        domain = 'example.com'

        args = fierce.parse_args([
            '--domain', domain,
        ])
        result = args.domain
        expected = domain

        assert expected == result

    def test_parse_args_included_list_file(self):
        filename = '5000.txt'

        args = fierce.parse_args([
            '--domain', 'example.com',
            '--subdomain-file', filename,

        ])
        result = args.subdomain_file
        expected = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'fierce',
            'lists',
            filename,
        )
        exists = os.path.exists(result)

        assert expected == result
        assert exists

    def test_parse_args_missing_list_file(self):
        filename = 'missing.txt'

        args = fierce.parse_args([
            '--domain', 'example.com',
            '--subdomain-file', filename,

        ])
        result = args.subdomain_file
        expected = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'fierce',
            'lists',
            filename,
        )
        exists = os.path.exists(result)

        assert expected == result
        assert not exists

    def test_parse_args_custom_list_file(self):
        self.setUpPyfakefs()

        filename = os.path.join('test', 'custom.txt')
        self.fs.create_file(
            filename,
            contents='subdomain'
        )

        args = fierce.parse_args([
            '--domain', 'example.com',
            '--subdomain-file', filename,
        ])
        result = args.subdomain_file
        expected = filename
        exists = os.path.exists(result)

        assert expected == result
        assert exists


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python

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

if __name__ == "__main__":
    unittest.main()

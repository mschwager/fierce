#!/usr/bin/env python
"""Regression tests for the documented fatal path of fierce.range_expander.

The defect: range_expander() only caught ipaddress.AddressValueError, so an
invalid netmask (ipaddress.NetmaskValueError) or a CIDR with host bits set
(a plain ValueError) escaped as an uncaught exception instead of reaching the
documented `Invalid IPv4 CIDR: ...` message and exit code -1.

These tests call the real product functions only. No dependency is stubbed and
no algorithm is re-implemented: input validation is delegated to the standard
library through the product code itself.
"""

import contextlib
import io
import sys
import unittest
from unittest import mock

from fierce import fierce


class TestRangeValidation(unittest.TestCase):

    def fatal_outcome(self, callable_):
        """Run callable_, returning (SystemExit.code, stdout, escaped type).

        A non-SystemExit exception escaping the product call is reported
        through the return value so that the assertions below fail with a
        readable diff, instead of turning the test into an opaque error.
        """
        buffer = io.StringIO()
        code = None
        escaped = "None"
        with contextlib.redirect_stdout(buffer):
            try:
                callable_()
            except SystemExit as exc:
                code = exc.code
            except BaseException as exc:  # the uncaught defect lands here
                escaped = type(exc).__name__
        return code, buffer.getvalue(), escaped

    def assert_fatal_invalid_cidr(self, cidr):
        code, output, escaped = self.fatal_outcome(
            lambda: fierce.range_expander(cidr))
        self.assertEqual(escaped, "None")
        self.assertEqual(code, -1)
        self.assertEqual(output, "Invalid IPv4 CIDR: {!r}\n".format(cidr))

    def test_invalid_netmask_length(self):
        self.assert_fatal_invalid_cidr("10.0.0.0/33")

    def test_invalid_netmask_text(self):
        self.assert_fatal_invalid_cidr("10.0.0.0/abc")

    def test_host_bits_remain_strict(self):
        self.assert_fatal_invalid_cidr("10.0.0.1/24")

    def test_invalid_address(self):
        for cidr in ("not-a-cidr", "10.0.0.256/24", "10.0.0.0/-1"):
            with self.subTest(cidr=cidr):
                self.assert_fatal_invalid_cidr(cidr)

    def test_valid_small_range_expands(self):
        result = fierce.range_expander("10.0.0.0/30")
        self.assertEqual(
            [str(ip) for ip in result],
            ["10.0.0.0", "10.0.0.1", "10.0.0.2", "10.0.0.3"],
        )

    def test_single_host_range(self):
        result = fierce.range_expander("10.0.0.1/32")
        self.assertEqual([str(ip) for ip in result], ["10.0.0.1"])

    def test_main_rejects_invalid_range_from_argv(self):
        argv = ["fierce", "--range", "10.0.0.0/33"]
        with mock.patch.object(sys, "argv", argv):
            code, output, escaped = self.fatal_outcome(fierce.main)
        self.assertEqual(escaped, "None")
        self.assertEqual(code, -1)
        self.assertEqual(output, "Invalid IPv4 CIDR: '10.0.0.0/33'\n")


if __name__ == "__main__":
    unittest.main()

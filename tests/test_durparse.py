import io
import os
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from decimal import Decimal
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from durparse.cli import format_human, main, parse_duration  # noqa: E402


def run(argv, stdin=None):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        if stdin is not None:
            with mock.patch("sys.stdin", io.StringIO(stdin)):
                code = main(argv)
        else:
            code = main(argv)
    return code, out.getvalue(), err.getvalue()


class TestParse(unittest.TestCase):
    def test_cases(self):
        cases = {"1h30m": 5400, "2d 4h": 187200, "90s": 90, "1.5h": 5400,
                 "1w2d": 777600, "01:30:45": 5445, "5:30": 330, "45": 45,
                 "1 hour 30 minutes": 5400, "500ms": Decimal("0.5"),
                 "1H": 3600, "1d, 1h": 90000, ".5m": 30}
        for text, want in cases.items():
            self.assertEqual(parse_duration(text), Decimal(want), text)

    def test_errors(self):
        for bad in ["", "   ", "abc", "1x", "1h30", "h", "1h 2", "1:2:3:4", "-5s"]:
            with self.assertRaises(ValueError, msg=bad):
                parse_duration(bad)


class TestHuman(unittest.TestCase):
    def test_human(self):
        self.assertEqual(format_human(Decimal(5400)), "1h 30m")
        self.assertEqual(format_human(Decimal(0)), "0s")
        self.assertEqual(format_human(Decimal(90061)), "1d 1h 1m 1s")
        self.assertEqual(format_human(Decimal("0.5")), "500ms")


class TestCli(unittest.TestCase):
    def test_default_seconds(self):
        self.assertEqual(run(["1h30m"]), (0, "5400\n", ""))

    def test_multiple_args(self):
        self.assertEqual(run(["90s", "1m"])[1], "90\n60\n")

    def test_to(self):
        self.assertEqual(run(["--to", "ms", "1.5s"])[1], "1500\n")
        self.assertEqual(run(["--to", "m", "90s"])[1], "1.5\n")
        self.assertEqual(run(["--to", "h", "1h30m"])[1], "1.5\n")
        self.assertEqual(run(["--to", "d", "36h"])[1], "1.5\n")
        self.assertEqual(run(["--to", "s", "2m"])[1], "120\n")

    def test_human(self):
        self.assertEqual(run(["--human", "90m"])[1], "1h 30m\n")
        self.assertEqual(run(["--human", "01:30:45"])[1], "1h 30m 45s\n")

    def test_stdin(self):
        self.assertEqual(run([], stdin="1m\n\n2m\n"), (0, "60\n120\n", ""))

    def test_error(self):
        code, out, err = run(["1m", "bogus"])
        self.assertEqual(code, 1)
        self.assertEqual(out, "60\n")
        self.assertIn("bogus", err)


if __name__ == "__main__":
    unittest.main()

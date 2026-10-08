"""Command line interface and parser for durparse."""
import argparse
import re
import sys
from decimal import Decimal, InvalidOperation

UNITS = {
    "ms": Decimal("0.001"), "msec": Decimal("0.001"), "msecs": Decimal("0.001"),
    "millisecond": Decimal("0.001"), "milliseconds": Decimal("0.001"),
    "s": Decimal(1), "sec": Decimal(1), "secs": Decimal(1),
    "second": Decimal(1), "seconds": Decimal(1),
    "m": Decimal(60), "min": Decimal(60), "mins": Decimal(60),
    "minute": Decimal(60), "minutes": Decimal(60),
    "h": Decimal(3600), "hr": Decimal(3600), "hrs": Decimal(3600),
    "hour": Decimal(3600), "hours": Decimal(3600),
    "d": Decimal(86400), "day": Decimal(86400), "days": Decimal(86400),
    "w": Decimal(604800), "wk": Decimal(604800), "wks": Decimal(604800),
    "week": Decimal(604800), "weeks": Decimal(604800),
}
TO_DIVISORS = {"ms": Decimal("0.001"), "s": Decimal(1), "m": Decimal(60),
               "h": Decimal(3600), "d": Decimal(86400)}

_NUM = r"(?:\d+(?:\.\d*)?|\.\d+)"
_TOKEN = re.compile(r"\s*(" + _NUM + r")\s*([A-Za-z]*)\s*,?")
_CLOCK = re.compile(r"^(?:(\d+):)?(\d+):(" + _NUM + r")$")


def parse_duration(text):
    """Return total seconds (Decimal). Raise ValueError on invalid input."""
    s = text.strip()
    if not s:
        raise ValueError("empty duration")
    m = _CLOCK.match(s)
    if m:
        h, mi, sec = m.groups()
        return Decimal(h or 0) * 3600 + Decimal(mi) * 60 + Decimal(sec)
    pos, total, seen = 0, Decimal(0), False
    while pos < len(s):
        m = _TOKEN.match(s, pos)
        if not m or m.end() == pos:
            raise ValueError("invalid duration: %r" % text)
        num, unit = m.groups()
        if unit == "":
            # a bare number is seconds, but only when it is the whole input
            if seen or m.end() != len(s):
                raise ValueError("missing unit in %r" % text)
            factor = Decimal(1)
        else:
            factor = UNITS.get(unit.lower())
            if factor is None:
                raise ValueError("unknown unit %r in %r" % (unit, text))
        try:
            total += Decimal(num) * factor
        except InvalidOperation:
            raise ValueError("invalid number in %r" % text)
        seen = True
        pos = m.end()
    return total


def _fmt(d):
    d = d.normalize() if d != d.to_integral_value() else d.to_integral_value()
    return format(d, "f")


def format_human(seconds):
    """Normalize seconds to a string like '1d 2h 30m 5s'."""
    if seconds == 0:
        return "0s"
    ms_total = int((seconds * 1000).to_integral_value())
    parts = []
    for name, size in (("d", 86400000), ("h", 3600000), ("m", 60000), ("s", 1000)):
        n, ms_total = divmod(ms_total, size)
        if n:
            parts.append("%d%s" % (n, name))
    if ms_total:
        parts.append("%dms" % ms_total)
    return " ".join(parts)


def _convert(seconds, to):
    return _fmt(seconds / TO_DIVISORS[to])


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="durparse",
        description="Parse human duration strings (1h30m, 2d 4h, 01:30:45) "
                    "into seconds. Reads stdin lines if no arguments are given.")
    p.add_argument("durations", nargs="*", help="duration strings")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--to", choices=sorted(TO_DIVISORS), default=None,
                   help="output unit (default: s)")
    g.add_argument("--human", action="store_true",
                   help="print normalized form like '1h 30m'")
    args = p.parse_args(argv)

    items = args.durations
    if not items:
        items = [ln for ln in sys.stdin.read().splitlines() if ln.strip()]
    status = 0
    for item in items:
        try:
            secs = parse_duration(item)
        except ValueError as e:
            print("durparse: error: %s" % e, file=sys.stderr)
            status = 1
            continue
        if args.human:
            print(format_human(secs))
        else:
            print(_convert(secs, args.to or "s"))
    return status

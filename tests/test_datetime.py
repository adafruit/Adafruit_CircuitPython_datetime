# SPDX-FileCopyrightText: 2001-2021 Python Software Foundation.All rights reserved.
# SPDX-FileCopyrightText: 2000 BeOpen.com. All rights reserved.
# SPDX-FileCopyrightText: 1995-2001 Corporation for National Research Initiatives.
#                         All rights reserved.
# SPDX-FileCopyrightText: 1995-2001 Corporation for National Research Initiatives.
#                         All rights reserved.
# SPDX-FileCopyrightText: 1991-1995 Stichting Mathematisch Centrum. All rights reserved.
# SPDX-FileCopyrightText: 2021 Brent Rubell for Adafruit Industries
# SPDX-License-Identifier: Python-2.0
# Implements a subset of https://github.com/python/cpython/blob/master/Lib/test/datetimetester.py
import sys
import unittest
from test import support
from test_date import TestDate

# CPython standard implementation
from datetime import datetime as cpython_datetime
from datetime import MINYEAR, MAXYEAR

# CircuitPython subset implementation
sys.path.append("..")
from adafruit_datetime import datetime as cpy_datetime
from adafruit_datetime import timedelta
from adafruit_datetime import tzinfo
from adafruit_datetime import date
from adafruit_datetime import time
from adafruit_datetime import timezone

# TZinfo test
class FixedOffset(tzinfo):
    def __init__(self, offset, name, dstoffset=42):
        if isinstance(offset, int):
            offset = timedelta(minutes=offset)
        if isinstance(dstoffset, int):
            dstoffset = timedelta(minutes=dstoffset)
        self.__offset = offset
        self.__name = name
        self.__dstoffset = dstoffset

    def __repr__(self):
        return self.__name.lower()

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return self.__dstoffset


# =======================================================================
# Decorator for running a function in a specific timezone, correctly
# resetting it afterwards.


def run_with_tz(tz):
    def decorator(func):
        def inner(*args, **kwds):
            try:
                tzset = time.tzset
            except AttributeError:
                raise unittest.SkipTest("tzset required")
            if "TZ" in os.environ:
                orig_tz = os.environ["TZ"]
            else:
                orig_tz = None
            os.environ["TZ"] = tz
            tzset()

            # now run the function, resetting the tz on exceptions
            try:
                return func(*args, **kwds)
            finally:
                if orig_tz is None:
                    del os.environ["TZ"]
                else:
                    os.environ["TZ"] = orig_tz
                time.tzset()

        inner.__name__ = func.__name__
        inner.__doc__ = func.__doc__
        return inner

    return decorator


class SubclassDatetime(cpy_datetime):
    sub_var = 1


class TestDateTime(TestDate):
    theclass = cpy_datetime
    theclass_cpython = cpython_datetime

    def test_basic_attributes(self):
        dt = self.theclass(2002, 3, 1, 12, 0)
        dt2 = self.theclass_cpython(2002, 3, 1, 12, 0)
        # test circuitpython basic attributes
        self.assertEqual(dt.year, 2002)
        self.assertEqual(dt.month, 3)
        self.assertEqual(dt.day, 1)
        self.assertEqual(dt.hour, 12)
        self.assertEqual(dt.minute, 0)
        self.assertEqual(dt.second, 0)
        self.assertEqual(dt.microsecond, 0)
        # test circuitpython basic attributes against cpython basic attributes
        self.assertEqual(dt.year, dt2.year)
        self.assertEqual(dt.month, dt2.month)
        self.assertEqual(dt.day, dt2.day)
        self.assertEqual(dt.hour, dt2.hour)
        self.assertEqual(dt.minute, dt2.minute)
        self.assertEqual(dt.second, dt2.second)
        self.assertEqual(dt.microsecond, dt2.microsecond)

    def test_basic_attributes_nonzero(self):
        # Make sure all attributes are non-zero so bugs in
        # bit-shifting access show up.
        dt = self.theclass(2002, 3, 1, 12, 59, 59, 8000)
        self.assertEqual(dt.year, 2002)
        self.assertEqual(dt.month, 3)
        self.assertEqual(dt.day, 1)
        self.assertEqual(dt.hour, 12)
        self.assertEqual(dt.minute, 59)
        self.assertEqual(dt.second, 59)
        self.assertEqual(dt.microsecond, 8000)

    @unittest.skip("issue with startswith and ada lib.")
    def test_roundtrip(self):
        for dt in (self.theclass(1, 2, 3, 4, 5, 6, 7), self.theclass.now()):
            # Verify dt -> string -> datetime identity.
            s = repr(dt)
            self.assertTrue(s.startswith("datetime."))
            s = s[9:]
            dt2 = eval(s)
            self.assertEqual(dt, dt2)

            # Verify identity via reconstructing from pieces.
            dt2 = self.theclass(
                dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond
            )
            self.assertEqual(dt, dt2)

    @unittest.skip("isoformat not implemented")
    def test_isoformat(self):
        t = self.theclass(1, 2, 3, 4, 5, 1, 123)
        self.assertEqual(t.isoformat(), "0001-02-03T04:05:01.000123")
        self.assertEqual(t.isoformat("T"), "0001-02-03T04:05:01.000123")
        self.assertEqual(t.isoformat(" "), "0001-02-03 04:05:01.000123")
        self.assertEqual(t.isoformat("\x00"), "0001-02-03\x0004:05:01.000123")
        # bpo-34482: Check that surrogates are handled properly.
        self.assertEqual(t.isoformat("\ud800"), "0001-02-03\ud80004:05:01.000123")
        self.assertEqual(t.isoformat(timespec="hours"), "0001-02-03T04")
        self.assertEqual(t.isoformat(timespec="minutes"), "0001-02-03T04:05")
        self.assertEqual(t.isoformat(timespec="seconds"), "0001-02-03T04:05:01")
        self.assertEqual(
            t.isoformat(timespec="milliseconds"), "0001-02-03T04:05:01.000"
        )
        self.assertEqual(
            t.isoformat(timespec="microseconds"), "0001-02-03T04:05:01.000123"
        )
        self.assertEqual(t.isoformat(timespec="auto"), "0001-02-03T04:05:01.000123")
        self.assertEqual(t.isoformat(sep=" ", timespec="minutes"), "0001-02-03 04:05")
        self.assertRaises(ValueError, t.isoformat, timespec="foo")
        # bpo-34482: Check that surrogates are handled properly.
        self.assertRaises(ValueError, t.isoformat, timespec="\ud800")
        # str is ISO format with the separator forced to a blank.
        self.assertEqual(str(t), "0001-02-03 04:05:01.000123")

        t = self.theclass(1, 2, 3, 4, 5, 1, 999500, tzinfo=timezone.utc)
        self.assertEqual(
            t.isoformat(timespec="milliseconds"), "0001-02-03T04:05:01.999+00:00"
        )

        t = self.theclass(1, 2, 3, 4, 5, 1, 999500)
        self.assertEqual(
            t.isoformat(timespec="milliseconds"), "0001-02-03T04:05:01.999"
        )

        t = self.theclass(1, 2, 3, 4, 5, 1)
        self.assertEqual(t.isoformat(timespec="auto"), "0001-02-03T04:05:01")
        self.assertEqual(
            t.isoformat(timespec="milliseconds"), "0001-02-03T04:05:01.000"
        )
        self.assertEqual(
            t.isoformat(timespec="microseconds"), "0001-02-03T04:05:01.000000"
        )

        t = self.theclass(2, 3, 2)
        self.assertEqual(t.isoformat(), "0002-03-02T00:00:00")
        self.assertEqual(t.isoformat("T"), "0002-03-02T00:00:00")
        self.assertEqual(t.isoformat(" "), "0002-03-02 00:00:00")
        # str is ISO format with the separator forced to a blank.
        self.assertEqual(str(t), "0002-03-02 00:00:00")
        # ISO format with timezone
        tz = FixedOffset(timedelta(seconds=16), "XXX")
        t = self.theclass(2, 3, 2, tzinfo=tz)
        self.assertEqual(t.isoformat(), "0002-03-02T00:00:00+00:00:16")

    @unittest.skip("isoformat not implemented.")
    def test_isoformat_timezone(self):
        tzoffsets = [
            ("05:00", timedelta(hours=5)),
            ("02:00", timedelta(hours=2)),
            ("06:27", timedelta(hours=6, minutes=27)),
            ("12:32:30", timedelta(hours=12, minutes=32, seconds=30)),
            (
                "02:04:09.123456",
                timedelta(hours=2, minutes=4, seconds=9, microseconds=123456),
            ),
        ]

        tzinfos = [
            ("", None),
            ("+00:00", timezone.utc),
            ("+00:00", timezone(timedelta(0))),
        ]

        tzinfos += [
            (prefix + expected, timezone(sign * td))
            for expected, td in tzoffsets
            for prefix, sign in [("-", -1), ("+", 1)]
        ]

        dt_base = self.theclass(2016, 4, 1, 12, 37, 9)
        exp_base = "2016-04-01T12:37:09"

        for exp_tz, tzi in tzinfos:
            dt = dt_base.replace(tzinfo=tzi)
            exp = exp_base + exp_tz
            with self.subTest(tzi=tzi):
                assert dt.isoformat() == exp

    @unittest.skip("strftime not implemented in datetime")
    def test_format(self):
        dt = self.theclass(2007, 9, 10, 4, 5, 1, 123)
        self.assertEqual(dt.__format__(""), str(dt))

        with self.assertRaisesRegex(TypeError, "must be str, not int"):
            dt.__format__(123)

        # check that a derived class's __str__() gets called
        class A(self.theclass):
            def __str__(self):
                return "A"

        a = A(2007, 9, 10, 4, 5, 1, 123)
        self.assertEqual(a.__format__(""), "A")

        # check that a derived class's strftime gets called
        class B(self.theclass):
            def strftime(self, format_spec):
                return "B"

        b = B(2007, 9, 10, 4, 5, 1, 123)
        self.assertEqual(b.__format__(""), str(dt))

        for fmt in [
            "m:%m d:%d y:%y",
            "m:%m d:%d y:%y H:%H M:%M S:%S",
            "%z %Z",
        ]:
            self.assertEqual(dt.__format__(fmt), dt.strftime(fmt))
            self.assertEqual(a.__format__(fmt), dt.strftime(fmt))
            self.assertEqual(b.__format__(fmt), "B")

    @unittest.skip("ctime not implemented")
    def test_more_ctime(self):
        # Test fields that TestDate doesn't touch.
        import time

        t = self.theclass(2002, 3, 2, 18, 3, 5, 123)
        self.assertEqual(t.ctime(), "Sat Mar  2 18:03:05 2002")
        # Oops!  The next line fails on Win2K under MSVC 6, so it's commented
        # out.  The difference is that t.ctime() produces " 2" for the day,
        # but platform ctime() produces "02" for the day.  According to
        # C99, t.ctime() is correct here.
        # self.assertEqual(t.ctime(), time.ctime(time.mktime(t.timetuple())))

        # So test a case where that difference doesn't matter.
        t = self.theclass(2002, 3, 22, 18, 3, 5, 123)
        self.assertEqual(t.ctime(), time.ctime(time.mktime(t.timetuple())))

    def test_tz_independent_comparing(self):
        dt1 = self.theclass(2002, 3, 1, 9, 0, 0)
        dt2 = self.theclass(2002, 3, 1, 10, 0, 0)
        dt3 = self.theclass(2002, 3, 1, 9, 0, 0)
        self.assertEqual(dt1, dt3)
        self.assertTrue(dt2 > dt3)

        # Make sure comparison doesn't forget microseconds, and isn't done
        # via comparing a float timestamp (an IEEE double doesn't have enough
        # precision to span microsecond resolution across years 1 through 9999,
        # so comparing via timestamp necessarily calls some distinct values
        # equal).
        dt1 = self.theclass(MAXYEAR, 12, 31, 23, 59, 59, 999998)
        us = timedelta(microseconds=1)
        dt2 = dt1 + us
        self.assertEqual(dt2 - dt1, us)
        self.assertTrue(dt1 < dt2)

    @unittest.skip("not implemented - strftime")
    def test_strftime_with_bad_tzname_replace(self):
        # verify ok if tzinfo.tzname().replace() returns a non-string
        class MyTzInfo(FixedOffset):
            def tzname(self, dt):
                class MyStr(str):
                    def replace(self, *args):
                        return None

                return MyStr("name")

        t = self.theclass(2005, 3, 2, 0, 0, 0, 0, MyTzInfo(3, "name"))
        self.assertRaises(TypeError, t.strftime, "%Z")

    def test_bad_constructor_arguments(self):
        # bad years
        self.theclass(MINYEAR, 1, 1)  # no exception
        self.theclass(MAXYEAR, 1, 1)  # no exception
        self.assertRaises(ValueError, self.theclass, MINYEAR - 1, 1, 1)
        self.assertRaises(ValueError, self.theclass, MAXYEAR + 1, 1, 1)
        # bad months
        self.theclass(2000, 1, 1)  # no exception
        self.theclass(2000, 12, 1)  # no exception
        self.assertRaises(ValueError, self.theclass, 2000, 0, 1)
        self.assertRaises(ValueError, self.theclass, 2000, 13, 1)
        # bad days
        self.theclass(2000, 2, 29)  # no exception
        self.theclass(2004, 2, 29)  # no exception
        self.theclass(2400, 2, 29)  # no exception
        self.assertRaises(ValueError, self.theclass, 2000, 2, 30)
        self.assertRaises(ValueError, self.theclass, 2001, 2, 29)
        self.assertRaises(ValueError, self.theclass, 2100, 2, 29)
        self.assertRaises(ValueError, self.theclass, 1900, 2, 29)
        self.assertRaises(ValueError, self.theclass, 2000, 1, 0)
        self.assertRaises(ValueError, self.theclass, 2000, 1, 32)
        # bad hours
        self.theclass(2000, 1, 31, 0)  # no exception
        self.theclass(2000, 1, 31, 23)  # no exception
        self.assertRaises(ValueError, self.theclass, 2000, 1, 31, -1)
        self.assertRaises(ValueError, self.theclass, 2000, 1, 31, 24)
        # bad minutes
        self.theclass(2000, 1, 31, 23, 0)  # no exception
        self.theclass(2000, 1, 31, 23, 59)  # no exception
        self.assertRaises(ValueError, self.theclass, 2000, 1, 31, 23, -1)
        self.assertRaises(ValueError, self.theclass, 2000, 1, 31, 23, 60)
        # bad seconds
        self.theclass(2000, 1, 31, 23, 59, 0)  # no exception
        self.theclass(2000, 1, 31, 23, 59, 59)  # no exception
        self.assertRaises(ValueError, self.theclass, 2000, 1, 31, 23, 59, -1)
        self.assertRaises(ValueError, self.theclass, 2000, 1, 31, 23, 59, 60)
        # bad microseconds
        self.theclass(2000, 1, 31, 23, 59, 59, 0)  # no exception
        self.theclass(2000, 1, 31, 23, 59, 59, 999999)  # no exception
        self.assertRaises(ValueError, self.theclass, 2000, 1, 31, 23, 59, 59, -1)
        self.assertRaises(ValueError, self.theclass, 2000, 1, 31, 23, 59, 59, 1000000)
        # bad fold
        self.assertRaises(ValueError, self.theclass, 2000, 1, 31, fold=-1)
        self.assertRaises(ValueError, self.theclass, 2000, 1, 31, fold=2)
        # Positional fold:
        self.assertRaises(TypeError, self.theclass, 2000, 1, 31, 23, 59, 59, 0, None, 1)

    def test_hash_equality(self):
        d = self.theclass(2000, 12, 31, 23, 30, 17)
        e = self.theclass(2000, 12, 31, 23, 30, 17)
        self.assertEqual(d, e)
        self.assertEqual(hash(d), hash(e))

        dic = {d: 1}
        dic[e] = 2
        self.assertEqual(len(dic), 1)
        self.assertEqual(dic[d], 2)
        self.assertEqual(dic[e], 2)

        d = self.theclass(2001, 1, 1, 0, 5, 17)
        e = self.theclass(2001, 1, 1, 0, 5, 17)
        self.assertEqual(d, e)
        self.assertEqual(hash(d), hash(e))

        dic = {d: 1}
        dic[e] = 2
        self.assertEqual(len(dic), 1)
        self.assertEqual(dic[d], 2)
        self.assertEqual(dic[e], 2)

    def test_computations(self):
        a = self.theclass(2002, 1, 31)
        b = self.theclass(1956, 1, 31)
        diff = a - b
        self.assertEqual(diff.days, 46 * 365 + len(range(1956, 2002, 4)))
        self.assertEqual(diff.seconds, 0)
        self.assertEqual(diff.microseconds, 0)
        a = self.theclass(2002, 3, 2, 17, 6)
        millisec = timedelta(0, 0, 1000)
        hour = timedelta(0, 3600)
        day = timedelta(1)
        week = timedelta(7)
        self.assertEqual(a + hour, self.theclass(2002, 3, 2, 18, 6))
        self.assertEqual(hour + a, self.theclass(2002, 3, 2, 18, 6))
        self.assertEqual(a + 10 * hour, self.theclass(2002, 3, 3, 3, 6))
        self.assertEqual(a - hour, self.theclass(2002, 3, 2, 16, 6))
        self.assertEqual(-hour + a, self.theclass(2002, 3, 2, 16, 6))
        self.assertEqual(a - hour, a + -hour)
        self.assertEqual(a - 20 * hour, self.theclass(2002, 3, 1, 21, 6))
        self.assertEqual(a + day, self.theclass(2002, 3, 3, 17, 6))
        self.assertEqual(a - day, self.theclass(2002, 3, 1, 17, 6))
        self.assertEqual(a + week, self.theclass(2002, 3, 9, 17, 6))
        self.assertEqual(a - week, self.theclass(2002, 2, 23, 17, 6))
        self.assertEqual(a + 52 * week, self.theclass(2003, 3, 1, 17, 6))
        self.assertEqual(a - 52 * week, self.theclass(2001, 3, 3, 17, 6))
        self.assertEqual((a + week) - a, week)
        self.assertEqual((a + day) - a, day)
        self.assertEqual((a + hour) - a, hour)
        self.assertEqual((a + millisec) - a, millisec)
        self.assertEqual((a - week) - a, -week)
        self.assertEqual((a - day) - a, -day)
        self.assertEqual((a - hour) - a, -hour)
        self.assertEqual((a - millisec) - a, -millisec)
        self.assertEqual(a - (a + week), -week)
        self.assertEqual(a - (a + day), -day)
        self.assertEqual(a - (a + hour), -hour)
        self.assertEqual(a - (a + millisec), -millisec)
        self.assertEqual(a - (a - week), week)
        self.assertEqual(a - (a - day), day)
        self.assertEqual(a - (a - hour), hour)
        self.assertEqual(a - (a - millisec), millisec)
        self.assertEqual(
            a + (week + day + hour + millisec),
            self.theclass(2002, 3, 10, 18, 6, 0, 1000),
        )
        self.assertEqual(
            a + (week + day + hour + millisec), (((a + week) + day) + hour) + millisec
        )
        self.assertEqual(
            a - (week + day + hour + millisec),
            self.theclass(2002, 2, 22, 16, 5, 59, 999000),
        )
        self.assertEqual(
            a - (week + day + hour + millisec), (((a - week) - day) - hour) - millisec
        )
        # Add/sub ints or floats should be illegal
        for i in 1, 1.0:
            self.assertRaises(TypeError, lambda: a + i)
            self.assertRaises(TypeError, lambda: a - i)
            self.assertRaises(TypeError, lambda: i + a)
            self.assertRaises(TypeError, lambda: i - a)

        # delta - datetime is senseless.
        self.assertRaises(TypeError, lambda: day - a)
        # mixing datetime and (delta or datetime) via * or // is senseless
        self.assertRaises(TypeError, lambda: day * a)
        self.assertRaises(TypeError, lambda: a * day)
        self.assertRaises(TypeError, lambda: day // a)
        self.assertRaises(TypeError, lambda: a // day)
        self.assertRaises(TypeError, lambda: a * a)
        self.assertRaises(TypeError, lambda: a // a)
        # datetime + datetime is senseless
        self.assertRaises(TypeError, lambda: a + a)

    def test_more_compare(self):
        # The test_compare() inherited from TestDate covers the error cases.
        # We just want to test lexicographic ordering on the members datetime
        # has that date lacks.
        args = [2000, 11, 29, 20, 58, 16, 999998]
        t1 = self.theclass(*args)
        t2 = self.theclass(*args)
        self.assertEqual(t1, t2)
        self.assertTrue(t1 <= t2)
        self.assertTrue(t1 >= t2)
        self.assertFalse(t1 != t2)
        self.assertFalse(t1 < t2)
        self.assertFalse(t1 > t2)

        for i in range(len(args)):
            newargs = args[:]
            newargs[i] = args[i] + 1
            t2 = self.theclass(*newargs)  # this is larger than t1
            self.assertTrue(t1 < t2)
            self.assertTrue(t2 > t1)
            self.assertTrue(t1 <= t2)
            self.assertTrue(t2 >= t1)
            self.assertTrue(t1 != t2)
            self.assertTrue(t2 != t1)
            self.assertFalse(t1 == t2)
            self.assertFalse(t2 == t1)
            self.assertFalse(t1 > t2)
            self.assertFalse(t2 < t1)
            self.assertFalse(t1 >= t2)
            self.assertFalse(t2 <= t1)

    # A helper for timestamp constructor tests.
    def verify_field_equality(self, expected, got):
        self.assertEqual(expected.tm_year, got.year)
        self.assertEqual(expected.tm_mon, got.month)
        self.assertEqual(expected.tm_mday, got.day)
        self.assertEqual(expected.tm_hour, got.hour)
        self.assertEqual(expected.tm_min, got.minute)
        self.assertEqual(expected.tm_sec, got.second)

    def test_fromtimestamp(self):
        import time

        ts = time.time()
        expected = time.localtime(ts)
        got = self.theclass.fromtimestamp(ts)
        self.verify_field_equality(expected, got)

    @unittest.skip("gmtime not implemented in CircuitPython")
    def test_utcfromtimestamp(self):
        import time

        ts = time.time()
        expected = time.gmtime(ts)
        got = self.theclass.utcfromtimestamp(ts)
        self.verify_field_equality(expected, got)

    # Run with US-style DST rules: DST begins 2 a.m. on second Sunday in
    # March (M3.2.0) and ends 2 a.m. on first Sunday in November (M11.1.0).
    @support.run_with_tz("EST+05EDT,M3.2.0,M11.1.0")
    def test_timestamp_naive(self):
        t = self.theclass(1970, 1, 1)
        self.assertEqual(t.timestamp(), 18000.0)
        t = self.theclass(1970, 1, 1, 1, 2, 3, 4)
        self.assertEqual(t.timestamp(), 18000.0 + 3600 + 2 * 60 + 3 + 4 * 1e-6)
        # Missing hour
        t0 = self.theclass(2012, 3, 11, 2, 30)
        t1 = t0.replace(fold=1)
        self.assertEqual(
            self.theclass.fromtimestamp(t1.timestamp()), t0 - timedelta(hours=1)
        )
        self.assertEqual(
            self.theclass.fromtimestamp(t0.timestamp()), t1 + timedelta(hours=1)
        )
        # Ambiguous hour defaults to DST
        t = self.theclass(2012, 11, 4, 1, 30)
        self.assertEqual(self.theclass.fromtimestamp(t.timestamp()), t)

        # Timestamp may raise an overflow error on some platforms
        # XXX: Do we care to support the first and last year?
        for t in [self.theclass(2, 1, 1), self.theclass(9998, 12, 12)]:
            try:
                s = t.timestamp()
            except OverflowError:
                pass
            else:
                self.assertEqual(self.theclass.fromtimestamp(s), t)

    def test_timestamp_aware(self):
        t = self.theclass(1970, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(t.timestamp(), 0.0)
        t = self.theclass(1970, 1, 1, 1, 2, 3, 4, tzinfo=timezone.utc)
        self.assertEqual(t.timestamp(), 3600 + 2 * 60 + 3 + 4 * 1e-6)
        t = self.theclass(
            1970, 1, 1, 1, 2, 3, 4, tzinfo=timezone(timedelta(hours=-5), "EST")
        )
        self.assertEqual(t.timestamp(), 18000 + 3600 + 2 * 60 + 3 + 4 * 1e-6)

    @unittest.skip("Not implemented - gmtime")
    @support.run_with_tz("MSK-03")  # Something east of Greenwich
    def test_microsecond_rounding(self):
        for fts in [self.theclass.fromtimestamp, self.theclass.utcfromtimestamp]:
            zero = fts(0)
            self.assertEqual(zero.second, 0)
            self.assertEqual(zero.microsecond, 0)
            one = fts(1e-6)
            try:
                minus_one = fts(-1e-6)
            except OSError:
                # localtime(-1) and gmtime(-1) is not supported on Windows
                pass
            else:
                self.assertEqual(minus_one.second, 59)
                self.assertEqual(minus_one.microsecond, 999999)

                t = fts(-1e-8)
                self.assertEqual(t, zero)
                t = fts(-9e-7)
                self.assertEqual(t, minus_one)
                t = fts(-1e-7)
                self.assertEqual(t, zero)
                t = fts(-1 / 2 ** 7)
                self.assertEqual(t.second, 59)
                self.assertEqual(t.microsecond, 992188)

            t = fts(1e-7)
            self.assertEqual(t, zero)
            t = fts(9e-7)
            self.assertEqual(t, one)
            t = fts(0.99999949)
            self.assertEqual(t.second, 0)
            self.assertEqual(t.microsecond, 999999)
            t = fts(0.9999999)
            self.assertEqual(t.second, 1)
            self.assertEqual(t.microsecond, 0)
            t = fts(1 / 2 ** 7)
            self.assertEqual(t.second, 0)
            self.assertEqual(t.microsecond, 7812)

    @unittest.skip("gmtime not implemented in CircuitPython")
    def test_timestamp_limits(self):
        # minimum timestamp
        min_dt = self.theclass.min.replace(tzinfo=timezone.utc)
        min_ts = min_dt.timestamp()
        try:
            # date 0001-01-01 00:00:00+00:00: timestamp=-62135596800
            self.assertEqual(
                self.theclass.fromtimestamp(min_ts, tz=timezone.utc), min_dt
            )
        except (OverflowError, OSError) as exc:
            # the date 0001-01-01 doesn't fit into 32-bit time_t,
            # or platform doesn't support such very old date
            self.skipTest(str(exc))

        # maximum timestamp: set seconds to zero to avoid rounding issues
        max_dt = self.theclass.max.replace(tzinfo=timezone.utc, second=0, microsecond=0)
        max_ts = max_dt.timestamp()
        # date 9999-12-31 23:59:00+00:00: timestamp 253402300740
        self.assertEqual(self.theclass.fromtimestamp(max_ts, tz=timezone.utc), max_dt)

        # number of seconds greater than 1 year: make sure that the new date
        # is not valid in datetime.datetime limits
        delta = 3600 * 24 * 400

        # too small
        ts = min_ts - delta
        # converting a Python int to C time_t can raise a OverflowError,
        # especially on 32-bit platforms.
        with self.assertRaises((ValueError, OverflowError)):
            self.theclass.fromtimestamp(ts)
        with self.assertRaises((ValueError, OverflowError)):
            self.theclass.utcfromtimestamp(ts)

        # too big
        ts = max_dt.timestamp() + delta
        with self.assertRaises((ValueError, OverflowError)):
            self.theclass.fromtimestamp(ts)
        with self.assertRaises((ValueError, OverflowError)):
            self.theclass.utcfromtimestamp(ts)

    def test_insane_fromtimestamp(self):
        # It's possible that some platform maps time_t to double,
        # and that this test will fail there.  This test should
        # exempt such platforms (provided they return reasonable
        # results!).
        for insane in -1e200, 1e200:
            self.assertRaises(OverflowError, self.theclass.fromtimestamp, insane)

    @unittest.skip("Not implemented - gmtime")
    def test_insane_utcfromtimestamp(self):
        # It's possible that some platform maps time_t to double,
        # and that this test will fail there.  This test should
        # exempt such platforms (provided they return reasonable
        # results!).
        for insane in -1e200, 1e200:
            self.assertRaises(OverflowError, self.theclass.utcfromtimestamp, insane)

    @unittest.skip("gmtime not implemented in CircuitPython")
    def test_utcnow(self):
        import time

        # Call it a success if utcnow() and utcfromtimestamp() are within
        # a second of each other.
        tolerance = timedelta(seconds=1)
        for dummy in range(3):
            from_now = self.theclass.utcnow()
            from_timestamp = self.theclass.utcfromtimestamp(time.time())
            if abs(from_timestamp - from_now) <= tolerance:
                break
            # Else try again a few times.
        self.assertLessEqual(abs(from_timestamp - from_now), tolerance)

    @unittest.skip("gmtime not implemented in CircuitPython")
    def test_strptime(self):
        string = "2004-12-01 13:02:47.197"
        format = "%Y-%m-%d %H:%M:%S.%f"
        expected = _strptime._strptime_datetime(self.theclass, string, format)
        got = self.theclass.strptime(string, format)
        self.assertEqual(expected, got)
        self.assertIs(type(expected), self.theclass)
        self.assertIs(type(got), self.theclass)

        # bpo-34482: Check that surrogates are handled properly.
        inputs = [
            ("2004-12-01\ud80013:02:47.197", "%Y-%m-%d\ud800%H:%M:%S.%f"),
            ("2004\ud80012-01 13:02:47.197", "%Y\ud800%m-%d %H:%M:%S.%f"),
            ("2004-12-01 13:02\ud80047.197", "%Y-%m-%d %H:%M\ud800%S.%f"),
        ]
        for string, format in inputs:
            with self.subTest(string=string, format=format):
                expected = _strptime._strptime_datetime(self.theclass, string, format)
                got = self.theclass.strptime(string, format)
                self.assertEqual(expected, got)

        strptime = self.theclass.strptime

        self.assertEqual(strptime("+0002", "%z").utcoffset(), 2 * MINUTE)
        self.assertEqual(strptime("-0002", "%z").utcoffset(), -2 * MINUTE)
        self.assertEqual(
            strptime("-00:02:01.000003", "%z").utcoffset(),
            -timedelta(minutes=2, seconds=1, microseconds=3),
        )
        # Only local timezone and UTC are supported
        for tzseconds, tzname in (
            (0, "UTC"),
            (0, "GMT"),
            (-_time.timezone, _time.tzname[0]),
        ):
            if tzseconds < 0:
                sign = "-"
                seconds = -tzseconds
            else:
                sign = "+"
                seconds = tzseconds
            hours, minutes = divmod(seconds // 60, 60)
            dtstr = "{}{:02d}{:02d} {}".format(sign, hours, minutes, tzname)
            dt = strptime(dtstr, "%z %Z")
            self.assertEqual(dt.utcoffset(), timedelta(seconds=tzseconds))
            self.assertEqual(dt.tzname(), tzname)
        # Can produce inconsistent datetime
        dtstr, fmt = "+1234 UTC", "%z %Z"
        dt = strptime(dtstr, fmt)
        self.assertEqual(dt.utcoffset(), 12 * HOUR + 34 * MINUTE)
        self.assertEqual(dt.tzname(), "UTC")
        # yet will roundtrip
        self.assertEqual(dt.strftime(fmt), dtstr)

        # Produce naive datetime if no %z is provided
        self.assertEqual(strptime("UTC", "%Z").tzinfo, None)

        with self.assertRaises(ValueError):
            strptime("-2400", "%z")
        with self.assertRaises(ValueError):
            strptime("-000", "%z")

    @unittest.skip("gmtime not implemented in CircuitPython")
    def test_strptime_single_digit(self):
        # bpo-34903: Check that single digit dates and times are allowed.

        strptime = self.theclass.strptime

        with self.assertRaises(ValueError):
            # %y does require two digits.
            newdate = strptime("01/02/3 04:05:06", "%d/%m/%y %H:%M:%S")
        dt1 = self.theclass(2003, 2, 1, 4, 5, 6)
        dt2 = self.theclass(2003, 1, 2, 4, 5, 6)
        dt3 = self.theclass(2003, 2, 1, 0, 0, 0)
        dt4 = self.theclass(2003, 1, 25, 0, 0, 0)
        inputs = [
            ("%d", "1/02/03 4:5:6", "%d/%m/%y %H:%M:%S", dt1),
            ("%m", "01/2/03 4:5:6", "%d/%m/%y %H:%M:%S", dt1),
            ("%H", "01/02/03 4:05:06", "%d/%m/%y %H:%M:%S", dt1),
            ("%M", "01/02/03 04:5:06", "%d/%m/%y %H:%M:%S", dt1),
            ("%S", "01/02/03 04:05:6", "%d/%m/%y %H:%M:%S", dt1),
            ("%j", "2/03 04am:05:06", "%j/%y %I%p:%M:%S", dt2),
            ("%I", "02/03 4am:05:06", "%j/%y %I%p:%M:%S", dt2),
            ("%w", "6/04/03", "%w/%U/%y", dt3),
            # %u requires a single digit.
            ("%W", "6/4/2003", "%u/%W/%Y", dt3),
            ("%V", "6/4/2003", "%u/%V/%G", dt4),
        ]
        for reason, string, format, target in inputs:
            reason = "test single digit " + reason
            with self.subTest(
                reason=reason, string=string, format=format, target=target
            ):
                newdate = strptime(string, format)
                self.assertEqual(newdate, target, msg=reason)

    def test_more_timetuple(self):
        # This tests fields beyond those tested by the TestDate.test_timetuple.
        t = self.theclass(2004, 12, 31, 6, 22, 33)
        self.assertEqual(t.timetuple(), (2004, 12, 31, 6, 22, 33, 4, 366, -1))
        self.assertEqual(
            t.timetuple(),
            (
                t.year,
                t.month,
                t.day,
                t.hour,
                t.minute,
                t.second,
                t.weekday(),
                t.toordinal() - date(t.year, 1, 1).toordinal() + 1,
                -1,
            ),
        )
        tt = t.timetuple()
        self.assertEqual(tt.tm_year, t.year)
        self.assertEqual(tt.tm_mon, t.month)
        self.assertEqual(tt.tm_mday, t.day)
        self.assertEqual(tt.tm_hour, t.hour)
        self.assertEqual(tt.tm_min, t.minute)
        self.assertEqual(tt.tm_sec, t.second)
        self.assertEqual(tt.tm_wday, t.weekday())
        self.assertEqual(tt.tm_yday, t.toordinal() - date(t.year, 1, 1).toordinal() + 1)
        self.assertEqual(tt.tm_isdst, -1)

    @unittest.skip("gmtime not implemented in CircuitPython")
    def test_more_strftime(self):
        # This tests fields beyond those tested by the TestDate.test_strftime.
        t = self.theclass(2004, 12, 31, 6, 22, 33, 47)
        self.assertEqual(
            t.strftime("%m %d %y %f %S %M %H %j"), "12 31 04 000047 33 22 06 366"
        )
        for (s, us), z in [
            ((33, 123), "33.000123"),
            ((33, 0), "33"),
        ]:
            tz = timezone(-timedelta(hours=2, seconds=s, microseconds=us))
            t = t.replace(tzinfo=tz)
            self.assertEqual(t.strftime("%z"), "-0200" + z)

        # bpo-34482: Check that surrogates don't cause a crash.
        try:
            t.strftime("%y\ud800%m %H\ud800%M")
        except UnicodeEncodeError:
            pass

    def test_extract(self):
        dt = self.theclass(2002, 3, 4, 18, 45, 3, 1234)
        self.assertEqual(dt.date(), date(2002, 3, 4))
        self.assertEqual(dt.time(), time(18, 45, 3, 1234))

    # TODO
    @unittest.skip("not implemented - timezone")
    def test_combine(self):
        d = date(2002, 3, 4)
        t = time(18, 45, 3, 1234)
        expected = self.theclass(2002, 3, 4, 18, 45, 3, 1234)
        combine = self.theclass.combine
        dt = combine(d, t)
        self.assertEqual(dt, expected)

        dt = combine(time=t, date=d)
        self.assertEqual(dt, expected)

        self.assertEqual(d, dt.date())
        self.assertEqual(t, dt.time())
        self.assertEqual(dt, combine(dt.date(), dt.time()))

        self.assertRaises(TypeError, combine)  # need an arg
        self.assertRaises(TypeError, combine, d)  # need two args
        self.assertRaises(TypeError, combine, t, d)  # args reversed
        self.assertRaises(TypeError, combine, d, t, 1)  # wrong tzinfo type
        self.assertRaises(TypeError, combine, d, t, 1, 2)  # too many args
        self.assertRaises(TypeError, combine, "date", "time")  # wrong types
        self.assertRaises(TypeError, combine, d, "time")  # wrong type
        self.assertRaises(TypeError, combine, "date", t)  # wrong type

        # tzinfo= argument
        dt = combine(d, t, timezone.utc)
        self.assertIs(dt.tzinfo, timezone.utc)
        dt = combine(d, t, tzinfo=timezone.utc)
        self.assertIs(dt.tzinfo, timezone.utc)
        t = time()
        dt = combine(dt, t)
        self.assertEqual(dt.date(), d)
        self.assertEqual(dt.time(), t)

    def test_replace(self):
        cls = self.theclass
        args = [1, 2, 3, 4, 5, 6, 7]
        base = cls(*args)
        self.assertEqual(base, base.replace())

        i = 0
        for name, newval in (
            ("year", 2),
            ("month", 3),
            ("day", 4),
            ("hour", 5),
            ("minute", 6),
            ("second", 7),
            ("microsecond", 8),
        ):
            newargs = args[:]
            newargs[i] = newval
            expected = cls(*newargs)
            got = base.replace(**{name: newval})
            self.assertEqual(expected, got)
            i += 1

        # Out of bounds.
        base = cls(2000, 2, 29)
        self.assertRaises(ValueError, base.replace, year=2001)

    @unittest.skip("astimezone not impld")
    @support.run_with_tz("EDT4")
    def test_astimezone(self):
        dt = self.theclass.now()
        f = FixedOffset(44, "0044")
        dt_utc = dt.replace(tzinfo=timezone(timedelta(hours=-4), "EDT"))
        self.assertEqual(dt.astimezone(), dt_utc)  # naive
        self.assertRaises(TypeError, dt.astimezone, f, f)  # too many args
        self.assertRaises(TypeError, dt.astimezone, dt)  # arg wrong type
        dt_f = dt.replace(tzinfo=f) + timedelta(hours=4, minutes=44)
        self.assertEqual(dt.astimezone(f), dt_f)  # naive
        self.assertEqual(dt.astimezone(tz=f), dt_f)  # naive

        class Bogus(tzinfo):
            def utcoffset(self, dt):
                return None

            def dst(self, dt):
                return timedelta(0)

        bog = Bogus()
        self.assertRaises(ValueError, dt.astimezone, bog)  # naive
        self.assertEqual(dt.replace(tzinfo=bog).astimezone(f), dt_f)

        class AlsoBogus(tzinfo):
            def utcoffset(self, dt):
                return timedelta(0)

            def dst(self, dt):
                return None

        alsobog = AlsoBogus()
        self.assertRaises(ValueError, dt.astimezone, alsobog)  # also naive

        class Broken(tzinfo):
            def utcoffset(self, dt):
                return 1

            def dst(self, dt):
                return 1

        broken = Broken()
        dt_broken = dt.replace(tzinfo=broken)
        with self.assertRaises(TypeError):
            dt_broken.astimezone()

    def test_subclass_datetime(self):
        class C(self.theclass):
            theAnswer = 42

            def __new__(cls, *args, **kws):
                temp = kws.copy()
                extra = temp.pop("extra")
                result = self.theclass.__new__(cls, *args, **temp)
                result.extra = extra
                return result

            def newmeth(self, start):
                return start + self.year + self.month + self.second

        args = 2003, 4, 14, 12, 13, 41

        dt1 = self.theclass(*args)
        dt2 = C(*args, **{"extra": 7})

        self.assertEqual(dt2.__class__, C)
        self.assertEqual(dt2.theAnswer, 42)
        self.assertEqual(dt2.extra, 7)
        self.assertEqual(dt1.toordinal(), dt2.toordinal())
        self.assertEqual(dt2.newmeth(-7), dt1.year + dt1.month + dt1.second - 7)

    # TODO
    @unittest.skip("timezone not implemented")
    def test_subclass_alternate_constructors_datetime(self):
        # Test that alternate constructors call the constructor
        class DateTimeSubclass(self.theclass):
            def __new__(cls, *args, **kwargs):
                result = self.theclass.__new__(cls, *args, **kwargs)
                result.extra = 7

                return result

        args = (2003, 4, 14, 12, 30, 15, 123456)
        d_isoformat = "2003-04-14T12:30:15.123456"  # Equivalent isoformat()
        utc_ts = 1050323415.123456  # UTC timestamp

        base_d = DateTimeSubclass(*args)
        self.assertIsInstance(base_d, DateTimeSubclass)
        self.assertEqual(base_d.extra, 7)

        # Timestamp depends on time zone, so we'll calculate the equivalent here
        ts = base_d.timestamp()

        test_cases = [
            ("fromtimestamp", (ts,), base_d),
            # See https://bugs.python.org/issue32417
            ("fromtimestamp", (ts, timezone.utc), base_d.astimezone(timezone.utc)),
            ("utcfromtimestamp", (utc_ts,), base_d),
            ("fromisoformat", (d_isoformat,), base_d),
            ("strptime", (d_isoformat, "%Y-%m-%dT%H:%M:%S.%f"), base_d),
            ("combine", (date(*args[0:3]), time(*args[3:])), base_d),
        ]

        for constr_name, constr_args, expected in test_cases:
            for base_obj in (DateTimeSubclass, base_d):
                # Test both the classmethod and method
                with self.subTest(
                    base_obj_type=type(base_obj), constr_name=constr_name
                ):
                    constructor = getattr(base_obj, constr_name)

                    dt = constructor(*constr_args)

                    # Test that it creates the right subclass
                    self.assertIsInstance(dt, DateTimeSubclass)

                    # Test that it's equal to the base object
                    self.assertEqual(dt, expected)

                    # Test that it called the constructor
                    self.assertEqual(dt.extra, 7)

    # TODO
    @unittest.skip("timezone not implemented")
    def test_subclass_now(self):
        # Test that alternate constructors call the constructor
        class DateTimeSubclass(self.theclass):
            def __new__(cls, *args, **kwargs):
                result = self.theclass.__new__(cls, *args, **kwargs)
                result.extra = 7

                return result

        test_cases = [
            ("now", "now", {}),
            ("utcnow", "utcnow", {}),
            ("now_utc", "now", {"tz": timezone.utc}),
            ("now_fixed", "now", {"tz": timezone(timedelta(hours=-5), "EST")}),
        ]

        for name, meth_name, kwargs in test_cases:
            with self.subTest(name):
                constr = getattr(DateTimeSubclass, meth_name)
                dt = constr(**kwargs)

                self.assertIsInstance(dt, DateTimeSubclass)
                self.assertEqual(dt.extra, 7)

    def test_fromisoformat_datetime(self):
        # Test that isoformat() is reversible
        base_dates = [(1, 1, 1), (1900, 1, 1), (2004, 11, 12), (2017, 5, 30)]

        base_times = [
            (0, 0, 0, 0),
            (0, 0, 0, 241000),
            (0, 0, 0, 234567),
            (12, 30, 45, 234567),
        ]

        separators = [" ", "T"]

        tzinfos = [
            None,
            timezone.utc,
            timezone(timedelta(hours=-5)),
            timezone(timedelta(hours=2)),
        ]

        dts = [
            self.theclass(*date_tuple, *time_tuple, tzinfo=tzi)
            for date_tuple in base_dates
            for time_tuple in base_times
            for tzi in tzinfos
        ]

        for dt in dts:
            for sep in separators:
                dtstr = dt.isoformat(sep=sep)

                with self.subTest(dtstr=dtstr):
                    dt_rt = self.theclass.fromisoformat(dtstr)
                    self.assertEqual(dt, dt_rt)

    # TODO
    @unittest.skip("not implemented timezone")
    def test_fromisoformat_timezone(self):
        base_dt = self.theclass(2014, 12, 30, 12, 30, 45, 217456)

        tzoffsets = [
            timedelta(hours=5),
            timedelta(hours=2),
            timedelta(hours=6, minutes=27),
            timedelta(hours=12, minutes=32, seconds=30),
            timedelta(hours=2, minutes=4, seconds=9, microseconds=123456),
        ]

        tzoffsets += [-1 * td for td in tzoffsets]

        tzinfos = [None, timezone.utc, timezone(timedelta(hours=0))]

        tzinfos += [timezone(td) for td in tzoffsets]

        for tzi in tzinfos:
            dt = base_dt.replace(tzinfo=tzi)
            dtstr = dt.isoformat()

            with self.subTest(tstr=dtstr):
                dt_rt = self.theclass.fromisoformat(dtstr)
                assert dt == dt_rt, dt_rt

    def test_fromisoformat_separators(self):
        separators = [
            " ",
            "T",
            "\u007f",  # 1-bit widths
            "\u0080",
            "ʁ",  # 2-bit widths
            "ᛇ",
            "時",  # 3-bit widths
            "🐍",  # 4-bit widths
            "\ud800",  # bpo-34454: Surrogate code point
        ]

        for sep in separators:
            dt = self.theclass(2018, 1, 31, 23, 59, 47, 124789)
            dtstr = dt.isoformat(sep=sep)

            with self.subTest(dtstr=dtstr):
                dt_rt = self.theclass.fromisoformat(dtstr)
                self.assertEqual(dt, dt_rt)

    def test_fromisoformat_ambiguous(self):
        # Test strings like 2018-01-31+12:15 (where +12:15 is not a time zone)
        separators = ["+", "-"]
        for sep in separators:
            dt = self.theclass(2018, 1, 31, 12, 15)
            dtstr = dt.isoformat(sep=sep)

            with self.subTest(dtstr=dtstr):
                dt_rt = self.theclass.fromisoformat(dtstr)
                self.assertEqual(dt, dt_rt)

    # TODO
    @unittest.skip("_format_time not fully implemented")
    def test_fromisoformat_timespecs(self):
        datetime_bases = [(2009, 12, 4, 8, 17, 45, 123456), (2009, 12, 4, 8, 17, 45, 0)]

        tzinfos = [
            None,
            timezone.utc,
            timezone(timedelta(hours=-5)),
            timezone(timedelta(hours=2)),
            timezone(timedelta(hours=6, minutes=27)),
        ]

        timespecs = ["hours", "minutes", "seconds", "milliseconds", "microseconds"]

        for ip, ts in enumerate(timespecs):
            for tzi in tzinfos:
                for dt_tuple in datetime_bases:
                    if ts == "milliseconds":
                        new_microseconds = 1000 * (dt_tuple[6] // 1000)
                        dt_tuple = dt_tuple[0:6] + (new_microseconds,)

                    dt = self.theclass(*(dt_tuple[0 : (4 + ip)]), tzinfo=tzi)
                    dtstr = dt.isoformat(timespec=ts)
                    with self.subTest(dtstr=dtstr):
                        dt_rt = self.theclass.fromisoformat(dtstr)
                        self.assertEqual(dt, dt_rt)

    def test_fromisoformat_fails_datetime(self):
        # Test that fromisoformat() fails on invalid values
        bad_strs = [
            "",  # Empty string
            "\ud800",  # bpo-34454: Surrogate code point
            "2009.04-19T03",  # Wrong first separator
            "2009-04.19T03",  # Wrong second separator
            "2009-04-19T0a",  # Invalid hours
            "2009-04-19T03:1a:45",  # Invalid minutes
            "2009-04-19T03:15:4a",  # Invalid seconds
            "2009-04-19T03;15:45",  # Bad first time separator
            "2009-04-19T03:15;45",  # Bad second time separator
            "2009-04-19T03:15:4500:00",  # Bad time zone separator
            "2009-04-19T03:15:45.2345",  # Too many digits for milliseconds
            "2009-04-19T03:15:45.1234567",  # Too many digits for microseconds
            "2009-04-19T03:15:45.123456+24:30",  # Invalid time zone offset
            "2009-04-19T03:15:45.123456-24:30",  # Invalid negative offset
            "2009-04-10ᛇᛇᛇᛇᛇ12:15",  # Too many unicode separators
            "2009-04\ud80010T12:15",  # Surrogate char in date
            "2009-04-10T12\ud80015",  # Surrogate char in time
            "2009-04-19T1",  # Incomplete hours
            "2009-04-19T12:3",  # Incomplete minutes
            "2009-04-19T12:30:4",  # Incomplete seconds
            "2009-04-19T12:",  # Ends with time separator
            "2009-04-19T12:30:",  # Ends with time separator
            "2009-04-19T12:30:45.",  # Ends with time separator
            "2009-04-19T12:30:45.123456+",  # Ends with timzone separator
            "2009-04-19T12:30:45.123456-",  # Ends with timzone separator
            "2009-04-19T12:30:45.123456-05:00a",  # Extra text
            "2009-04-19T12:30:45.123-05:00a",  # Extra text
            "2009-04-19T12:30:45-05:00a",  # Extra text
        ]

        for bad_str in bad_strs:
            with self.subTest(bad_str=bad_str):
                with self.assertRaises(ValueError):
                    self.theclass.fromisoformat(bad_str)

    def test_fromisoformat_fails_surrogate(self):
        # Test that when fromisoformat() fails with a surrogate character as
        # the separator, the error message contains the original string
        dtstr = "2018-01-03\ud80001:0113"

        with self.assertRaisesRegex(ValueError, repr(dtstr)):
            self.theclass.fromisoformat(dtstr)

    # TODO
    @unittest.skip("fromisoformat not implemented")
    def test_fromisoformat_utc(self):
        dt_str = "2014-04-19T13:21:13+00:00"
        dt = self.theclass.fromisoformat(dt_str)

        self.assertIs(dt.tzinfo, timezone.utc)

    def test_fromisoformat_subclass(self):
        class DateTimeSubclass(self.theclass):
            pass

        dt = DateTimeSubclass(
            2014,
            12,
            14,
            9,
            30,
            45,
            457390,
            tzinfo=timezone(timedelta(hours=10, minutes=45)),
        )

        dt_rt = DateTimeSubclass.fromisoformat(dt.isoformat())

        self.assertEqual(dt, dt_rt)
        self.assertIsInstance(dt_rt, DateTimeSubclass)

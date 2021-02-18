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

# CPython standard implementation
from datetime import date as cpython_date
from datetime import MINYEAR, MAXYEAR

# CircuitPython subset implementation
sys.path.append("..")
from adafruit_datetime import date as cpy_date

# An arbitrary collection of objects of non-datetime types, for testing
# mixed-type comparisons.
OTHERSTUFF = (10, 34.5, "abc", {}, [], ())


class TestDate(unittest.TestCase):
    def test_basic_attributes(self):
        dt = cpy_date(2002, 3, 1)
        dt_2 = cpython_date(2002, 3, 1)
        self.assertEqual(dt.year, dt_2.year)
        self.assertEqual(dt.month, dt_2.month)
        self.assertEqual(dt.day, dt_2.day)

    def test_bad_constructor_arguments(self):
        # bad years
        cpy_date(MINYEAR, 1, 1)  # no exception
        cpy_date(MAXYEAR, 1, 1)  # no exception
        self.assertRaises(ValueError, cpy_date, MINYEAR - 1, 1, 1)
        self.assertRaises(ValueError, cpy_date, MAXYEAR + 1, 1, 1)
        # bad months
        cpy_date(2000, 1, 1)  # no exception
        cpy_date(2000, 12, 1)  # no exception
        self.assertRaises(ValueError, cpy_date, 2000, 0, 1)
        self.assertRaises(ValueError, cpy_date, 2000, 13, 1)
        # bad days
        cpy_date(2000, 2, 29)  # no exception
        cpy_date(2004, 2, 29)  # no exception
        cpy_date(2400, 2, 29)  # no exception
        self.assertRaises(ValueError, cpy_date, 2000, 2, 30)
        self.assertRaises(ValueError, cpy_date, 2001, 2, 29)
        self.assertRaises(ValueError, cpy_date, 2100, 2, 29)
        self.assertRaises(ValueError, cpy_date, 1900, 2, 29)
        self.assertRaises(ValueError, cpy_date, 2000, 1, 0)
        self.assertRaises(ValueError, cpy_date, 2000, 1, 32)

    def test_hash_equality(self):
        d = cpy_date(2000, 12, 31)
        e = cpy_date(2000, 12, 31)
        self.assertEqual(d, e)
        self.assertEqual(hash(d), hash(e))

        dic = {d: 1}
        dic[e] = 2
        self.assertEqual(len(dic), 1)
        self.assertEqual(dic[d], 2)
        self.assertEqual(dic[e], 2)

        d = cpy_date(2001, 1, 1)
        e = cpy_date(2001, 1, 1)
        self.assertEqual(d, e)
        self.assertEqual(hash(d), hash(e))

        dic = {d: 1}
        dic[e] = 2
        self.assertEqual(len(dic), 1)
        self.assertEqual(dic[d], 2)
        self.assertEqual(dic[e], 2)

    def test_fromtimestamp(self):
        import time

        # Try an arbitrary fixed value.
        year, month, day = 1999, 9, 19
        ts = time.mktime((year, month, day, 0, 0, 0, 0, 0, -1))
        d = cpy_date.fromtimestamp(ts)
        self.assertEqual(d.year, year)
        self.assertEqual(d.month, month)
        self.assertEqual(d.day, day)

    def test_fromisoformat(self):
        # Try an arbitrary fixed value.
        iso_date_string = "1999-09-19"
        d = cpy_date.fromisoformat(iso_date_string)
        self.assertEqual(d.year, 1999)
        self.assertEqual(d.month, 9)
        self.assertEqual(d.day, 19)

    def test_fromisoformat_bad_formats(self):
        # Try an arbitrary fixed value.
        self.assertRaises(ValueError, cpy_date.fromisoformat, "99-09-19")
        self.assertRaises(ValueError, cpy_date.fromisoformat, "1999-13-19")

    # TODO: Test this when timedelta is added in
    @unittest.skip("Skip for CircuitPython - timedelta() not yet implemented.")
    def test_today(self):
        import time

        # We claim that today() is like fromtimestamp(time.time()), so
        # prove it.
        for dummy in range(3):
            today = cpy_date.today()
            ts = time.time()
            todayagain = cpy_date.fromtimestamp(ts)
            if today == todayagain:
                break
            # There are several legit reasons that could fail:
            # 1. It recently became midnight, between the today() and the
            #    time() calls.
            # 2. The platform time() has such fine resolution that we'll
            #    never get the same value twice.
            # 3. The platform time() has poor resolution, and we just
            #    happened to call today() right before a resolution quantum
            #    boundary.
            # 4. The system clock got fiddled between calls.
            # In any case, wait a little while and try again.
            time.sleep(0.1)

        # It worked or it didn't.  If it didn't, assume it's reason #2, and
        # let the test pass if they're within half a second of each other.
        self.assertTrue(
            today == todayagain or abs(todayagain - today) < timedelta(seconds=0.5)
        )

    def test_weekday(self):
        for i in range(7):
            # March 4, 2002 is a Monday
            self.assertEqual(
                cpy_date(2002, 3, 4 + i).weekday(),
                cpython_date(2002, 3, 4 + i).weekday(),
            )
            self.assertEqual(
                cpy_date(2002, 3, 4 + i).isoweekday(),
                cpython_date(2002, 3, 4 + i).isoweekday(),
            )
            # January 2, 1956 is a Monday
            self.assertEqual(
                cpy_date(1956, 1, 2 + i).weekday(),
                cpython_date(1956, 1, 2 + i).weekday(),
            )
            self.assertEqual(
                cpy_date(1956, 1, 2 + i).isoweekday(),
                cpython_date(1956, 1, 2 + i).isoweekday(),
            )

    @unittest.skip(
        "Skip for CircuitPython - isocalendar() not implemented for date objects."
    )
    def test_isocalendar(self):
        # Check examples from
        # http://www.phys.uu.nl/~vgent/calendar/isocalendar.htm
        for i in range(7):
            d = cpy_date(2003, 12, 22 + i)
            self.assertEqual(d.isocalendar(), (2003, 52, i + 1))
            d = cpy_date(2003, 12, 29) + timedelta(i)
            self.assertEqual(d.isocalendar(), (2004, 1, i + 1))
            d = cpy_date(2004, 1, 5 + i)
            self.assertEqual(d.isocalendar(), (2004, 2, i + 1))
            d = cpy_date(2009, 12, 21 + i)
            self.assertEqual(d.isocalendar(), (2009, 52, i + 1))
            d = cpy_date(2009, 12, 28) + timedelta(i)
            self.assertEqual(d.isocalendar(), (2009, 53, i + 1))
            d = cpy_date(2010, 1, 4 + i)
            self.assertEqual(d.isocalendar(), (2010, 1, i + 1))

    def test_isoformat(self):
        # test isoformat against expected and cpython equiv.
        t = cpy_date(2, 3, 2)
        t2 = cpython_date(2, 3, 2)
        self.assertEqual(t.isoformat(), "0002-03-02")
        self.assertEqual(t.isoformat(), t2.isoformat())

    @unittest.skip("Skip for CircuitPython - ctime() not implemented for date objects.")
    def test_ctime(self):
        t = cpy_date(2002, 3, 2)
        self.assertEqual(t.ctime(), "Sat Mar  2 00:00:00 2002")

    @unittest.skip(
        "Skip for CircuitPython - strftime() not implemented for date objects."
    )
    def test_strftime(self):
        t = cpy_date(2005, 3, 2)
        self.assertEqual(t.strftime("m:%m d:%d y:%y"), "m:03 d:02 y:05")
        self.assertEqual(t.strftime(""), "")  # SF bug #761337
        #        self.assertEqual(t.strftime('x'*1000), 'x'*1000) # SF bug #1556784

        self.assertRaises(TypeError, t.strftime)  # needs an arg
        self.assertRaises(TypeError, t.strftime, "one", "two")  # too many args
        self.assertRaises(TypeError, t.strftime, 42)  # arg wrong type

        # test that unicode input is allowed (issue 2782)
        self.assertEqual(t.strftime("%m"), "03")

        # A naive object replaces %z and %Z w/ empty strings.
        self.assertEqual(t.strftime("'%z' '%Z'"), "'' ''")

        # make sure that invalid format specifiers are handled correctly
        # self.assertRaises(ValueError, t.strftime, "%e")
        # self.assertRaises(ValueError, t.strftime, "%")
        # self.assertRaises(ValueError, t.strftime, "%#")

        # oh well, some systems just ignore those invalid ones.
        # at least, excercise them to make sure that no crashes
        # are generated
        for f in ["%e", "%", "%#"]:
            try:
                t.strftime(f)
            except ValueError:
                pass

        # check that this standard extension works
        t.strftime("%f")

    def test_format(self):
        dt = cpy_date(2007, 9, 10)
        self.assertEqual(dt.__format__(""), str(dt))

        # check that a derived class's __str__() gets called
        class A(cpy_date):
            def __str__(self):
                return "A"

        a = A(2007, 9, 10)
        self.assertEqual(a.__format__(""), "A")

        # check that a derived class's strftime gets called
        class B(cpy_date):
            def strftime(self, format_spec):
                return "B"

        b = B(2007, 9, 10)
        self.assertEqual(b.__format__(""), str(dt))

        # date strftime not implemented in CircuitPython, skip
        """for fmt in ["m:%m d:%d y:%y",
                    "m:%m d:%d y:%y H:%H M:%M S:%S",
                    "%z %Z",
                    ]:
            self.assertEqual(dt.__format__(fmt), dt.strftime(fmt))
            self.assertEqual(a.__format__(fmt), dt.strftime(fmt))
            self.assertEqual(b.__format__(fmt), 'B')"""

    @unittest.skip(
        "Skip for CircuitPython - min/max/resolution not implemented for date objects."
    )
    def test_resolution_info(self):
        # XXX: Should min and max respect subclassing?
        if issubclass(cpy_date, datetime):
            expected_class = datetime
        else:
            expected_class = date
        self.assertIsInstance(cpy_date.min, expected_class)
        self.assertIsInstance(cpy_date.max, expected_class)
        self.assertIsInstance(cpy_date.resolution, timedelta)
        self.assertTrue(cpy_date.max > cpy_date.min)

    # TODO: Needs timedelta
    @unittest.skip("Skip for CircuitPython - timedelta not implemented.")
    def test_extreme_timedelta(self):
        big = cpy_date.max - cpy_date.min
        # 3652058 days, 23 hours, 59 minutes, 59 seconds, 999999 microseconds
        n = (big.days * 24 * 3600 + big.seconds) * 1000000 + big.microseconds
        # n == 315537897599999999 ~= 2**58.13
        justasbig = timedelta(0, 0, n)
        self.assertEqual(big, justasbig)
        self.assertEqual(cpy_date.min + big, cpy_date.max)
        self.assertEqual(cpy_date.max - big, cpy_date.min)

    def test_timetuple(self):
        for i in range(7):
            # January 2, 1956 is a Monday (0)
            d = cpy_date(1956, 1, 2 + i)
            t = d.timetuple()
            d2 = cpython_date(1956, 1, 2 + i)
            t2 = d2.timetuple()
            self.assertEqual(t, t2)
            # February 1, 1956 is a Wednesday (2)
            d = cpy_date(1956, 2, 1 + i)
            t = d.timetuple()
            d2 = cpython_date(1956, 2, 1 + i)
            t2 = d2.timetuple()
            self.assertEqual(t, t2)
            # March 1, 1956 is a Thursday (3), and is the 31+29+1 = 61st day
            # of the year.
            d = cpy_date(1956, 3, 1 + i)
            t = d.timetuple()
            d2 = cpython_date(1956, 3, 1 + i)
            t2 = d2.timetuple()
            self.assertEqual(t, t2)
            self.assertEqual(t.tm_year, t2.tm_year)
            self.assertEqual(t.tm_mon, t2.tm_mon)
            self.assertEqual(t.tm_mday, t2.tm_mday)
            self.assertEqual(t.tm_hour, t2.tm_hour)
            self.assertEqual(t.tm_min, t2.tm_min)
            self.assertEqual(t.tm_sec, t2.tm_sec)
            self.assertEqual(t.tm_wday, t2.tm_wday)
            self.assertEqual(t.tm_yday, t2.tm_yday)
            self.assertEqual(t.tm_isdst, t2.tm_isdst)

    def test_compare(self):
        t1 = cpy_date(2, 3, 4)
        t2 = cpy_date(2, 3, 4)
        self.assertEqual(t1, t2)
        self.assertTrue(t1 <= t2)
        self.assertTrue(t1 >= t2)
        self.assertTrue(not t1 != t2)
        self.assertTrue(not t1 < t2)
        self.assertTrue(not t1 > t2)

        for args in (3, 3, 3), (2, 4, 4), (2, 3, 5):
            t2 = cpy_date(*args)  # this is larger than t1
            self.assertTrue(t1 < t2)
            self.assertTrue(t2 > t1)
            self.assertTrue(t1 <= t2)
            self.assertTrue(t2 >= t1)
            self.assertTrue(t1 != t2)
            self.assertTrue(t2 != t1)
            self.assertTrue(not t1 == t2)
            self.assertTrue(not t2 == t1)
            self.assertTrue(not t1 > t2)
            self.assertTrue(not t2 < t1)
            self.assertTrue(not t1 >= t2)
            self.assertTrue(not t2 <= t1)

        for badarg in OTHERSTUFF:
            self.assertEqual(t1 == badarg, False)
            self.assertEqual(t1 != badarg, True)
            self.assertEqual(badarg == t1, False)
            self.assertEqual(badarg != t1, True)

            self.assertRaises(TypeError, lambda: t1 < badarg)
            self.assertRaises(TypeError, lambda: t1 > badarg)
            self.assertRaises(TypeError, lambda: t1 >= badarg)
            self.assertRaises(TypeError, lambda: badarg <= t1)
            self.assertRaises(TypeError, lambda: badarg < t1)
            self.assertRaises(TypeError, lambda: badarg > t1)
            self.assertRaises(TypeError, lambda: badarg >= t1)

    def test_mixed_compare(self):
        our = cpy_date(2000, 4, 5)
        our2 = cpython_date(2000, 4, 5)

        # Our class can be compared for equality to other classes
        self.assertEqual(our == 1, our2 == 1)
        self.assertEqual(1 == our, 1 == our2)
        self.assertEqual(our != 1, our2 != 1)
        self.assertEqual(1 != our, 1 != our2)

        # But the ordering is undefined
        self.assertRaises(TypeError, lambda: our < 1)
        self.assertRaises(TypeError, lambda: 1 < our)

        # Repeat those tests with a different class

        class SomeClass:
            pass

        their = SomeClass()
        self.assertEqual(our == their, False)
        self.assertEqual(their == our, False)
        self.assertEqual(our != their, True)
        self.assertEqual(their != our, True)
        self.assertRaises(TypeError, lambda: our < their)
        self.assertRaises(TypeError, lambda: their < our)

        # However, if the other class explicitly defines ordering
        # relative to our class, it is allowed to do so

        class LargerThanAnything:
            def __lt__(self, other):
                return False

            def __le__(self, other):
                return isinstance(other, LargerThanAnything)

            def __eq__(self, other):
                return isinstance(other, LargerThanAnything)

            def __ne__(self, other):
                return not isinstance(other, LargerThanAnything)

            def __gt__(self, other):
                return not isinstance(other, LargerThanAnything)

            def __ge__(self, other):
                return True

        their = LargerThanAnything()
        self.assertEqual(our == their, False)
        self.assertEqual(their == our, False)
        self.assertEqual(our != their, True)
        self.assertEqual(their != our, True)
        self.assertEqual(our < their, True)
        self.assertEqual(their < our, False)

    @unittest.skip(
        "Skip for CircuitPython - min/max date attributes not implemented yet."
    )
    def test_bool(self):
        # All dates are considered true.
        self.assertTrue(cpy_date.min)
        self.assertTrue(cpy_date.max)

    @unittest.skip("Skip for CircuitPython - date strftime not implemented yet.")
    def test_strftime_y2k(self):
        for y in (1, 49, 70, 99, 100, 999, 1000, 1970):
            d = cpy_date(y, 1, 1)
            # Issue 13305:  For years < 1000, the value is not always
            # padded to 4 digits across platforms.  The C standard
            # assumes year >= 1900, so it does not specify the number
            # of digits.
            if d.strftime("%Y") != "%04d" % y:
                # Year 42 returns '42', not padded
                self.assertEqual(d.strftime("%Y"), "%d" % y)
                # '0042' is obtained anyway
                self.assertEqual(d.strftime("%4Y"), "%04d" % y)

    @unittest.skip("Skip for CircuitPython - date replace not implemented.")
    def test_replace(self):
        cls = cpy_date
        args = [1, 2, 3]
        base = cls(*args)
        self.assertEqual(base, base.replace())

        i = 0
        for name, newval in (("year", 2), ("month", 3), ("day", 4)):
            newargs = args[:]
            newargs[i] = newval
            expected = cls(*newargs)
            got = base.replace(**{name: newval})
            self.assertEqual(expected, got)
            i += 1

        # Out of bounds.
        base = cls(2000, 2, 29)
        self.assertRaises(ValueError, base.replace, year=2001)

    def test_subclass_date(self):
        class C(cpy_date):
            theAnswer = 42

            def __new__(cls, *args, **kws):
                temp = kws.copy()
                extra = temp.pop("extra")
                result = cpy_date.__new__(cls, *args, **temp)
                result.extra = extra
                return result

            def newmeth(self, start):
                return start + self.year + self.month

        args = 2003, 4, 14

        dt1 = cpy_date(*args)
        dt2 = C(*args, **{"extra": 7})

        self.assertEqual(dt2.__class__, C)
        self.assertEqual(dt2.theAnswer, 42)
        self.assertEqual(dt2.extra, 7)
        self.assertEqual(dt1.toordinal(), dt2.toordinal())
        self.assertEqual(dt2.newmeth(-7), dt1.year + dt1.month - 7)

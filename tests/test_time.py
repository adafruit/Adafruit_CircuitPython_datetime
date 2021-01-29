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
import unittest

# CPython standard implementation
from datetime import time as cpython_time

# CircuitPython subset implementation
import sys

sys.path.append("..")
from adafruit_datetime import time as cpy_time

# An arbitrary collection of objects of non-datetime types, for testing
# mixed-type comparisons.
OTHERSTUFF = (10, 34.5, "abc", {}, [], ())

#############################################################################
# Base class for testing a particular aspect of timedelta, time, date and
# datetime comparisons.


class HarmlessMixedComparison:
    # Test that __eq__ and __ne__ don't complain for mixed-type comparisons.

    # Subclasses must define 'theclass', and theclass(1, 1, 1) must be a
    # legit constructor.

    def test_harmless_mixed_comparison(self):
        me = self.theclass(1, 1, 1)

        self.assertFalse(me == ())
        self.assertTrue(me != ())
        self.assertFalse(() == me)
        self.assertTrue(() != me)

        self.assertIn(me, [1, 20, [], me])
        self.assertIn([], [me, 1, 20, []])

    def test_harmful_mixed_comparison(self):
        me = self.theclass(1, 1, 1)

        self.assertRaises(TypeError, lambda: me < ())
        self.assertRaises(TypeError, lambda: me <= ())
        self.assertRaises(TypeError, lambda: me > ())
        self.assertRaises(TypeError, lambda: me >= ())

        self.assertRaises(TypeError, lambda: () < me)
        self.assertRaises(TypeError, lambda: () <= me)
        self.assertRaises(TypeError, lambda: () > me)
        self.assertRaises(TypeError, lambda: () >= me)


class TestTime(HarmlessMixedComparison, unittest.TestCase):

    theclass = cpy_time
    theclass_cpython = cpython_time

    def test_basic_attributes(self):
        t = self.theclass(12, 0)
        t2 = self.theclass_cpython(12, 0)
        # Check adafruit_datetime module
        self.assertEqual(t.hour, 12)
        self.assertEqual(t.minute, 0)
        self.assertEqual(t.second, 0)
        self.assertEqual(t.microsecond, 0)
        # Validate against CPython datetime module
        self.assertEqual(t.hour, t2.hour)
        self.assertEqual(t.minute, t2.minute)
        self.assertEqual(t.second, t2.second)
        self.assertEqual(t.microsecond, t2.microsecond)

    def test_basic_attributes_nonzero(self):
        # Make sure all attributes are non-zero so bugs in
        # bit-shifting access show up.
        t = self.theclass(12, 59, 59, 8000)
        t2 = self.theclass_cpython(12, 59, 59, 8000)
        # Check adafruit_datetime module
        self.assertEqual(t.hour, 12)
        self.assertEqual(t.minute, 59)
        self.assertEqual(t.second, 59)
        self.assertEqual(t.microsecond, 8000)
        # Validate against CPython datetime module
        self.assertEqual(t.hour, t2.hour)
        self.assertEqual(t.minute, t2.minute)
        self.assertEqual(t.second, t2.second)
        self.assertEqual(t.microsecond, t2.microsecond)

    def test_comparing(self):
        args = [1, 2, 3, 4]
        t1 = self.theclass(*args)
        t2 = self.theclass(*args)
        self.assertEqual(t1, t2)
        self.assertTrue(t1 <= t2)
        self.assertTrue(t1 >= t2)
        self.assertTrue(not t1 != t2)
        self.assertTrue(not t1 < t2)
        self.assertTrue(not t1 > t2)

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

            self.assertRaises(TypeError, lambda: t1 <= badarg)
            self.assertRaises(TypeError, lambda: t1 < badarg)
            self.assertRaises(TypeError, lambda: t1 > badarg)
            self.assertRaises(TypeError, lambda: t1 >= badarg)
            self.assertRaises(TypeError, lambda: badarg <= t1)
            self.assertRaises(TypeError, lambda: badarg < t1)
            self.assertRaises(TypeError, lambda: badarg > t1)
            self.assertRaises(TypeError, lambda: badarg >= t1)

    def test_bad_constructor_arguments(self):
        # bad hours
        self.theclass(0, 0)  # no exception
        self.theclass(23, 0)  # no exception
        self.assertRaises(ValueError, self.theclass, -1, 0)
        self.assertRaises(ValueError, self.theclass, 24, 0)
        # bad minutes
        self.theclass(23, 0)  # no exception
        self.theclass(23, 59)  # no exception
        self.assertRaises(ValueError, self.theclass, 23, -1)
        self.assertRaises(ValueError, self.theclass, 23, 60)
        # bad seconds
        self.theclass(23, 59, 0)  # no exception
        self.theclass(23, 59, 59)  # no exception
        self.assertRaises(ValueError, self.theclass, 23, 59, -1)
        self.assertRaises(ValueError, self.theclass, 23, 59, 60)
        # bad microseconds
        self.theclass(23, 59, 59, 0)  # no exception
        self.theclass(23, 59, 59, 999999)  # no exception
        self.assertRaises(ValueError, self.theclass, 23, 59, 59, -1)
        self.assertRaises(ValueError, self.theclass, 23, 59, 59, 1000000)

    def test_hash_equality(self):
        d = self.theclass(23, 30, 17)
        e = self.theclass(23, 30, 17)
        self.assertEqual(d, e)
        self.assertEqual(hash(d), hash(e))

        dic = {d: 1}
        dic[e] = 2
        self.assertEqual(len(dic), 1)
        self.assertEqual(dic[d], 2)
        self.assertEqual(dic[e], 2)

        d = self.theclass(0, 5, 17)
        e = self.theclass(0, 5, 17)
        self.assertEqual(d, e)
        self.assertEqual(hash(d), hash(e))

        dic = {d: 1}
        dic[e] = 2
        self.assertEqual(len(dic), 1)
        self.assertEqual(dic[d], 2)
        self.assertEqual(dic[e], 2)

    def test_isoformat(self):
        t = self.theclass(4, 5, 1, 123)
        self.assertEqual(t.isoformat(), "04:05:01.000123")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass()
        self.assertEqual(t.isoformat(), "00:00:00")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=1)
        self.assertEqual(t.isoformat(), "00:00:00.000001")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=10)
        self.assertEqual(t.isoformat(), "00:00:00.000010")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=100)
        self.assertEqual(t.isoformat(), "00:00:00.000100")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=1000)
        self.assertEqual(t.isoformat(), "00:00:00.001000")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=10000)
        self.assertEqual(t.isoformat(), "00:00:00.010000")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=100000)
        self.assertEqual(t.isoformat(), "00:00:00.100000")
        self.assertEqual(t.isoformat(), str(t))

    def test_1653736(self):
        # verify it doesn't accept extra keyword arguments
        t = self.theclass(second=1)
        self.assertRaises(TypeError, t.isoformat, foo=3)

    @unittest.skip("strftime not implemented for CircuitPython time objects")
    def test_strftime(self):
        t = self.theclass(1, 2, 3, 4)
        self.assertEqual(t.strftime("%H %M %S %f"), "01 02 03 000004")
        # A naive object replaces %z and %Z with empty strings.
        self.assertEqual(t.strftime("'%z' '%Z'"), "'' ''")
        # bpo-34482: Check that surrogates don't cause a crash.
        try:
            t.strftime("%H\ud800%M")
        except UnicodeEncodeError:
            pass

    @unittest.skip("strftime not implemented for CircuitPython time objects")
    def test_format(self):
        t = self.theclass(1, 2, 3, 4)
        self.assertEqual(t.__format__(""), str(t))

        with self.assertRaisesRegex(TypeError, "must be str, not int"):
            t.__format__(123)

        # check that a derived class's __str__() gets called
        class A(self.theclass):
            def __str__(self):
                return "A"

        a = A(1, 2, 3, 4)
        self.assertEqual(a.__format__(""), "A")

        # check that a derived class's strftime gets called
        class B(self.theclass):
            def strftime(self, format_spec):
                return "B"

        b = B(1, 2, 3, 4)
        self.assertEqual(b.__format__(""), str(t))

        for fmt in [
            "%H %M %S",
        ]:
            self.assertEqual(t.__format__(fmt), t.strftime(fmt))
            self.assertEqual(a.__format__(fmt), t.strftime(fmt))
            self.assertEqual(b.__format__(fmt), "B")

    def test_str(self):
        self.assertEqual(str(self.theclass(1, 2, 3, 4)), "01:02:03.000004")
        self.assertEqual(str(self.theclass(10, 2, 3, 4000)), "10:02:03.004000")
        self.assertEqual(str(self.theclass(0, 2, 3, 400000)), "00:02:03.400000")
        self.assertEqual(str(self.theclass(12, 2, 3, 0)), "12:02:03")
        self.assertEqual(str(self.theclass(23, 15, 0, 0)), "23:15:00")

    def test_repr(self):
        name = "datetime." + self.theclass.__name__
        self.assertEqual(repr(self.theclass(1, 2, 3, 4)), "%s(1, 2, 3, 4)" % name)
        self.assertEqual(
            repr(self.theclass(10, 2, 3, 4000)), "%s(10, 2, 3, 4000)" % name
        )
        self.assertEqual(
            repr(self.theclass(0, 2, 3, 400000)), "%s(0, 2, 3, 400000)" % name
        )
        self.assertEqual(repr(self.theclass(12, 2, 3, 0)), "%s(12, 2, 3)" % name)
        self.assertEqual(repr(self.theclass(23, 15, 0, 0)), "%s(23, 15)" % name)

    @unittest.skip("Skip for CircuitPython  - not implemented")
    def test_resolution_info(self):
        self.assertIsInstance(self.theclass.min, self.theclass)
        self.assertIsInstance(self.theclass.max, self.theclass)
        self.assertIsInstance(self.theclass.resolution, timedelta)
        self.assertTrue(self.theclass.max > self.theclass.min)

    @unittest.skip("Skip for CircuitPython  - not implemented")
    def test_pickling(self):
        args = 20, 59, 16, 64 ** 2
        orig = self.theclass(*args)
        for pickler, unpickler, proto in pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)

    @unittest.skip("Skip for CircuitPython  - not implemented")
    def test_pickling_subclass_time(self):
        args = 20, 59, 16, 64 ** 2
        orig = SubclassTime(*args)
        for pickler, unpickler, proto in pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)

    def test_bool(self):
        # time is always True.
        cls = self.theclass
        self.assertTrue(cls(1))
        self.assertTrue(cls(0, 1))
        self.assertTrue(cls(0, 0, 1))
        self.assertTrue(cls(0, 0, 0, 1))
        self.assertTrue(cls(0))
        self.assertTrue(cls())

    @unittest.skip("Skip for CircuitPython  - replace() not implemented")
    def test_replace(self):
        cls = self.theclass
        args = [1, 2, 3, 4]
        base = cls(*args)
        self.assertEqual(base, base.replace())

        i = 0
        for name, newval in (
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
        base = cls(1)
        self.assertRaises(ValueError, base.replace, hour=24)
        self.assertRaises(ValueError, base.replace, minute=-1)
        self.assertRaises(ValueError, base.replace, second=100)
        self.assertRaises(ValueError, base.replace, microsecond=1000000)

    @unittest.skip("Skip for CircuitPython  - replace() not implemented")
    def test_subclass_replace(self):
        class TimeSubclass(self.theclass):
            pass

        ctime = TimeSubclass(12, 30)
        self.assertIs(type(ctime.replace(hour=10)), TimeSubclass)

    def test_subclass_time(self):
        class C(self.theclass):
            theAnswer = 42

            def __new__(cls, *args, **kws):
                temp = kws.copy()
                extra = temp.pop("extra")
                result = self.theclass.__new__(cls, *args, **temp)
                result.extra = extra
                return result

            def newmeth(self, start):
                return start + self.hour + self.second

        args = 4, 5, 6

        dt1 = self.theclass(*args)
        dt2 = C(*args, **{"extra": 7})

        self.assertEqual(dt2.__class__, C)
        self.assertEqual(dt2.theAnswer, 42)
        self.assertEqual(dt2.extra, 7)
        self.assertEqual(dt1.isoformat(), dt2.isoformat())
        self.assertEqual(dt2.newmeth(-7), dt1.hour + dt1.second - 7)

    def test_backdoor_resistance(self):
        # see TestDate.test_backdoor_resistance().
        base = "2:59.0"
        for hour_byte in " ", "9", chr(24), "\xff":
            self.assertRaises(TypeError, self.theclass, hour_byte + base[1:])
        # Good bytes, but bad tzinfo:
        with self.assertRaises(TypeError):
            self.theclass(bytes([1] * len(base)), "EST")

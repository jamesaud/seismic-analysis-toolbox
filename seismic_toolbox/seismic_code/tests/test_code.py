import unittest
from ..config import Time
from obspy import UTCDateTime
from ..helpers import *

class TestMethods(unittest.TestCase):
    def test_overlaps(self):
        time1 = UTCDateTime(2015, 1, 1, 10, 0, 10)
        time2 = UTCDateTime(2015, 1, 1, 10, 0, 19)
        time3 = UTCDateTime(2015, 1, 1, 10, 0, 30)
        t1 = Time(time1, time1 + 10)
        t2 = Time(time2, time2 + 10)
        t3 = Time(time3, time3 + 10)
        self.assertTrue(overlaps(t1, t2))
        self.assertFalse(overlaps(t2, t3))

    def test_encompassed(self):
        t = UTCDateTime(2015, 1, 1, 10, 0, 0)
        times = [Time(t + 10 * i, t + 10 * (i + 1)) for i in range(1, 7)]  # 1 minute of times
        times.append(Time(t + 1000, t + 1010))
        times.append(Time(t + 1010, t + 1020))
        times.sort()  # sorted just to remember that the function requires sorted times

        # Encompassed within the times
        self.assertTrue(encompassed(Time(t + 30, t + 40), times))

        # Not encompassed
        self.assertFalse(encompassed(Time(t + 990, t + 999), times))
        self.assertFalse(encompassed(Time(t - 10, t), times))

    def test_find_closest_index(self):
        lst = [1, 2, 3, 5, 6]
        self.assertEqual(find_closest_index(lst, 2), 2)  # defaults to finding index to the right
        self.assertEqual(find_closest_index(lst, 4), 3)

    def test_get_noise_times(self):
        t = UTCDateTime(2015, 1, 1, 10, 0, 0)
        exclude = [t + 60 * i for i in range(1, 11)]  # 10 times in a 10 minute range

        times = get_noise_times(exclude, startafter=exclude[0], endbefore=exclude[-1], amount=10, duration=10)

        # Make sure none of the noise times overlap with the event (exclude) times
        exclude_times = [Time(time, time + 10) for time in exclude]
        self.assertFalse(any((encompassed(Time(time, time + 10), exclude_times)) for time in times))

        # Make sure that the times are generated in the correct time window
        times.sort()
        self.assertTrue((times[0] > exclude[0]) and (times[-1] < exclude[-1]))

        # Should generate the correct amount
        self.assertEqual(len(times), 10)

    def test_slide(self):
        gen = slide(list(range(7)), 3)
        self.assertEqual(next(gen), [0, 1, 2])
        self.assertEqual(next(gen), [3, 4, 5])
        self.assertEqual(next(gen), [6])

        res = list(slide(list(range(7)), 3, 2))
        self.assertEqual(res, [[0, 1, 2], [2, 3, 4], [4, 5, 6]])
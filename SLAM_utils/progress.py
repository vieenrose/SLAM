# Progress module
# Copyright: Stavros Korokithakis, 2007
# License: GNU LGPL
#
import time
import unittest


class Progress:
    """Track the progress of an operation and calculate the projected time to
    its completion."""
    def __init__(self, totalitems, timeasstring = True):
        """Create a Progress instance. totalitems must be the total number of
        items we intend to process, so the class knows how far we've gone."""
        self._totalitems = totalitems
        self._starttime = time.time()
        self._timeasstring = timeasstring

    def timetostr(self, duration):
        """Convert seconds to D:H:M:S format (whichever applicable)."""
        # The verbosity is because this class should be as light as possible,
        # since it will probably be used in loops (hopefully not called very
        # often, but still).
        duration = int(duration)
        days = duration / 86400
        hours = (duration / 3600) % 24
        minutes = (duration / 60) % 60
        seconds = duration % 60
        timestring = "%(minutes)0.2d:%(seconds)0.2d"
        if days > 0:
            timestring = "%(days)0.2d:%(hours)0.2d:" + timestring
        elif hours > 0:
            timestring = "%(hours)0.2d:" + timestring
        return timestring % {"days": days, "hours": hours, "minutes": minutes, "seconds": seconds}

    def progress(self, itemnumber):
        """We have progressed itemnumber items, so return our completion
        percentage, items/total items, total time and projected total
        time."""
        elapsed = time.time() - self._starttime
        # Multiply by 1.0 to force conversion to long.
        percentcomplete = (1.0 * itemnumber) / self._totalitems
        try:
            total = int(elapsed / percentcomplete)
        except ZeroDivisionError:
            total = 0
        if self._timeasstring:
            return (
                self.timetostr(elapsed),
                self.timetostr(total),
                int(percentcomplete * 100),
                itemnumber, self._totalitems
                )
        else:
            return (
                int(elapsed),
                int(total),
                int(percentcomplete * 100),
                itemnumber,
                self._totalitems
                )

    def progressstring(self, itemnumber):
        """Return a string detailing the current progress."""
        timings = self.progress(itemnumber)
        if itemnumber == self._totalitems:
            return "Done in %s, processed %s " % \
            (timings[0], timings[4])
        else:
            return "%s/%s, %s%%, %s/%s" % timings
        return progstr


class UnitTests(unittest.TestCase):
    def setUp(self):
        self.progress = Progress(100)

    def testtimetostr(self):
        tests = [(10, "00:10"),
            (75, "01:15"),
            (4000, "01:06:40"),
            (87123, "01:00:12:03"),
            (187123, "02:03:58:43"),
                ]
        for test, result in tests:
            self.assertEqual(self.progress.timetostr(test), result)


if __name__ == "__main__":
    prog = Progress(100)
    for i in range(100):
        print(prog.progressstring(i))

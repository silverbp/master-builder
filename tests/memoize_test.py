from __future__ import absolute_import
from __future__ import unicode_literals

from mb.lib.memoize import memoize


class SomeClass:
    def __init__(self):
        self._x = 0

    def _the_test(self, number):
        self._x += 1
        return number * self._x

    @memoize
    def TestCache1(self, number):
        return self._the_test(number)

    @memoize("self", "number")
    def TestCache2(self, number, **kw):
        tmp = self._the_test(kw["number2"])
        return self._the_test(tmp - number)


def test_NoArgumentsPassed_UsesAllArgumentsForCache():
    someClass = SomeClass()
    assert someClass._the_test(5) == 5
    assert someClass.TestCache1(5) == 10
    assert someClass.TestCache1(5) == 10


def test_ArgumentsPassedToUseForCache_UsesArgumentsForCache():
    someClass = SomeClass()
    assert someClass.TestCache2(5, number2=10) == 10
    assert someClass.TestCache2(5, number2=10) == 10

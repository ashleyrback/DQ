#!/usr/bin/env python
#
# list_manips.py
#
# A collection of useful methods for manipulating lists
#
# Author A R Back - 28/02/2014 <ab571@sussex.ac.uk> : First revision
###############################################################################

def item_containing(expression, list_):
    """ Iterates over all items in the list_ supplied and searches each
    list item for the supplied expression. Assumes both list_ and
    expression are stings. Returns index of the list entry.
    """
    _index = None
    try:
        assert (type(expression) is str), ("Supplied expression must "
                                           "be a string")
        for index, item in enumerate(list_):
            assert (type(item) is str), ("list_manips.item_containing:\n "
                                         " --> list_ items must be strings")
            if (item.find(expression) >= 0):
                _index = index
    except AssertionError as detail:
        print "list_manips.item_containing error: ", detail
    return _index

#!/usr/bin/env python
#
# bit_manips.py
#
# A collection of useful methods involving bit/bitmask manipulations
#
# Author A R Back - 27/02/2014 <ab571@sussex.ac.uk> : First revision
#
###############################################################################

def query_mask(bit, mask):
    """ Queries a given bit in a bitmask, returns True if the bit is a one
    and returns False if the bit is a zero. Can also specify an applied mask,
    then the function will check if the to make sure the
    """
    query = 1<<bit # Shifts 1 to the position of bit = 1*(2**bit)
    result = False
    if (query&mask == query):
        result = True
    return result
    
def query_mask(bit, mask, applied):
    """ Queries a given bit in a bitmask, returns true if the bit is a one
    and returns false if the bit is a zero. Overloads the original version of
    query mask so that here you can also specify an applied mask. Only returns
    True if the bit is a one in both the mask and applied mask.
    """
    query = 1<<bit # Shifts 1 to the position of bit = 1*(2**bit)
    result = False
    if (query&mask == query) and (query&applied == query):
        result = True
    return result


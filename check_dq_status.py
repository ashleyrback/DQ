#!/usr/bin/env python
#
# check_dq_status.py
#
# Gets the DQ status word from a processed root file, identifies which DQ
# checks passed/failed
#
# Author A R Back - 26/02/2014 <ab571@sussex.ac.uk> : First revision
#
###############################################################################
import rat

class CheckDQStatus(object):
    """ Base class for analysing the DQ status word """
    def __init__(self, path):
        """ Initialises the class members, give specified path to a DQ- 
        processed root file
        """
        self._path = path
        print "file: " + self._path
    def get_dq_masks(self):
        """ Reads the RAT DS in DQ-processed root file. Returns DQ status word
        """
        events = rat.dsreader(self._path)
        ds, run = events.next()
        self._dq_applied = run.GetDQApplied()
        self._dq_mask = run.GetDQMask()
        return (self._dq_applied, self._dq_mask)

###############################################################################
if __name__=="__main__":
    from ROOT import TH1D

    import argparse    
    import os
    import re
    import math

    from bit_manips import query_mask

    parser = argparse.ArgumentParser(description="DQ status word analyser"
                                     "specify either directory of files or a"
                                     "single file to analyse")
    parser.add_argument("directory", help="indicate directory containing DQ"
                        "processed root files")
    args = parser.parse_args()

    file_list = []
    for root, dirs, files in os.walk(args.directory):
        for file in files:
            match = re.search(r"_p[0-9]+.root", file)
            if match:
                file_list.append(os.path.join(root, file))
    
    max_bits = 12

    hist_title = "Percentage pass rate for DQ checks"
    hist_dq_checks = TH1D(hist_title, hist_title, max_bits, 0, max_bits) 
    for file in file_list:
        dq_status = CheckDQStatus(file)
        applied, status = dq_status.get_dq_masks()
        for bit in range(0, int(math.log(applied, 2))):
            passed_check = query_mask(bit, status, applied)
            if passed_check:
                hist_dq_checks.Fill(bit)


    hist_dq_checks.Draw()
    raw_input("RET to exit")

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
        self._dq_flags = run.GetDataQualityFlags().GetFlags(0)
        print self._dq_flags
        self._dq_applied = run.GetDataQualityFlags().GetApplied(0)
        print self._dq_applied
        return self._dq_flags, self._dq_applied

###############################################################################
if __name__=="__main__":
    from ROOT import TH1D
    from ROOT import TFile

    import argparse    
    import os
    import re
    import math

    parser = argparse.ArgumentParser(description="DQ status word analyser"
                                     "specify either directory of files or a"
                                     "single file to analyse")
    parser.add_argument("directory", help="indicate directory containing DQ"
                        "processed root files")
    parser.add_argument("-p", "--passnum", type=int,
                        help="supply a pass number to use processed Root files")
    parser.add_argument("-w", "--write", help="Write histograms to file",
                        action="store_true")
    args = parser.parse_args()

    file_list = []
    for root, dirs, files in os.walk(args.directory):
        for file in files:
            match = False
            if args.passnum:
                if (file.find(r"SNOP_[0-9]+_[0-9]+_p"+str(args.passnum)+".root") > 0):
                    match = True
            else:
                match = re.search(r"SNOP_[0-9]+_[0-9]+_p[0-9]+.root", file)
            if match:
                file_list.append(os.path.join(root, file))
    max_bits = 13
    utility = rat.utility()
    dq_bits = utility.GetDataQualityBits()

    hist_title = "Performance of DQ checks"
    hist_dq_flags = TH1D("TH1D_dq_status", hist_title, max_bits, 0, max_bits) 
    hist_dq_flags.GetXaxis().SetBinLabel(1, "run_type")
    hist_dq_flags.GetXaxis().SetBinLabel(2, "mc_flag")
    hist_dq_flags.GetXaxis().SetBinLabel(3, "trigger")
    hist_dq_flags.GetXaxis().SetBinLabel(4, "run_length")
    hist_dq_flags.GetXaxis().SetBinLabel(5, "general_coverage")
    hist_dq_flags.GetXaxis().SetBinLabel(6, "crate_coverage")
    hist_dq_flags.GetXaxis().SetBinLabel(7, "panel_coverage")
    hist_dq_flags.GetXaxis().SetBinLabel(8, "run_header")
    hist_dq_flags.GetXaxis().SetBinLabel(9, "delta_t_comparison")
    hist_dq_flags.GetXaxis().SetBinLabel(10, "clock_forward")
    hist_dq_flags.GetXaxis().SetBinLabel(11, "event_separation")
    hist_dq_flags.GetXaxis().SetBinLabel(12, "retriggers")
    hist_dq_flags.GetXaxis().SetBinLabel(13, "event_rate")
    hist_dq_applied = TH1D("TH1D_dq_applied", hist_title, max_bits, 0, max_bits) 
    hist_dq_applied.GetXaxis().SetBinLabel(1, "run_type")
    hist_dq_applied.GetXaxis().SetBinLabel(2, "mc_flag")
    hist_dq_applied.GetXaxis().SetBinLabel(3, "trigger")
    hist_dq_applied.GetXaxis().SetBinLabel(4, "run_length")
    hist_dq_applied.GetXaxis().SetBinLabel(5, "general_coverage")
    hist_dq_applied.GetXaxis().SetBinLabel(6, "crate_coverage")
    hist_dq_applied.GetXaxis().SetBinLabel(7, "panel_coverage")
    hist_dq_applied.GetXaxis().SetBinLabel(8, "run_header")
    hist_dq_applied.GetXaxis().SetBinLabel(9, "delta_t_comparison")
    hist_dq_applied.GetXaxis().SetBinLabel(10, "clock_forward")
    hist_dq_applied.GetXaxis().SetBinLabel(11, "event_separation")
    hist_dq_applied.GetXaxis().SetBinLabel(12, "retriggers")
    hist_dq_applied.GetXaxis().SetBinLabel(13, "event_rate")
    for file in file_list:
        events = rat.dsreader(file)
        ds, run = events.next()
        flags = run.GetDataQualityFlags().GetFlags(0)
        applied = run.GetDataQualityFlags().GetApplied(0)
        if(flags.Get(dq_bits.GetBitIndex("run_type"))):
            hist_dq_flags.AddBinContent(1)
        if(applied.Get(dq_bits.GetBitIndex("run_type"))):
            hist_dq_applied.AddBinContent(1)
        if(flags.Get(dq_bits.GetBitIndex("mc_flag"))):
            hist_dq_flags.AddBinContent(2)
        if(applied.Get(dq_bits.GetBitIndex("mc_flag"))):
            hist_dq_applied.AddBinContent(2)
        if(flags.Get(dq_bits.GetBitIndex("trigger"))):
            hist_dq_flags.AddBinContent(3)
        if(applied.Get(dq_bits.GetBitIndex("trigger"))):
            hist_dq_applied.AddBinContent(3)
        if(flags.Get(dq_bits.GetBitIndex("run_length"))):
            hist_dq_flags.AddBinContent(4)
        if(applied.Get(dq_bits.GetBitIndex("run_length"))):
            hist_dq_applied.AddBinContent(4)
        if(flags.Get(dq_bits.GetBitIndex("general_coverage"))):
            hist_dq_flags.AddBinContent(5)
        if(applied.Get(dq_bits.GetBitIndex("general_coverage"))):
            hist_dq_applied.AddBinContent(5)
        if(flags.Get(dq_bits.GetBitIndex("crate_coverage"))):
            hist_dq_flags.AddBinContent(6)
        if(applied.Get(dq_bits.GetBitIndex("crate_coverage"))):
            hist_dq_applied.AddBinContent(6)
        if(flags.Get(dq_bits.GetBitIndex("panel_coverage"))):
            hist_dq_flags.AddBinContent(7)
        if(applied.Get(dq_bits.GetBitIndex("panel_coverage"))):
            hist_dq_applied.AddBinContent(7)
        if(flags.Get(dq_bits.GetBitIndex("run_header"))):
            hist_dq_flags.AddBinContent(8)
        if(applied.Get(dq_bits.GetBitIndex("run_header"))):
            hist_dq_applied.AddBinContent(8)
        if(flags.Get(dq_bits.GetBitIndex("delta_t_comparison"))):
            hist_dq_flags.AddBinContent(9)
        if(applied.Get(dq_bits.GetBitIndex("delta_t_comparison"))):
            hist_dq_applied.AddBinContent(9)
        if(flags.Get(dq_bits.GetBitIndex("clock_forward"))):
            hist_dq_flags.AddBinContent(10)
        if(applied.Get(dq_bits.GetBitIndex("clock_forward"))):
            hist_dq_applied.AddBinContent(10)
        if(flags.Get(dq_bits.GetBitIndex("event_separation"))):
            hist_dq_flags.AddBinContent(11)
        if(applied.Get(dq_bits.GetBitIndex("event_separation"))):
            hist_dq_applied.AddBinContent(11)
        if(flags.Get(dq_bits.GetBitIndex("retriggers"))):
            hist_dq_flags.AddBinContent(12)
        if(applied.Get(dq_bits.GetBitIndex("retriggers"))):
            hist_dq_applied.AddBinContent(12)
        if(flags.Get(dq_bits.GetBitIndex("event_rate"))):
            hist_dq_flags.AddBinContent(13)
        if(applied.Get(dq_bits.GetBitIndex("event_rate"))):
            hist_dq_applied.AddBinContent(13)
    hist_dq_flags.Draw()
    if args.write:
        if args.passnum:
            filename = "check_dq_status_records_p"+str(args.passnum)+".root"
        else:
            filename = "check_dq_status_records.root"
        output_file = TFile(filename, "RECREATE")
        hist_dq_checks.Write("TH1D_dq_status")
        output_file.Write()
        output_file.ls()
        output_file.Close()
    raw_input("RETURN to exit")

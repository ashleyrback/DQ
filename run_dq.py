#!/usr/bin/env python
#
# run_dq.py
#
# Runs DQ processors on raw zdab files in a given directory
#
# Author A R Back - 04/03/2014 <ab571@sussex.ac.uk> : First revision
#
###############################################################################
import file_manips
import list_manips

import subprocess
import sys
import os
import re
import socket
import shutil

class RunDQ(object):
    """ Base class for DQ processing """
    def __init__(self, path, pass_number=None):
        """ Initialises the class members, given specified path to zdab file or
        previously DQ-processed RAT-Root file.
        """
        self._path = path
        self._dir, self._filename = file_manips.split_path(path)
        self._name, self._ext = file_manips.split_ext(self._filename)
        print self._name
        self._pass_number = pass_number
        if (self._ext == ".zdab"):
            self._root_path = None
        elif (self._ext == ".root"):
            name_attributes = self._name.split("_")
            pass_index = list_manips.item_containing("p"+str(self._pass_number),
                                                     name_attributes)
            try:
                error_message = "Filename does not contain pass count _p"
                error_message += str(self._pass_number)
                error_message += (". Please supply a valid processed Root file"
                                  " or raw zdab")
                assert (pass_index != None), error_message
                self._name = ""
                for index in range(0, pass_index):
                    self._name += name_attributes[index] + "_"
            except AssertionError as detail:
                print "RunDQ.__init__: error", detail
                sys.exit(1)
            self._root_path = self._path
        self._mac_path = None
    def convert_zdab(self, root_dir=""):
        """ Uses the zdab2root converter in rat-tools to convert zdab file to 
        RAT Root file.
        """
        try:
            assert (self._pass_number == None), ("Processed Root file already " 
                                                 "exists, no need to convert!")
            RATZDAB_ROOT = os.environ["RATZDAB_ROOT"]
        except KeyError as detail:
            print "RunDQ.convert_zdab: error", detail, "not set"
            print " --> source correct environment scripts before running!"
            sys.exit(1)
        except AssertionError as detail:
            print "RunDQ.convert_zdab: error", detail
            sys.exit(1)
        RATZDAB_DIR = RATZDAB_ROOT+"/bin/"
        if (root_dir == ""):
            root_dir = os.getcwd()
        self._root_dir = root_dir+"/"
        self._root_path = self._root_dir+self._name+".root"
        command = "/"+RATZDAB_DIR+"zdab2root "+self._path+" "+self._root_path
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output = process.communicate()[0]
    def write_macro(self, mac_dir=""):
        """ Writes macro based on standard macro template """
        if (mac_dir == ""):
            mac_dir = os.getcwd()
        self._mac_dir = mac_dir+"/"
        self._mac_path = self._mac_dir+self._name+".mac"
        mac_file = open(self._mac_path, "w")
        mac_file.write("/run/initialize\n")
        mac_file.write("/rat/proc dqrunproc\n")
        mac_file.write("/rat/proc dqtimeproc\n")
        mac_file.write("/rat/proclast outroot\n")
        if self._pass_number == None:
            mac_file.write("/rat/procset file \""+self._dir+self._name+"_p1.root\"\n")
        else:
            self._pass_number += 1
            mac_file.write("/rat/procset file \""+self._dir+self._name+"p" \
                               +str(self._pass_number)+".root\"\n")
        try:
            assert (self._root_path != None), \
                "method RunDQ.convert_zdab must be used before RunDQ.write_macro" 
            mac_file.write("/rat/inroot/read "+self._root_path+"\n")
        except AssertionError as detail:
            print "RunDQ.write_macro: error cannot use inroot producer,", detail
            sys.exit(1)
        mac_file.write("exit")
        mac_file.close()
    def run_rat(self):
        """ Runs rat using the macro created in write_macro """
        try:
            assert (self._mac_path != None), \
                "method RunDQ.write_macro must be used before RunDQ.run_rat" 
            command = "rat "+self._mac_path
            os.environ["RATROOT"]
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            output = process.communicate()[0]
        except AssertionError as detail:
            print "RunDQ.run_rat: error cannot locate macro,", detail
            sys.exit(1)
        except KeyError as detail:
            print "RunDQ.run_rat: error", detail, "not set"
            print " --> source correct environment scripts before running!"
            sys.exit(1)
    def clean_up(self, overwrite=False):
        """ Move DQ outputs to their appropriate directory """
        try:
            records_dir = os.environ["RECORDS"]
            plots_dir = os.environ["PLOTS"]
            logs_dir = os.environ["LOGS"]
        except KeyError as detail:
            print "RunDQ.clean_up: error", detail, "not set"
            print " --> source analysis environment scripts before running!"
            sys.exit(1)
        for root, dirs, files in os.walk(os.getcwd()):
            for file in files:
                is_record = re.search(r"^DATAQUALITY_RECORDS_[0-9]+\..*", file)
                is_plot = re.search(r".*\.png$", file)
                hostname = socket.gethostname()
                is_log =  re.search(r"^rat\."+hostname+r"\.[0-9]+\.log$", file)
                if is_record:
                    file_manips.copy_file(os.path.join(root, file), records_dir,
                                          self._pass_number, overwrite)
                elif is_plot:
                    file_manips.copy_file(os.path.join(root, file), plots_dir,
                                          self._pass_number, overwrite)
                elif is_log:
                    file_manips.copy_file(os.path.join(root, file), logs_dir,
                                          self._pass_number, overwrite)

###############################################################################
if __name__=="__main__":
    import argparse    
    import contextlib
    import tempfile

    parser = argparse.ArgumentParser(description="Run DQ processors")
    parser.add_argument("directory", help="indicate directory containing"
                        "raw zdab files to be processed")
    parser.add_argument("-p", "--passnum", type=int,
                        help="supply a pass number to use processed Root files")
    parser.add_argument("-o", "--overwrite", help="if output record files/"
                        "plots already exist, overwrite", action="store_true")
    args = parser.parse_args()

    # set environment
    env=os.environ.copy()

    # make list of files
    file_list = []
    for root, dirs, files in os.walk(args.directory):
        for file in files:
            if args.passnum == None:
                match = re.search(r"_[0-9]+.zdab", file)
            else:
                match = re.search(r"_p[0-9]+.root", file)
            if match:
                file_list.append(os.path.join(root, file))
    
    # make temporary directory to write macro files
    @contextlib.contextmanager
    def temporary_directory(*args, **kwargs):
        d = tempfile.mkdtemp(*args, **kwargs)
        try:
            yield d
        finally:
            shutil.rmtree(d)

    with temporary_directory() as temp_dir:
        for file in file_list:
            data_quality = RunDQ(file, args.passnum)
            if (args.passnum == None):
                data_quality.convert_zdab(temp_dir)
            data_quality.write_macro(temp_dir)
            data_quality.run_rat()
            data_quality.clean_up(args.overwrite)

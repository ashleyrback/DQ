#!/usr/bin/env python
#
# run_dq.py
#
# Runs DQ processors on raw zdab files in a given directory
#
# Author A R Back
#
# 04/03/2014 <ab571@sussex.ac.uk> : First revision
# 29/05/2014 <ab571@sussex.ac.uk> : Update for RAT-4.6
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
        self._zdab_path = None
        self._root_path = None
        if (self._ext == ".zdab"):
            self._zdab_path = self._path
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
        self._write_macro_path = None
    def convert_zdab(self, root_dir=""):
        """ DEPRECIATED METHOD - use inzdab in macro
        Uses the zdab2root converter in rat-tools to convert zdab file to 
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
    def write_macro(self, write_macro_dir="default",
                    read_macro_path="default"):
        """ Writes macro based on standard macro template """
        # Open file for writing macro to
        if (write_macro_dir == "default"):
            write_macro_dir = os.getcwd()
        self._write_macro_dir = write_macro_dir+"/"
        self._write_macro_path = self._write_macro_dir+self._name+".mac"
        write_macro = open(self._write_macro_path, "w")
        # Read from template macro
        if (read_macro_path == "default"):
            read_macro_path = os.environ.get("RATROOT") \
                + "/mac/processing/processing.mac"
        for line in open(read_macro_path):
            if (line.find("/rat/proclast outroot") >= 0):
                write_macro.write(line)
                if self._pass_number == None:
                    write_macro.write("/rat/procset file \""+self._dir+self._name\
                                       +"_p1.root\"\n")
                else:
                    self._pass_number += 1
                    write_macro.write("/rat/procset file \""+self._dir+self._name\
                                       +"p"+str(self._pass_number)+".root\"\n")
            elif (line.find("/rat/inzdab/read_default") >= 0):
                if (self._zdab_path != None):
                    write_macro.write(line.split("_")[0]+" "+self._zdab_path+"\n")
                elif (self._root_path != None):
                    write_macro.write("/rat/inroot/read "+self._root_path+"\n")
                else:
                    try:
                        assert ((self._zdab_path != None) or \
                                    (self._root_path != None)), \
                                    "No valid zdab or root file"
                    except AssertionError as detail:
                        print "RunDQ.write_macro: ERROR", detail
                        sys.exit(1)
            else:
                write_macro.write(line)
        write_macro.close()
        for line in open(self._write_macro_path, "r"):
            print line
    def run_rat(self):
        """ Runs rat using the macro created in write_macro """
        try:
            assert (self._write_macro_path != None), \
                "method RunDQ.write_macro must be used before RunDQ.run_rat" 
            command = "rat "+self._write_macro_path
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
                                          self._pass_number, 0, overwrite)
                elif is_plot:
                    file_manips.copy_file(os.path.join(root, file), plots_dir,
                                          self._pass_number, 0, overwrite)
                elif is_log:
                    file_manips.copy_file(os.path.join(root, file), logs_dir,
                                          self._pass_number, 0, overwrite)

###############################################################################
if __name__=="__main__":
    import argparse    
    import contextlib
    import tempfile

    parser = argparse.ArgumentParser(description="Run DQ processors")
    parser.add_argument("directory", help="indicate directory containing"
                        "raw zdab files to be processed")
    parser.add_argument("-p", "--passnum", type=int, default=0,
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
            if args.passnum == 0: # zdab
                match = re.search(r"_[0-9]+.zdab", file)
            else:
                match = re.search(r"_p"+str(args.passnum)+".root", file)
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
            print file
            data_quality = RunDQ(file, args.passnum)
            data_quality.write_macro(temp_dir)
            data_quality.run_rat()
            data_quality.clean_up(args.overwrite)

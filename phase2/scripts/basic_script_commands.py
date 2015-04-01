#!/usr/bin/python

import sys

def display_help():
 print "_________________________________________________\n"
 print "The script <manage.py> can be used to:"
 print "\t--Don't perform linear regressions.(--no-regressions)"
 print "\t--Remove invalid rows of CSVs. That is, those with non-numeric or empty cells. (--clean)"
 print "\t--Write the \"cleansed\" data to a CSV. (--clean output_file)"
 print "\t--Normalize the CSV (after cleaning if both are selected). (--normalize)"
 print "\t--Write the \"normalized\" data to a CSV (same output as \"--clean\"). (--normalize output_file)"
 print "\t--Print the linear regression results.(--show-regressions)"
 print "\t  --Write this these calculations in a JSON file.(--show-regressions output_file)"
 print "\t--Print the R-squared values for each regression. (--calculate-r2)"
 print "\t  --Store these calculations in a JSON file. (--calculate-r2 output_file)"
 print "\t--Print a random sampling of N rows from the CSV. (--random-sampling N)"
 print "\t  --Store these N rows as a json file. (--random-sampling N output_file)"
 print "\t--Print a KD-Tree from the rows in the CSV. (--create-kd-tree)"
 print "\t  --Store the tree in a json file. (--create-kd-tree output_file)"
 print "\t--Remove column N from the CSV where N is zero-indexed. (--remove-cols output_file N)"
 print "\n"
 print "\t--In order to create all files with default values, use only the option: --default"
 print "\t--To create a subdirectory to contain the default files, use: --default new_directory"
 print "\n"
 print "The first argument passed to this script must be the input file. IE:"
 print "\t\t python manage.py input_file.csv [OPTIONS]\n"
 print "\t--In order to hide the progress display, use the option: --hide-extra-output"
 print "_________________________________________________\n"
 sys.exit()


def fatal_error(message):
 print "Fatal Error:: {}".format(message)
 sys.exit()

def message(msg, show = True):
  if show:
   print msg

def user_verify(msg):
 return raw_input(msg).lower()=="y"

#http://stackoverflow.com/questions/11887762/how-to-compare-version-style-strings
def versiontuple(v):
 return tuple(map(int, (v.split("."))))

def check_version():
 return versiontuple("2.7.0") > versiontuple(sys.version_info[:3])

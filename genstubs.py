#! /usr/bin/env python

import sys

# conduct argument checking
if(len(sys.argv) != 2):
    print("Usage: genstubs.py <filename>")
    print("\t<filename> must point to a c++ header file")
    sys.exit()

# ensure the argument connects to a file that be opened
try:
    fp = open(sys.argv[1], 'r')
except IOError:
    print("Error: unable to open file " + str(sys.argv[1]))
    sys.exit()

lines = fp.readlines()
classes = []

for line in lines:
    words = str.split(line)
    if len(words) > 0:
        if words[0] == "class":     #found a line with word class
            print ("found class: "+words[1])
            print ("The last word in the line is: "+str(words[-1]))
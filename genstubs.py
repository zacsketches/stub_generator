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

#************************************************************************
#*                         DEBUG CONROL
#************************************************************************
DEBUG_FORWARD = 0
DEBUG_MAIN = 1

#************************************************************************
#*                         Basic Error Feedback
#************************************************************************
def error(msg):
    print(msg)
    sys.exit()

#************************************************************************
#*                         Forward Declaration Test
#************************************************************************
def forward_declaration(words):
    # argument is list of words from a line that begins with 'class'
    # returns true if the line if a forward declaration or false
    # if the line is in the first line in the class definition
    result = False
    
    last_word = words[-1]
    if DEBUG_FORWARD:
        print("the last word in the line is: " + last_word)
        print("the last char in the word is: " + last_word[-1])

    # only the forward declaration has a semi-colon as the last symbol of
    # the last word
    if last_word[-1] == ';':
        result = True
        
    return result

#************************************************************************
#*                         Find Class Name
#************************************************************************
def class_name(words):
    # argument is a list of words from a line that begins with 'class'
    # returns the class name
    # expects a valid class definition line as input...not a forward
    # declaration
    result = ""
    
    if len(words) >= 2:
        result = words[1]
    else:
        error("Error: The list of words passed to class_name was not at least two words long")
            
    return result
    

#************************************************************************
#*                         MAIN
#************************************************************************
lines = fp.readlines()
classes = []

for line in lines:
    words = str.split(line)
    if len(words) > 0:
        if words[0] == "class":     #found a line with word class
            if not forward_declaration(words):
                classes.append(class_name(words))

if DEBUG_MAIN: 
    print(classes)


                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
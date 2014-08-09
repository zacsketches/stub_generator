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
DEBUG_LAST_LINE = 1

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
#*                         Find the last line of the class
#************************************************************************
def class_end(start_index, lines):
    # argument is the line number of the first line in the class and the
    # List of lines in the file
    # if we start scanning at this point we should find the first '{'
    # right around there and then a closing '}' at some point later.
    # we have to watch out for inline definitions that will have their
    # own pair of curly braces.  So I'm really looking for the first
    # unbalanced '}'
    end_index = 0
    inline_open = False
    found_class_open_curly = False
    found_class_closing_curly = False
    
    cur_line_index = start_index
    for line in lines[start_index : ]:
        if not found_class_closing_curly:
            for word in line:
                for char in word:
                    if (char == '{' and not found_class_open_curly):
                        found_class_open_curly = True
                        if DEBUG_LAST_LINE:
                            print ("Found class open curly at index: " + str(cur_line_index))
                        break;
                    if (char == '{' and found_class_open_curly):
                        if DEBUG_LAST_LINE:
                            print ("Found inline open curly at index: " + str(cur_line_index))
                        inline_open = True
                        break;
                    if (char == '}' and inline_open):
                        if DEBUG_LAST_LINE:
                            print ("Found inline closing curly at index: " + str(cur_line_index))                        
                        inline_open = False
                        break;
                    if (char == '}' and not inline_open):
                        if DEBUG_LAST_LINE:
                            print ("Found class closing curly at index: " + str(cur_line_index))                        
                        end_index = cur_line_index
                        found_class_closing_curly = True
        else:
            break
        cur_line_index = cur_line_index + 1
        
    if end_index == 0:
        error("Could not find closing curly for the class that begins at \
            index: "+str(start_index))
    
    return end_index
    

#************************************************************************
#*                         MAIN
#************************************************************************
lines = fp.readlines()
classes = {}

# fill the classes dict with the class names and starting line numbers for
# each class definition
line_number = 1
for line in lines:
    words = str.split(line)
    if len(words) > 0:
        if words[0] == "class":     #found a line with word class
            if not forward_declaration(words):
                classes[class_name(words)] = line_number
    line_number = line_number + 1

# iterate over each class and create a dictionary of method name: str_arguments
for key in classes:
    start_line = classes[key]
    end_line = class_end(start_line, lines)
    
if DEBUG_MAIN: 
    print(classes)


                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
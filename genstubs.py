#! /usr/bin/env python

# Zac Staples on 9 Aug 2014
# Lots to improve upon here, but it gets me started.
# Some specific improvement would be to handle discriminators like static, and virtual
# I also need to handle the double set of parens in an operator function
# like this one:
#   bool operator()(const int arg1, cont int arg2)

import sys

# conduct argument checking
if(len(sys.argv) < 2):
    print("Usage: genstubs.py <in_filename> [<out_filename> = out.cpp]")
    print("\t<in_filename> must point to a c++ header file")
    print("\t<out_filename> is optional and is the filename genstubs will write to")
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
DEBUG_MAIN = 0
DEBUG_LAST_LINE = 0
DEBUG_SLICES = 0
DEBUG_CALC_SLICES = 0
DEBUG_HAS_INLINE = 0

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
#*               Return the list of slices excluding inline functions
#************************************************************************
def find_inline_slices(start_index, end_index, lines):
    # argument is the index of the first line in the class and the
    # index of the last line and the list of lines
    # If I slice at start+1 : end-1 then I can find every blanced pair of 
    # curly braces and use them as start/stop points for the inline functions
    # and enums
    # return a List of (start, stop) tuples
    
    slices = []
    inline_start = 0
    inline_stop = 0
    
    start_index = start_index+1
    end_index = end_index       #we don't adjust this because we search [start: end)

    inline_open = False
    
    cur_line_index = start_index
    for line in lines[start_index : end_index]:
        for word in line:
            for char in word:
                if (char == '{'):
                    if DEBUG_SLICES:
                        print ("Found inline open curly at index: " + str(cur_line_index))
                    inline_open = True
                    inline_start = cur_line_index
                    break;
                if (char == '}' and inline_open):
                    if DEBUG_SLICES:
                        print ("Found inline closing curly at index: " + str(cur_line_index))                        
                    inline_open = False
                    inline_stop = cur_line_index
                    slices.append((inline_start, inline_stop))
                    break;
        cur_line_index = cur_line_index + 1
    
    if len(slices) == 0:
        slices.append((start_index, end_index))

    if DEBUG_SLICES:
        print ("slices constains: ", slices)
    
    return slices

#************************************************************************
#*               Calculate the search slices for a class
#************************************************************************
def calc_search_slices(start_index, end_index, inline_slices):
    # just stitch toget a list of tuples from the given index points
    slices = []
    
    start = start_index
    if len(inline_slices) > 0:
        for end, next_start in inline_slices:
            slices.append((start, end))
            start = next_start + 1
    end = end_index
    slices.append((start, end))
    
    if DEBUG_CALC_SLICES:
        print ("calc slices contains: ", slices)
    
    return slices
 
#************************************************************************
#*                Has Inline Slices     
#************************************************************************
def has_inline_slices(start_index, end_index, lines):
    # return true is the function has any inline slices
    has_inlines = False
    
    start_index = start_index+1
    end_index = end_index       #we don't adjust this because we search [start: end)
    
    cur_line_index = start_index
    for line in lines[start_index : end_index]:
        if has_inlines: break      #only look if we haven't found an inline yet
        for word in line:
            for char in word:
                if (char == '{'):
                    if DEBUG_HAS_INLINE:
                        print ("Found inline open curly at index: " + str(cur_line_index))
                    has_inlines = True;
                    break;
        cur_line_index = cur_line_index + 1
    
    return has_inlines

#************************************************************************
#*                         MAIN
#************************************************************************
lines = fp.readlines()
classes = {}
class_inline_slices = {}
class_search_slices = {}
class_methods = {}

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

# create a dictionary of slices for each class that may contain method names
for key in classes:
    start_index = classes[key]
    end_index = class_end(start_index, lines)

    key_inline_slices = find_inline_slices(start_index, end_index, lines)
    class_inline_slices[key] = key_inline_slices
    
    if has_inline_slices(start_index, end_index, lines):
        key_search_slices = calc_search_slices(start_index, end_index, key_inline_slices)
        class_search_slices[key] = key_search_slices
    else:
        class_search_slices[key] = [(start_index, end_index)]
        
# open the output file
out_file = "out.cpp"
if len(sys.argv)>2:
    out_file = sys.argv[2]
out = open(out_file, "w")

out.write("// Generateed by "+str(sys.argv[0])+"\n")
out.write("//      based on "+str(sys.argv[1])+"\n")
out.write("\n")
out.write("#include <"+sys.argv[1]+">\n")
out.write("\n")
    
# iterate over each class dictionary and find each method.
# each class is a dict key with tuples(return_type, method_name, arguments)
for key in class_search_slices:
    out.write("//************************************************************************\n")
    out.write("//*                     CLASS "+key.upper()+"\n")
    out.write("//************************************************************************\n")

    if DEBUG_MAIN:
        print "--------------------------------------"
        print "searching " + str(key)
        print class_search_slices[key]
    for start, end in class_search_slices[key]:
        if DEBUG_MAIN:
            print "\t\tstart is " + str(start) + "\tend is " + str(end)
        for line in lines[start : end]:
            if '(' in line:
                words = str.split(line)
                constructor = words[0]
                con_paren_index = constructor.find("(")
                if con_paren_index != -1:
                    # get the constructor name
                    constructor = constructor[:con_paren_index]
                    # get the constructor args
                    open_paren_index = line.find("(")
                    close_paren_index = line.find(")")
                    con_args = line[open_paren_index+1 : close_paren_index]
                    if DEBUG_MAIN:
                        print "the constructor is: " + constructor
                        print "the args are: " + con_args
                    #write the constructor stub
                    out.write(key+"::"+constructor+"("+con_args+")\n{")
                    out.write("\n\t/* TODO: Implement "+key+" constructor */\n")
                    out.write("}\n\n")
                else:
                    return_type = words[0]
                    method = words[1]
                    paren_index = method.find("(")
                    method = method[:paren_index]
                    # get the method args
                    open_paren_index = line.find("(")
                    close_paren_index = line.find(")")
                    meth_args = line[open_paren_index+1 : close_paren_index]
                    # check for a const; at the end of the declaration
                    if words[-1] == "const;":
                        modifier = "const"
                    else:
                        modifier = ""
                        
                    if DEBUG_MAIN:
                        print(return_type, method, meth_args)
    
                    #write the method stub
                    out.write(return_type+" "+key+"::"+method+"("+meth_args+") "+modifier+"\n")
                    out.write("{\n")
                    out.write("\t/* TODO: Implement "+method+" method */\n")
                    out.write("}\n\n")

print ("SUCCESS: Stub file written to "+out_file)
    
    
if DEBUG_MAIN: 
#    print(classes)
#    print(class_inline_slices)
#    print(class_search_slices)

    val = "end"         
#!/usr/bin/env python
# encoding: utf-8
''' 
Extends the reST title markup to the length given by the heading text. 

Text selection needs to wrap the construct completely, e.g. select all 
lines in the heading construct that need adjusting. Is smart enough to 
preserve proper indentation. 

Caveats

    - can only deal with one heading at a time.
    - doesn't handle continuation of mixed underline characters properly.
  
'''

import os, sys, re

BARS_PATTERN = re.compile(r'((?:=|\-|~|`|#|"|\^|\+|\*)+)', flags=re.UNICODE)
TEXT_PATTERN = re.compile(r'(?!\s)([^=\-~`#"\^\+\*\n\r]+)', flags=re.UNICODE)

DEBUG = 0 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)
PROFILE = 0 or ('ProfileLevel' in os.environ and os.environ['ProfileLevel'] > 0)

ENV = os.environ

TAB_SIZE = 4
try:
    TAB_SIZE = int(ENV['TM_TAB_SIZE'])
except:
    pass

if DEBUG or TESTRUN:
    ENV['TM_TAB_SIZE'] = "3"
    #ENV['TM_SELECTED_FILE'] = "/Users/andre/Documents/Eclipse/Workspaces/Python/mp3tagger/docs/index.rst"
    #ENV['TM_LINE_NUMBER'] = "2"

def is_underline(string):
    return (re.search(BARS_PATTERN, string) is not None)

def is_empty(string):
    return len(string.strip()) == 0

def fix_indentation(lines_dict, startpos):
    result = []
    for k in sorted(lines_dict.iterkeys()):
        line = lines_dict[k]
        if is_underline(line):
            result.append((' ' * startpos) + line.strip())
        else:
            result.append(line)
    return os.linesep.join(result)
    
def extend_title(text):
    text = text.expandtabs()
    lines = text.splitlines()
    # escape snippet characters
    lines = [re.sub(r'([$`\\])', r'\\\1', line) for line in lines]
    last_char = text[-1]
    if last_char not in ['\r', '\n']:
        last_char = ''
    text_part = None
    text_startpos = -1
    lines_dict = {}
    for idx, line in enumerate(lines):
        if is_empty(line):
            lines_dict[idx] = line
            continue
        match = re.search(TEXT_PATTERN, line)
        if match:
            text_part = match.group(1)
            text_startpos = match.regs[-1][0]
            lines_dict[idx] = line
            break
    if text_part is None:
        return text
    text_len = len(text_part)
    for idx, line in enumerate(lines):
        if is_empty(line):
            lines_dict[idx] = line
            continue
        match = re.search(BARS_PATTERN, line)
        if match:
            underline_part = match.group(1)
            extended_underlines = underline_part[0] * text_len
            lines_dict[idx] = re.sub(underline_part, 
                                     extended_underlines, line, flags=re.UNICODE)
    result = fix_indentation(lines_dict, text_startpos)
    result += last_char
    return result

# def get_text_from_file(file=ENV['TM_SELECTED_FILE']):
#     if not os.path.exists(file):
#         return None
#     text = io.open(file, 'rt')
#     return text

# def expand_selection(lines, index=int(ENV['TM_LINE_NUMBER'])):
#     line_index = index - 1
#     line_selected = lines[line_index]
#     selected_text = line_selected
#     if len(selected_text) < 1:
#         return None
#     line_before = None
#     line_after = None
#     line_indexes = [index]
#     try:
#         line_before = lines[line_index - 1]
#         line_after = lines[line_index + 1]
#     except IndexError:
#         pass
#     if line_before is not None:
#         selected_text = line_before + selected_text
#         line_indexes.append(index - 1)
#     if line_after is not None:
#         selected_text = selected_text + line_after
#         line_indexes.append(index + 1)
#     return (selected_text, line_indexes)

if __name__ == '__main__':
    
    if TESTRUN:
        def test_extend_title(input_text, expected):  # IGNORE:W0621
            output = extend_title(input_text)
            print('%s' % output)
            assert(output == expected)
                    
        sampletext = """
        ===
        module
        ===
        """
        expected = """
        ======
        module
        ======
        """
        test_extend_title(sampletext, expected)

        sampletext = """
==============
module docs
=======
"""
        expected = """
===========
module docs
===========
"""
        test_extend_title(sampletext, expected)
    else:
        input_text = sys.stdin.read()
        
        # Commented out because originally I wanted to support
        # extending titles where the user didn't have any text
        # selected just by inferring the line number and the 
        # contents of the lines before and after. However this
        # meant also replacing the full document each and every
        # time (to support both ways: selection or no selection).
        # 
        # This seams too drastic for something as simple as this 
        # so I let the user make the decision to specifically say 
        # in which lines the title should be extended.
        #
        #doc = get_text_from_file()
        #if doc is None:
        #    sys.exit(1)
        #if len(input_text) < 1:
        #    lines = doc.readlines()
        #    selected_text, line_numbers_selected_text = expand_selection(lines)
        #    extended_title = extend_title(selected_text)
        #else:
        #    extended_title = extend_title(input_text)
        
        try:
            extended_title = extend_title(input_text)
        except Exception as e:
            print(e)
            sys.exit(1)
        sys.stdout.write(extended_title)
        sys.exit(0)

    
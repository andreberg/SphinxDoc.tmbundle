#!/bin/bash
# -*- coding: utf-8 -*-
# 
#  sphinxdoc.sh
#  SphinxDoc.tmbundle
#  
#  Created by André Berg on 2010-12-14.
#  Copyright 2010 Berg Media. All rights reserved.
# 
#  Common functions shared by the whole bundle.
#  These are typically functions used at runtime
#  of bundle commands defined via the bundle editor
#  interface.
#
#  You can find more functions in init.sh which
#  are used in earlier points in time. 
#

. "$TM_BUNDLE_SUPPORT/init.sh"

function present_errors() {
    # $1: tool name => sphinx-build or docutils
    echo "<p>"
    "$ruby" "$TM_BUNDLE_SUPPORT/error_parser.rb" "$errors_tmp_file" "$current_file" "${1:-sphinx-build}"
    echo "</p>"
}

function prepend_error_label() {
    # $2: if "true" or 1, pre-ify text
    if [[ ${#} = 2 ]]; then
        if [[ "$2" = "true" || "$2" = 1 ]]; then
            # pre-ify text
            txt=`echo "${1}" | perl -pe '$| = 1; s/&/&amp;/g; s/</&lt;/g; s/>/&gt;/g; s/$\\n/<br>/'`
        else
            txt=`echo "${1}"`
        fi
    else
        txt=`echo "${1}"`
    fi
    txt=`entitify_keyboard_shortcuts "$txt"`
    echo -n '<pre style="word-wrap: break-word;">'
    echo -n "<span style=\"color: ${TM_SPHINX_DOC_COLOR_ERRORS:-$color_errors};\">Error:</span>&nbsp;"
    echo "$txt"
	echo '</pre>'
}

function preview_selected_text() {
    
    . "$TM_SUPPORT_PATH/lib/webpreview.sh"
    
    require_cmd "$python" "${err_python_not_found_msg:-see help (alt+F1)}"

    cd "$TM_BUNDLE_SUPPORT"

    pythonscript=`cat <<EOF
import sys
try:
    import rested_util
    from sphinxdoc import SphinxDocUtils as util
except Exception, e:
    msg = """$err_python_modules_not_found"""
    sys.stderr.write(msg+"\n")
    sys.exit(1)

import os

sel = util.current_text(True)
output, errors = rested_util.docutils_rest_to_html(sel)

sys.stdout.write(output+"\n")
if len(errors) > 0:
    sys.stderr.write(repr(errors))
EOF
`
    if [[ "${1}" = "docutils" ]]; then
        
        output=`"$python" -c "$pythonscript" 2> /dev/null`

        if [[ $? = 0 ]]; then
            html_header "Preview Selected Text" "Sphinx Doc"
            echo -e "$output"
            html_footer
            exit_show_html
        else
            exit_show_tool_tip "Error: try again with sphinx"
        fi
    else

        output=`"$python" -c "$pythonscript" 2> /dev/null`
        pythonscript=`echo "$pythonscript" | sed -E 's/docutils_rest_to_html/sphinx_rest_to_html/'`

        "$python" -c "$pythonscript" 1> "$output_tmp_file_html"  2> "$errors_tmp_file"

        if [[ $? = 0 ]]; then
            echo "<meta http-equiv=\"refresh\" content=\"0; tm-file://$output_tmp_file_html\">"
            exit_show_html
        else
            html_header "Preview Selected Text" "Sphinx Doc"
            errors=`cat "$errors_tmp_file"`
            prepend_error_label "$errors"
            html_footer
            exit_show_html
        fi
    fi
}
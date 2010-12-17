#!/bin/bash

. "$TM_BUNDLE_SUPPORT/init.sh"
. "$TM_BUNDLE_SUPPORT/sphinx_build.sh"
. "$TM_SUPPORT_PATH/lib/webpreview.sh"

filepath="$TM_FILEPATH"

dirname="${filepath%/*}"   # => /path1/path2
basename="${filepath##*/}" # => filename.txt
filename="${basename%%.*}" # => filename
fileext=".${basename##*.}" # => .txt

if [[ "$fileext" = ".py" ]]; then
	# try pycheckmate
	"$python" "$TM_BUNDLE_SUPPORT/pycheckmate.py" "$filepath"
	exit_show_html
else
    
	cmd='run_sphinx_build mute_stdout_redirect_stderr'
	output=`$cmd`

	if [[ $? = 0 && ! -s "$errors_tmp_file" ]]; then
	    # if we get no build errors for the whole project we can exit with OK tool tip right away
		exit_show_tool_tip "Syntax OK"
	else
	    # otherwise we need to filter for the current file
	    # best would be to ask sphinx-build to check one file only - need to look into that
		output=`"$ruby" "$TM_BUNDLE_SUPPORT/error_parser.rb" "$errors_tmp_file" "$filepath"`
		#echo -e "$output"
		if [[ "$output" = "" ]]; then
		    exit_show_tool_tip "Syntax OK"
		else
		    html_header "Validate Syntax" "Sphinx Doc"
		    echo "$output"
		    html_footer
    		exit_show_html
		fi
	fi	
fi

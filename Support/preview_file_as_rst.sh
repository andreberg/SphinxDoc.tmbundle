. "$TM_BUNDLE_SUPPORT/init.sh"
. "$TM_BUNDLE_SUPPORT/sphinxdoc.sh"
. "$TM_SUPPORT_PATH/lib/webpreview.sh"

if [[ -s "$TM_SPHINX_DOCUTILS_DIR/rst2html.py" ]]; then
	TRST="$TM_SPHINX_DOCUTILS_DIR/rst2html.py"
else
	TRST=${TM_RST2HTML:=rst2html.py}
	require_cmd "$TRST" "You can either set the <tt>TM_SPHINX_DOCUTILS_DIR</tt> variable to the <tt>bin</tt> path of your docutils (docutils.sourceforge.net) installation (e.g. <tt>/Library/Frameworks/Python.framework/Versions/Current/bin</tt> or set the <tt>PATH</tt> variable to include the path of the docutils converters. Alternatively, for fine-grained control, you can set the <tt>TM_RST2HTML</tt> variable to the full path of the <tt>rst2html.py</tt> file."
fi

html_header "Preview as RST" "Sphinx Doc"

if [[ -f "$TM_DIRECTORY/default.css" ]]
	then stylesheet="$TM_DIRECTORY/default.css"
elif [[ -f "$TM_PROJECT_DIRECTORY/default.css" ]]
	then stylesheet="$TM_PROJECT_DIRECTORY/default.css"
else
	css=`mktemp -t /tmp`
	echo 'body {	
		background-color: #eee;
	}
	.document {
		font-family: Georgia, serif;
		font-size: 13px;
		border: 1px #888 solid;
		padding: 0 1em;
	}' > $css
	stylesheet=$css
	tmpCreated="yes"
fi

if [[ -n $stylesheet ]]
    then flags="--embed-stylesheet --stylesheet=$stylesheet"
    else flags=""
fi

old_pwd="$PWD"
cd "$current_dir"

"$TRST" --warnings="$errors_tmp_file" --halt=5 "$current_file" 1> /dev/null

output=`"$TRST" --source-link --halt=5 --quiet $flags "$current_file"`

cd "$old_pwd"

echo -e "$output"

if [[ -s "$errors_tmp_file" ]]; then
	present_errors "docutils"
fi

if [[ -n $css ]]
	then rm $css
fi

html_footer
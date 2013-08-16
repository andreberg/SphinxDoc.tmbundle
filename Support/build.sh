. "$TM_SUPPORT_PATH/lib/webpreview.sh"
. "$TM_BUNDLE_SUPPORT/init.sh"
. "$TM_BUNDLE_SUPPORT/sphinx_build.sh"

DEBUG=0

html_header "Build" "Sphinx Doc"

if [[ "$DEBUG" = 1 ]]; then    
    basepath="/Users/andre/Documents/Aptana Studio 2.0/Workspaces/Python/File Sequence Checker/doc/sphinx"
    target=`python "$HOME/Library/Application Support/TextMate/Bundles/SphinxDoc.tmbundle/Support/get_target.py" "$basepath" "$fullname"`
    echo "basepath=$basepath<br/>"
    echo "target=$target<br/>"
else
    # get target file so we can check if_ it was built properly later
    target=`"$python" "${TM_BUNDLE_SUPPORT}/get_target.py" "$current_dir" "$current_file"`
    #echo "basepath=$basepath<br/>"
    #echo "current_file=$current_file<br/>"
    #echo "target=$target<br/>"
fi

if [[ $? = 3 ]]; then
    . "$TM_BUNDLE_SUPPORT/sphinxdoc.sh"
    errmsg=`prepend_error_label "Your Python installation seems to 'think' that your Sphinx config file (<code>conf.py</code>) contains <code>SyntaxErrors</code>. If you have multiple Python installations active, make sure the correct one is utilized.<br><br>See bundle help (alt+F1) for more info."`
    echo -e `entitify_keyboard_shortcuts "$errmsg"` 
else
    run_sphinx_build "redirect_stderr"
fi

html_footer
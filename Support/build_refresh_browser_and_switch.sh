. "$TM_SUPPORT_PATH/lib/webpreview.sh"
. "$TM_BUNDLE_SUPPORT/init.sh"
. "$TM_BUNDLE_SUPPORT/sphinx_build.sh"
. "$TM_BUNDLE_SUPPORT/browser_refresh.sh"

html_header "Make HTML, Refresh Browser and Switch" "Sphinx Doc"

sphinx_build "redirect_stderr"

html_footer

if [[ $? = 0 ]]; then
    browser_refresh "switch"
else
    echo "Build failed! See '$errors_tmp_file' for details."
fi
. "$TM_SUPPORT_PATH/lib/webpreview.sh"
. "$TM_BUNDLE_SUPPORT/init.sh"
. "$TM_BUNDLE_SUPPORT/sphinx_build.sh"
. "$TM_BUNDLE_SUPPORT/browser_refresh.sh"

html_header "Build and Refresh Browser" "Sphinx Doc"

run_sphinx_build "redirect_stderr"

if [[ $? = 0 ]]; then
    browser_refresh
else
    echo "Build failed! See '$errors_tmp_file' for details."
fi

html_footer

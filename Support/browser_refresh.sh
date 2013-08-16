function browser_refresh() {
    ###	Active Browser Refresh - OmniWeb, Safari, Firefox & IE
    ### v1.1. 2010-12-04
    ### changed slightly by Andre Berg to support the TM_PREFERRED_BROWSER custom variable
        
    if [[ ${1} = "activate" || ${1} = "switch" ]]; then
        activate="activate"
    else
        activate=""
    fi
    
    which_browser="${preferred_browser}"
    
    #echo "which_browser = ${which_browser}"

    if [[ -n $which_browser ]]; then
    	if [[ $which_browser = "IE" ]]; then
    		# Check if Internet Explorer is running, if so refresh
    		ps -xc|grep -sq "Internet Explorer" && osascript -e 'tell app "Internet Explorer"' -e "$activate" -e 'OpenURL "JavaScript:window.location.reload();" toWindow -1' -e 'end tell' > /dev/null 2>&1
    	elif [[ $which_browser = "OmniWeb" ]]; then
    		# Check if OmniWeb is running, if so refresh
    		ps -xc|grep -sq OmniWeb && osascript -e 'tell app "OmniWeb"' -e "$activate" -e 'reload first browser' -e 'end tell' > /dev/null 2>&1
    	elif [[ $which_browser = "Firefox" ]]; then
    		# Check if Firefox is running, if so refresh
            ps -xc|grep -sqi firefox && osascript > /dev/null 2>&1 <<-'APPLESCRIPT'
            tell app "Firefox" to activate
            tell app "System Events"
                if UI elements enabled then
                    keystroke "r" using command down
                    -- Fails if System Preferences > Universal access > "Enable access for assistive devices" is not on 
                else
                    -- Comment out until Firefox regains Applescript support
                    -- tell app "Firefox" to Get URL "JavaScript:window.location.reload();" inside window 1
                    -- Fails if Firefox is set to open URLs from external apps in new tabs.
                end if
            end tell
APPLESCRIPT
    	elif [[ $which_browser = "Safari" ]]; then
    		# Check if Safari is running, if so refresh
    		ps -xc|grep -sq Safari && osascript -e 'tell app "Safari"' -e "$activate" -e 'do JavaScript "window.location.reload();" in first document' -e 'end tell' > /dev/null 2>&1
    	elif [[ $which_browser = "Chrome" ]]; then
    		# Check if Chrome is running, if so refresh 
            ps -xc|grep -sq Chrome && osascript -e 'tell app "Google Chrome"' -e "$activate" -e 'tell app "System Events" to keystroke "r" using {command down}' -e 'end tell' > /dev/null 2>&1
        fi
        exit 0
    fi

    # if no preferred browser reload all running...

    # Check if Internet Explorer is running, if so refresh
    ps -xc|grep -sq "Internet Explorer" && osascript -e 'tell app "Internet Explorer"' -e "$activate" -e 'OpenURL "JavaScript:window.location.reload();" toWindow -1' -e 'end tell' > /dev/null 2>&1

    # Check if OmniWeb is running, if so refresh
    ps -xc|grep -sq OmniWeb && osascript -e 'tell app "OmniWeb"' -e "$activate" -e 'reload first browser' -e 'end tell' > /dev/null 2>&1

    # Check if Firefox is running, if so refresh
    ps -xc|grep -sqi firefox && osascript > /dev/null 2>&1 <<-'APPLESCRIPT'
    tell app "Firefox" to activate
    tell app "System Events"
        if UI elements enabled then
            keystroke "r" using command down
            -- Fails if System Preferences > Universal access > "Enable access for assistive devices" is not on 
        else
            -- Comment out until Firefox regains Applescript support
            -- tell app "Firefox" to Get URL "JavaScript:window.location.reload();" inside window 1
            -- Fails if Firefox is set to open URLs from external apps in new tabs.
        end if
    end tell
APPLESCRIPT

    # Check if Safari is running, if so refresh
    ps -xc|grep -sq Safari && osascript -e 'tell app "Safari"' -e "$activate" -e 'do JavaScript "window.location.reload();" in first document' -e 'end tell' > /dev/null 2>&1

    # Check if Camino is running, if so refresh 
    ps -xc|grep -sq Camino && osascript -e 'tell app "Camino"' -e "$activate" -e 'tell app "System Events" to keystroke "r" using {command down}' -e 'end tell' > /dev/null 2>&1

    # Check if Chrome is running, if so refresh 
    ps -xc|grep -sq Chrome && osascript -e 'tell app "Google Chrome"' -e "$activate" -e 'tell app "System Events" to keystroke "r" using {command down}' -e 'end tell' > /dev/null 2>&1
    
}

#browser_refresh "activate"

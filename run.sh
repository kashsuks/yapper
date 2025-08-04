#!/bin/bash

npm install
node index.js &

osascript <<EOF
tell application "Terminal"
    activate
    tell application "System Events" to keystroke "t" using command down
    delay 1
    do script "cd \"$(pwd)\"; source venv/bin/activate; pip3 install -r requirements.txt; python3 events/osuSlack.py" in selected tab of the front window
end tell
EOF
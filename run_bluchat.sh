#!/bin/bash

# TODO: add .venv creation if it does not exist

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Create a detached session called 'bluchat-session' if it doesn't exist
if tmux has-session -t bluchat-session 2>/dev/null; then
    echo "tmux session 'bluchat-session' already running"
else
    # Run the venv's python directly (avoids activate setting an absolute VIRTUAL_ENV path)
    tmux new-session -d -s bluchat-session "bash -lc '"$SCRIPT_DIR"/.venv/bin/python main.py'"
    # Verify session started and report failure if it exited immediately
    sleep 1
    if tmux has-session -t bluchat-session 2>/dev/null; then
      echo "Started bluchat in tmux session 'bluchat-session'"
    else
      echo "Failed to start bluchat in tmux; check logs or run the command manually:" >&2
      echo ""$SCRIPT_DIR"/.venv/bin/python main.py" >&2
      exit 1
    fi
fi

# TODO: add methods to control power via pinctrl
# pinctrl set 6 op dh && sleep 0.5 && pinctrl set 6 dl 

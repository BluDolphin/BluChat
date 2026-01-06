#!/bin/bash

# TODO: add .venv creation if it does not exist

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Activate the virtual environment
source .venv/bin/activate

# Run the main application
python main.py

# TODO: add methods to control power via pinctrl
# pinctrl set 6 op dh && sleep 0.5 && pinctrl set 6 dl 
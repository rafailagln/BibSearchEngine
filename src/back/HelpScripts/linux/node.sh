#!/bin/bash

# This script is used to set the Python path and execute a node in the BibSearchEngine distributed system.
# Each node should have a unique node_id, config.json, and config.ini.
#
# Usage:
#   chmod +x node.sh
#   ./node.sh /path/to/BibSearchEngine/src/back /path/to/config.json /path/to/config.ini 1
#

# Check if the correct number of arguments is provided
if [ $# -ne 4 ]; then
    echo "Error: Incorrect number of arguments provided."
    echo "Usage: zsh node.sh '/path/to/BibSearchEngine/src/back' /path/to/config.json /path/to/config.ini <node_id>"
    exit 1
fi

PYTHON_SRC_PATH="$1"
JSON_CONFIG_PATH="$2"
INI_CONFIG_PATH="$3"
NODE_ID="$4"

# Validate paths
if [ ! -d "$PYTHON_SRC_PATH" ]; then
    echo "Error: The provided Python source directory does not exist: $PYTHON_SRC_PATH"
    exit 1
fi

if [ ! -f "$JSON_CONFIG_PATH" ]; then
    echo "Error: The provided JSON config file does not exist: $JSON_CONFIG_PATH"
    exit 1
fi

if [ ! -f "$INI_CONFIG_PATH" ]; then
    echo "Error: The provided INI config file does not exist: $INI_CONFIG_PATH"
    exit 1
fi

# Validate node id
if ! [[ "$NODE_ID" =~ ^[0-9]+$ ]] ; then
   echo "Error: Node ID must be a number: $NODE_ID"
   exit 1
fi

# Set python path
export PYTHONPATH="${PYTHONPATH}:${PYTHON_SRC_PATH}"
cd "${PYTHON_SRC_PATH}/distributed" || exit

# Execute the node
python3 node.py --json_config "$JSON_CONFIG_PATH" --ini_config "$INI_CONFIG_PATH" --node_id "$NODE_ID"

echo "Node execution complete."

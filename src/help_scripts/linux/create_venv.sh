#!/bin/bash

# Define the path to the virtual environment
ENV_PATH=$1

# Check if the path is not empty
if [ -z "$ENV_PATH" ]; then
    echo "Please provide a path for the virtual environment."
    exit 1
fi

apt install -y python3.10-venv

# Create the virtual environment
python3 -m venv $ENV_PATH

# Activate the virtual environment
source $ENV_PATH/bin/activate

# Install the dependencies
pip install uvicorn fastapi pymongo nltk

echo "Setup is complete and the virtual environment is now active!"

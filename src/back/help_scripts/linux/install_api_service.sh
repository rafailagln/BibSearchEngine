#!/bin/bash

# check if the correct number of arguments is provided
if [ $# -ne 2 ]; then
    echo "Error: Incorrect number of arguments provided."
    echo "Usage: ./install_api_service <working_directory> <log_directory>"
    exit 1
fi

WORKING_DIR="$1"
LOG_DIR="$2"

# the path of the service file to be created
SERVICE_PATH="/etc/systemd/system/bib-engine-api.service"

# creating the service file
echo "[Unit]" > $SERVICE_PATH
echo "Description=BibEngine FastAPI Backend" >> $SERVICE_PATH
echo "After=network.target" >> $SERVICE_PATH

echo "" >> $SERVICE_PATH

echo "[Service]" >> $SERVICE_PATH
echo "WorkingDirectory=${WORKING_DIR}" >> $SERVICE_PATH
echo "ExecStart=python3 ${WORKING_DIR}/fast_api.py" >> $SERVICE_PATH
echo "Restart=always" >> $SERVICE_PATH
echo "StandardOutput=file:${LOG_DIR}/log_file.log" >> $SERVICE_PATH
echo "StandardError=file:${LOG_DIR}/error_file.log" >> $SERVICE_PATH

echo "" >> $SERVICE_PATH

echo "[Install]" >> $SERVICE_PATH
echo "WantedBy=multi-user.target" >> $SERVICE_PATH

# notify the user of the successful operation
echo "Service file has been created successfully at ${SERVICE_PATH}."

# make it executable
chmod u+x /etc/systemd/system/bib-engine-api.service
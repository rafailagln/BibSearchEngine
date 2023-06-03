#!/bin/bash

# check if the correct number of arguments is provided
if [ $# -ne 5 ]; then
    echo "Error: Incorrect number of arguments provided."
    echo "Usage: bash service-creator.sh <working_directory> <project_src_path> <json_config_path> <ini_config_path> <node_id>"
    exit 1
fi

WORKING_DIR="$1"
PROJECT_SRC_PATH="$2"
JSON_CONFIG_PATH="$3"
INI_CONFIG_PATH="$4"
NODE_ID="$5"

# the path of the service file to be created
SERVICE_PATH="/etc/systemd/system/bibnode.service"

# creating the service file
echo "[Unit]" > $SERVICE_PATH
echo "Description=node" >> $SERVICE_PATH
echo "After=network.target" >> $SERVICE_PATH

echo "" >> $SERVICE_PATH

echo "[Service]" >> $SERVICE_PATH
echo "WorkingDirectory=${WORKING_DIR}" >> $SERVICE_PATH
echo "ExecStart=${WORKING_DIR}/node.sh ${PROJECT_SRC_PATH} ${JSON_CONFIG_PATH} ${INI_CONFIG_PATH} ${NODE_ID}" >> $SERVICE_PATH
echo "Restart=always" >> $SERVICE_PATH

echo "" >> $SERVICE_PATH

echo "[Install]" >> $SERVICE_PATH
echo "WantedBy=multi-user.target" >> $SERVICE_PATH

# notify the user of the successful operation
echo "Service file has been created successfully at ${SERVICE_PATH}."
#!/bin/bash

# Download Apache Maven
wget https://mirrors.estointernet.in/apache/maven/maven-3/3.6.3/binaries/apache-maven-3.6.3-bin.tar.gz

# Extract the downloaded archive
tar -xvf apache-maven-3.6.3-bin.tar.gz

# Move the extracted folder to /opt directory (requires sudo)
sudo mv apache-maven-3.6.3 /opt/

# Cleanup - remove the downloaded archive
rm apache-maven-3.6.3-bin.tar.gz


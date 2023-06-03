#!/bin/bash

# Create tomcat user
sudo useradd -m -d /opt/tomcat -U -s /bin/false tomcat

# Update package information
sudo apt update

# Install OpenJDK 19
sudo apt install openjdk-19-jre-headless

# Download and extract Apache Tomcat
cd /tmp
wget https://dlcdn.apache.org/tomcat/tomcat-10/v10.1.9/bin/apache-tomcat-10.1.9.tar.gz
sudo tar xzvf apache-tomcat-10*tar.gz -C /opt/tomcat --strip-components=1

# Set appropriate ownership and permissions
sudo chown -R tomcat:tomcat /opt/tomcat/
sudo chmod -R u+x /opt/tomcat/bin


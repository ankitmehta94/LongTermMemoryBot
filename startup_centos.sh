#!/bin/bash

# Update all packages
sudo yum update -y

# Install required packages
sudo yum install -y git docker postgresql postgresql-devel python-devel

# Start Docker
sudo systemctl start docker

# Clone the repository
git clone https://github.com/ankitmehta94/LongTermMemoryBot.git --branch main --single-branch --depth 1 --recursive --shallow-submodules --quiet

# Enter the cloned directory
cd LongTermMemoryBot

# Start the Docker Compose services
sudo docker-compose up

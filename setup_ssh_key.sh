#!/bin/bash

# Script to setup SSH key on the server
# This script should be run ON THE SERVER (not locally)

echo "🔑 Setting up SSH key for pharmasky-github-deploy..."

# Create .ssh directory if it doesn't exist
mkdir -p ~/.ssh

# Add the public key to authorized_keys
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICiYHpODLkXsNKxolkjyIN6xWhWULWKnvL8cyNaNr+Jp pharmasky-github-deploy" >> ~/.ssh/authorized_keys

# Set proper permissions
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh

echo "✅ SSH key has been added successfully!"
echo "🚀 You can now connect from local machine using:"
echo "ssh -i ~/.ssh/pharmasky-github-deploy root@129.212.140.152"

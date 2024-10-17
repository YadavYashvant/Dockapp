#!/bin/bash
# Script to clean the Android project

# Check if project directory exists
if [ ! -d "/usr/src/app/$1" ]; then
  echo "Project directory not found. Please initialize a project first."
  exit 1
fi

# Navigate to the project directory
cd /usr/src/app/$1

# Clean the project
./gradlew clean

echo "Project cleaned for $1"

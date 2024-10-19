#!/bin/bash

# Check if the project directory exists
if [ ! -d "/usr/src/app/$1" ]; then
  echo "Project directory not found. Please initialize a project first."
  exit 1
fi

# Navigate to the project directory
cd /usr/src/app/$1

# Build the Android app
./gradlew build

echo "Build completed for the project $1"

#!/bin/bash
# Script to initialize a new Android project

# Check if project name is passed as an argument
if [ -z "$1" ]; then
  echo "Usage: ./init-android-project.sh <project-name>"
  exit 1
fi

PROJECT_NAME=$1

# Create the Android project using the command-line tools
android create project --target android-33 --name $PROJECT_NAME --path /usr/src/app/$PROJECT_NAME --activity MainActivity --package com.example.$PROJECT_NAME

echo "Android project '$PROJECT_NAME' initialized at /usr/src/app/$PROJECT_NAME"

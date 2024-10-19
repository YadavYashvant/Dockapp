#!/bin/bash

# Check if project directory exists
if [ ! -d "/usr/src/app/$1" ]; then
  echo "Project directory not found. Please initialize a project first."
  exit 1
fi

# Check if any device is connected
ADB_DEVICES=$(adb devices | grep -w "device")
if [ -z "$ADB_DEVICES" ]; then
  echo "No devices connected. Please connect a device or start an emulator."
  exit 1
fi

# Navigate to the project directory
cd /usr/src/app/$1

# Run the Android app on the connected device
./gradlew installDebug

echo "App installed and running on the connected device"

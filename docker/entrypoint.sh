#!/bin/bash

# Set environment variables
export ANDROID_HOME=/opt/android-sdk
export PATH=$ANDROID_HOME/emulator:$ANDROID_HOME/tools:$ANDROID_HOME/tools/bin:$ANDROID_HOME/platform-tools:$PATH

# Function to accept Android SDK licenses
accept_android_licenses() {
  yes | sdkmanager --licenses
}

# Install Android SDK components (if required)
install_sdk_components() {
  sdkmanager "platform-tools" "build-tools;33.0.0" "platforms;android-33" "emulator" "system-images;android-30;google_apis;x86_64"
}

# Initialize project if necessary
init_android_project() {
  if [ ! -d "/workspace/android-app" ]; then
    echo "No Android project found, initializing a new project."
    /scripts/init-android-project.sh my-android-app
  fi
}

# Check for passed command or start a bash session by default
if [ "$1" == "build" ]; then
  /scripts/build-android-app.sh my-android-app
elif [ "$1" == "run" ]; then
  /scripts/run-android-app.sh my-android-app
elif [ "$1" == "clean" ]; then
  /scripts/clean-project.sh my-android-app
else
  echo "No valid command passed, defaulting to bash session."
  exec "$@"
fi

# Accept licenses and install SDK components during startup
accept_android_licenses
install_sdk_components

# Default command if no argument is passed
exec "$@"


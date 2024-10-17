# Use a base image with JDK 11 and required dependencies
FROM openjdk:11-jdk-slim

# Install required tools
RUN apt-get update && \
    apt-get install -y curl unzip git gradle && \
    apt-get clean

# Install Android SDK
ENV ANDROID_SDK_ROOT /opt/android-sdk
RUN mkdir -p $ANDROID_SDK_ROOT/cmdline-tools && \
    curl -o sdk-tools.zip https://dl.google.com/android/repository/commandlinetools-linux-8092744_latest.zip && \
    unzip sdk-tools.zip -d $ANDROID_SDK_ROOT/cmdline-tools && \
    rm sdk-tools.zip

# Set up PATH
ENV PATH=$PATH:$ANDROID_SDK_ROOT/cmdline-tools/bin:$ANDROID_SDK_ROOT/platform-tools

# Accept licenses
RUN yes | $ANDROID_SDK_ROOT/cmdline-tools/bin/sdkmanager --licenses

# Install required SDK packages (e.g., build tools, platforms)
RUN $ANDROID_SDK_ROOT/cmdline-tools/bin/sdkmanager "platform-tools" "build-tools;33.0.0" "platforms;android-33"

# Set up working directory for your Android project
WORKDIR /usr/src/app

# Install Docker in the container to use Docker commands
RUN apt-get install -y docker.io

# Install Docker Compose
RUN curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

# Copy scripts into the container
COPY scripts/ /usr/local/bin/

# Make scripts executable
RUN chmod +x /usr/local/bin/*.sh

# Expose necessary ports (e.g., for Android devices/emulators)
EXPOSE 5554 5555

# Add an entrypoint to run commands easily
ENTRYPOINT ["/bin/bash"]
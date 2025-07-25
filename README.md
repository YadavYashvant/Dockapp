# DockApp

DockApp is a lightweight GTK-based Android development environment for Linux. It provides essential features for Android development without the heavy resource requirements of Android Studio.

## Features

- [x] Project creation and management
- [x] Code editor with Kotlin LSP support
- [x] GTK interface using libadwaita
- [ ] USB device debugging
- [ ] Build and run capabilities

## Requirements

- Linux operating system
- Python 3.8 or higher
- GTK 4.0
- libadwaita
- Android SDK
- Android Debug Bridge (adb)
- Kotlin Language Server

## Installation

1. Install system dependencies:

```bash
# Arch Linux
sudo pacman -S python-gobject gtk4 libadwaita android-tools
yay -S kotlin-language-server

# Ubuntu/Debian
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adwaita-1.0 adb
```
For Kotlin Language Server Installation in Ubuntu, follow <strong>https://ultahost.com/knowledge-base/install-kotlin-ubuntu/</strong> <br><br>
❗<b> Important Note : The Kotlin language server would be automatically setup on the installation of the dockapp, in case some error occurs, it should be manually downloaded.<b> <br><br>
2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Install Android SDK:

```bash
# Download Android SDK command line tools
wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
unzip commandlinetools-linux-9477386_latest.zip
mkdir -p ~/Android/Sdk/cmdline-tools
mv cmdline-tools ~/Android/Sdk/cmdline-tools/latest

# Add to your shell configuration
echo 'export ANDROID_HOME=$HOME/Android/Sdk' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin' >> ~/.bashrc
source ~/.bashrc

# Install required SDK components
sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.0"
```

## Usage

1. Start the application:

```bash
python src/main.py
```

2. Create a new project:
   - Click "New Project" in the sidebar
   - Enter project name and package name
   - Click "Create"

3. Connect a device:
   - Connect your Android device via USB
   - Enable USB debugging in developer options
   - The device should appear in the devices list

4. Build and run:
   - Open a Kotlin file in the editor
   - Click "Build" to compile the project
   - Click "Run" to install and launch on the connected device

## Project Structure

```
dockapp/
├── src/
│   ├── main.py          # Main application window
│   ├── editor.py        # Code editor component
│   ├── project_manager.py # Project management
│   └── device_manager.py # Device management
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

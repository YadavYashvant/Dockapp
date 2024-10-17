# **Dockapp: Android CLI Dockerized Environment**

This project provides a lightweight, fully Dockerized environment for Android app development without the need for Android Studio. Using this Docker container, you can easily build, test, and run Android apps from the command line, with pre-configured scripts to streamline the process. It also includes Docker Compose support and optional Kubernetes deployment for flexible management.

## **Project Structure**

```plaintext
android-docker-cli/
├── android-app/             # Your Android app source code (optional or clone it later)
│   ├── app/
│   │   ├── src/
│   │   │   ├── main/
│   │   │   │   ├── AndroidManifest.xml
│   │   │   │   ├── java/
│   │   │   │   │   └── com/example/app/MainActivity.java or MainActivity.kt
│   │   │   │   └── res/   # Resources like layouts, images, etc.
│   │   ├── build.gradle    # Gradle build script for the app module
│   └── ...
├── docker/
│   ├── Dockerfile           # Dockerfile for the Android CLI environment
│   └── entrypoint.sh        # Optional entrypoint script for container initialization
├── docker-compose.yml       # Docker Compose file for container management
├── android-deployment.yaml  # Kubernetes deployment file (optional)
├── README.md                # Project documentation and setup instructions
├── scripts/
│   ├── init-android-project.sh  # Shell script to initialize an Android project
│   ├── build-android-app.sh     # Shell script to build the Android app
│   ├── run-android-app.sh       # Shell script to run the Android app on a device/emulator
│   └── clean-project.sh         # Shell script to clean the Android project
```

---

## **Setup**

### **1. Clone the Repository**

First, clone the project repository:

```bash
git clone https://github.com/YadavYashvant/Dockapp.git
cd Dockapp
```

### **2. Build the Docker Image**

Use Docker Compose to build the Docker image defined in the `Dockerfile`:

```bash
docker-compose build
```

### **3. Run the Container**

After building the image, run the container using Docker Compose:

```bash
docker-compose up
```

### **4. Access the Container**

To access the container's shell, use the following command:

```bash
docker exec -it android-cli-container /bin/bash
```

---

## **Using the Android CLI Development Environment**

You can either clone an existing Android project into the `android-app/` directory or create a new Android project using the provided scripts.

### **1. Initialize a New Android Project**

To create a new Android project using the CLI, run the following script:

```bash
./scripts/init-android-project.sh <project-name>
```

This will create a new Android project in the `/usr/src/app/<project-name>` directory inside the container.

### **2. Build the Android App**

To build the Android app, run:

```bash
./scripts/build-android-app.sh <project-name>
```

This will compile the app and generate the APK file. The APK will be located in the `build/outputs/apk/` directory.

```bash
APK built at: /usr/src/app/<project-name>/build/outputs/apk/debug/app-debug.apk
```

### **3. Run the App on a Device/Emulator**

To run the app on a connected device or emulator:

```bash
./scripts/run-android-app.sh <project-name>
```

Make sure a device or emulator is connected before running the script.

### **4. Clean the Project**

To clean the project (i.e., remove build files), run:

```bash
./scripts/clean-project.sh <project-name>
```

---

## **Optional: Running an Android Emulator**

You can run an Android emulator inside the container by following these steps:

1. Create an Android Virtual Device (AVD):

    ```bash
    avdmanager create avd -n test -k "system-images;android-30;google_apis;x86_64"
    ```

2. Start the emulator:

    ```bash
    emulator -avd test
    ```

---

## **Optional: Kubernetes Deployment**

You can deploy the container using Kubernetes for scalable and managed deployment. The deployment configuration is provided in `android-deployment.yaml`.

To deploy the container:

```bash
kubectl apply -f android-deployment.yaml
```

---

## **Cleaning Up**

To stop and remove the Docker container after use, run:

```bash
docker-compose down
```

---

## **Troubleshooting**

- **Permissions Issues**: If you encounter permission issues, ensure Docker has appropriate access rights to your filesystem (especially on Linux).
- **SDK Paths**: Make sure the Android SDK paths are correctly configured in the Dockerfile and the SDK tools are properly installed.
- **System Resources**: Running an emulator inside the container may require significant system resources (CPU, RAM).

---

## **License**

This project is licensed under the MIT License.

---

This README now reflects the complete setup, usage instructions, and all relevant scripts for building, running, and testing Android apps in a Dockerized CLI environment.

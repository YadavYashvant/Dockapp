import subprocess
import os
from pathlib import Path
import json
import shutil
import time

class ProjectManager:
    def __init__(self):
        self.projects_dir = Path.home() / ".dockapp" / "projects"
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        
        # Get Android SDK path from environment
        self.android_sdk = os.environ.get('ANDROID_HOME')
        if not self.android_sdk:
            self.android_sdk = str(Path.home() / "Android" / "Sdk")
            
        self.sdkmanager = str(Path(self.android_sdk) / "cmdline-tools" / "latest" / "bin" / "sdkmanager")
        self.avdmanager = str(Path(self.android_sdk) / "cmdline-tools" / "latest" / "bin" / "avdmanager")
        
    def create_project(self, name, package_name, target_sdk="33"):
        """Create a new Android project."""
        project_dir = self.projects_dir / name
        
        if project_dir.exists():
            raise ValueError(f"Project {name} already exists")
            
        try:
            # Create project using Gradle
            project_dir.mkdir(parents=True)
            
            # Create basic project structure
            app_dir = project_dir / "app"
            app_dir.mkdir()
            
            # Create build.gradle files
            self._create_root_build_gradle(project_dir)
            self._create_app_build_gradle(app_dir, package_name, target_sdk)
            
            # Create settings.gradle
            self._create_settings_gradle(project_dir, name)
            
            # Create basic source structure
            src_dir = app_dir / "src" / "main"
            src_dir.mkdir(parents=True)
            
            # Create AndroidManifest.xml
            self._create_android_manifest(src_dir, package_name)
            
            # Create basic Kotlin source
            kotlin_dir = src_dir / "kotlin" / package_name.replace('.', '/')
            kotlin_dir.mkdir(parents=True)
            self._create_main_activity(kotlin_dir, package_name)
            
            # Create project metadata
            metadata = {
                'name': name,
                'package': package_name,
                'target_sdk': target_sdk,
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(project_dir)))
            }
            
            with open(project_dir / '.dockapp.json', 'w') as f:
                json.dump(metadata, f, indent=2)
                
            return project_dir
            
        except Exception as e:
            if project_dir.exists():
                shutil.rmtree(project_dir)
            raise RuntimeError(f"Failed to create project: {e}")
            
    def _create_root_build_gradle(self, project_dir):
        content = """buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:7.4.2'
        classpath 'org.jetbrains.kotlin:kotlin-gradle-plugin:1.8.0'
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

task clean(type: Delete) {
    delete rootProject.buildDir
}
"""
        with open(project_dir / "build.gradle", 'w') as f:
            f.write(content)
            
    def _create_app_build_gradle(self, app_dir, package_name, target_sdk):
        content = f"""plugins {{
    id 'com.android.application'
    id 'kotlin-android'
}}

android {{
    compileSdk {target_sdk}

    defaultConfig {{
        applicationId "{package_name}"
        minSdk 21
        targetSdk {target_sdk}
        versionCode 1
        versionName "1.0"
    }}

    buildTypes {{
        release {{
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }}
    }}
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }}
    kotlinOptions {{
        jvmTarget = '1.8'
    }}
}}

dependencies {{
    implementation 'androidx.core:core-ktx:1.10.0'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.9.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
}}
"""
        with open(app_dir / "build.gradle", 'w') as f:
            f.write(content)
            
    def _create_settings_gradle(self, project_dir, name):
        content = f"""rootProject.name = "{name}"
include ':app'
"""
        with open(project_dir / "settings.gradle", 'w') as f:
            f.write(content)
            
    def _create_android_manifest(self, src_dir, package_name):
        content = f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{package_name}">

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.AppCompat.Light.DarkActionBar">
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""
        with open(src_dir / "AndroidManifest.xml", 'w') as f:
            f.write(content)
            
    def _create_main_activity(self, kotlin_dir, package_name):
        content = f"""package {package_name}

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }}
}}
"""
        with open(kotlin_dir / "MainActivity.kt", 'w') as f:
            f.write(content)
            
        # Create basic layout
        layout_dir = kotlin_dir.parent.parent / "res" / "layout"
        layout_dir.mkdir(parents=True)
        
        layout_content = """<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello World!"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toRightOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
"""
        with open(layout_dir / "activity_main.xml", 'w') as f:
            f.write(layout_content)
            
    def build_project(self, project_name):
        """Build an Android project."""
        project_dir = self.projects_dir / project_name
        
        if not project_dir.exists():
            raise ValueError(f"Project {project_name} does not exist")
            
        try:
            subprocess.run(['./gradlew', 'build'], cwd=project_dir, check=True)
            return True
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Build failed: {e}")
            
    def run_project(self, project_name, device_id=None):
        """Run an Android project on a device."""
        project_dir = self.projects_dir / project_name
        
        if not project_dir.exists():
            raise ValueError(f"Project {project_name} does not exist")
            
        try:
            # Build the project first
            self.build_project(project_name)
            
            # Install and run on device
            if device_id:
                subprocess.run(['adb', '-s', device_id, 'install', '-r', str(project_dir / 'app/build/outputs/apk/debug/app-debug.apk')], check=True)
                package_name = self.get_package_name(project_name)
                subprocess.run(['adb', '-s', device_id, 'shell', 'monkey', '-p', package_name, '1'], check=True)
            else:
                subprocess.run(['adb', 'install', '-r', str(project_dir / 'app/build/outputs/apk/debug/app-debug.apk')], check=True)
                package_name = self.get_package_name(project_name)
                subprocess.run(['adb', 'shell', 'monkey', '-p', package_name, '1'], check=True)
                
            return True
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Run failed: {e}")
            
    def get_package_name(self, project_name):
        """Get the package name of a project."""
        project_dir = self.projects_dir / project_name
        
        if not project_dir.exists():
            raise ValueError(f"Project {project_name} does not exist")
            
        try:
            with open(project_dir / '.dockapp.json', 'r') as f:
                metadata = json.load(f)
                return metadata['package']
        except (FileNotFoundError, json.JSONDecodeError):
            # Fallback to reading from build.gradle
            try:
                with open(project_dir / 'app/build.gradle', 'r') as f:
                    for line in f:
                        if 'applicationId' in line:
                            return line.split('"')[1]
            except FileNotFoundError:
                raise RuntimeError("Could not determine package name")
                
    def list_projects(self):
        """List all projects."""
        projects = []
        
        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                try:
                    with open(project_dir / '.dockapp.json', 'r') as f:
                        metadata = json.load(f)
                        projects.append(metadata)
                except (FileNotFoundError, json.JSONDecodeError):
                    # Skip projects without metadata
                    continue
                    
        return projects
        
    def delete_project(self, project_name):
        """Delete a project."""
        project_dir = self.projects_dir / project_name
        
        if not project_dir.exists():
            raise ValueError(f"Project {project_name} does not exist")
            
        try:
            shutil.rmtree(project_dir)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete project: {e}")
            
    def get_project_files(self, project_name):
        """Get a list of files in the project."""
        project_dir = self.projects_dir / project_name
        
        if not project_dir.exists():
            raise ValueError(f"Project {project_name} does not exist")
            
        files = []
        
        for path in project_dir.rglob('*'):
            if path.is_file() and not path.name.startswith('.'):
                files.append(str(path.relative_to(project_dir)))
                
        return files 
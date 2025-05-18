import subprocess
import json
import threading
import time
from typing import List, Dict, Optional

class DeviceManager:
    def __init__(self):
        self.devices: Dict[str, Dict] = {}
        self.monitor_thread: Optional[threading.Thread] = None
        self.running = False
        
    def start_monitoring(self):
        """Start monitoring for device connections."""
        if self.monitor_thread is not None:
            return
            
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_devices)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop monitoring for device connections."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
            self.monitor_thread = None
            
    def _monitor_devices(self):
        """Monitor for device connections in the background."""
        while self.running:
            self.refresh_devices()
            time.sleep(2)  # Check every 2 seconds
            
    def refresh_devices(self) -> List[Dict]:
        """Refresh the list of connected devices."""
        try:
            result = subprocess.run(['adb', 'devices', '-l'], capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')[1:]  # Skip the first line
            
            new_devices = {}
            
            for line in lines:
                if not line.strip():
                    continue
                    
                parts = line.split()
                if len(parts) < 2:
                    continue
                    
                device_id = parts[0]
                state = parts[1]
                
                if state != 'device':
                    continue
                    
                # Get device properties
                try:
                    props = self._get_device_properties(device_id)
                    new_devices[device_id] = props
                except subprocess.CalledProcessError:
                    continue
                    
            self.devices = new_devices
            return list(new_devices.values())
            
        except subprocess.CalledProcessError as e:
            print(f"Error refreshing devices: {e}")
            return []
            
    def _get_device_properties(self, device_id: str) -> Dict:
        """Get properties of a specific device."""
        try:
            result = subprocess.run(
                ['adb', '-s', device_id, 'shell', 'getprop'],
                capture_output=True,
                text=True,
                check=True
            )
            
            props = {}
            for line in result.stdout.split('\n'):
                if not line.strip():
                    continue
                    
                try:
                    key, value = line.split(':', 1)
                    key = key.strip('[]')
                    value = value.strip('[]')
                    props[key] = value
                except ValueError:
                    continue
                    
            return {
                'id': device_id,
                'model': props.get('ro.product.model', 'Unknown'),
                'manufacturer': props.get('ro.product.manufacturer', 'Unknown'),
                'android_version': props.get('ro.build.version.release', 'Unknown'),
                'sdk_version': props.get('ro.build.version.sdk', 'Unknown'),
                'is_emulator': props.get('ro.kernel.qemu', '0') == '1'
            }
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get device properties: {e}")
            
    def get_devices(self) -> List[Dict]:
        """Get the list of connected devices."""
        return list(self.devices.values())
        
    def get_device(self, device_id: str) -> Optional[Dict]:
        """Get information about a specific device."""
        return self.devices.get(device_id)
        
    def is_device_connected(self, device_id: str) -> bool:
        """Check if a specific device is connected."""
        return device_id in self.devices
        
    def install_app(self, device_id: str, apk_path: str) -> bool:
        """Install an APK on a device."""
        try:
            subprocess.run(
                ['adb', '-s', device_id, 'install', '-r', apk_path],
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to install app: {e}")
            
    def uninstall_app(self, device_id: str, package_name: str) -> bool:
        """Uninstall an app from a device."""
        try:
            subprocess.run(
                ['adb', '-s', device_id, 'uninstall', package_name],
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to uninstall app: {e}")
            
    def launch_app(self, device_id: str, package_name: str) -> bool:
        """Launch an app on a device."""
        try:
            subprocess.run(
                ['adb', '-s', device_id, 'shell', 'monkey', '-p', package_name, '1'],
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to launch app: {e}")
            
    def get_logcat(self, device_id: str, package_name: str) -> str:
        """Get logcat output for a specific app."""
        try:
            result = subprocess.run(
                ['adb', '-s', device_id, 'logcat', '-d', f'*:E'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get logcat: {e}")
            
    def clear_logcat(self, device_id: str) -> bool:
        """Clear the logcat buffer on a device."""
        try:
            subprocess.run(
                ['adb', '-s', device_id, 'logcat', '-c'],
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to clear logcat: {e}") 
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('GtkSource', '5')
from gi.repository import Gtk, GtkSource, GLib, Gio, Gdk, GObject
import json
import subprocess
import threading
import queue
import os
import shutil
from pathlib import Path

class FileTreeView(Gtk.Box):
    __gsignals__ = {
        'file-selected': (GObject.SignalFlags.RUN_LAST, None, (str,))
    }
    
    def __init__(self, project_dir):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.project_dir = Path(project_dir)
        
        # Add header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header.add_css_class("file-tree-header")
        header.set_margin_start(12)
        header.set_margin_end(12)
        header.set_margin_top(12)
        header.set_margin_bottom(6)
        
        title = Gtk.Label(label="Project Files")
        title.add_css_class("file-tree-title")
        header.append(title)
        
        # Add new file/folder buttons
        new_file_btn = Gtk.Button()
        new_file_btn.set_icon_name("document-new-symbolic")
        new_file_btn.set_tooltip_text("New File")
        new_file_btn.connect("clicked", self.show_new_file_dialog)
        header.append(new_file_btn)
        
        new_folder_btn = Gtk.Button()
        new_folder_btn.set_icon_name("folder-new-symbolic")
        new_folder_btn.set_tooltip_text("New Folder")
        new_folder_btn.connect("clicked", self.show_new_folder_dialog)
        header.append(new_folder_btn)
        
        self.append(header)
        
        # Create the tree view
        self.tree_view = Gtk.TreeView()
        self.tree_view.set_headers_visible(False)
        self.tree_view.add_css_class("file-tree-view")
        
        # Enable right-click menu using gesture controller
        gesture = Gtk.GestureClick()
        gesture.set_button(Gdk.BUTTON_SECONDARY)  # Right click
        gesture.connect("pressed", self.on_gesture_pressed)
        self.tree_view.add_controller(gesture)
        
        # Create the model
        self.store = Gtk.TreeStore(str, str)  # display name, full path
        self.tree_view.set_model(self.store)
        
        # Create the column
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Files", renderer, text=0)
        self.tree_view.append_column(column)
        
        # Add scroll window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self.tree_view)
        scrolled.set_margin_start(12)
        scrolled.set_margin_end(12)
        scrolled.set_margin_bottom(12)
        scrolled.set_vexpand(True)
        self.append(scrolled)
        
        # Connect selection changed signal
        self.tree_view.get_selection().connect("changed", self.on_selection_changed)
        
        # Populate the tree
        self.populate_tree()
        
    def show_new_file_dialog(self, button):
        dialog = Gtk.Dialog()
        dialog.set_title("New File")
        dialog.set_transient_for(self.get_root())
        dialog.set_modal(True)
        
        # Add buttons
        dialog.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL,
            "Create", Gtk.ResponseType.OK
        )
        
        content = dialog.get_content_area()
        content.set_margin_start(12)
        content.set_margin_end(12)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        
        # Get selected directory or use project root
        selection = self.tree_view.get_selection()
        model, iter = selection.get_selected()
        if iter:
            parent_path = Path(model.get_value(iter, 1))
            if not parent_path.is_dir():
                parent_path = parent_path.parent
        else:
            parent_path = self.project_dir
            
        # Create form
        form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # File name entry
        name_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        name_label = Gtk.Label(label="File Name:", xalign=0)
        name_entry = Gtk.Entry()
        name_entry.set_hexpand(True)
        name_box.append(name_label)
        name_box.append(name_entry)
        form.append(name_box)
        
        content.append(form)
        
        def on_response(dialog, response):
            if response == Gtk.ResponseType.OK:
                file_name = name_entry.get_text()
                if file_name:
                    file_path = parent_path / file_name
                    try:
                        file_path.touch()
                        self.refresh_tree()
                    except Exception as e:
                        print(f"Error creating file: {e}")
            dialog.destroy()
            
        dialog.connect("response", on_response)
        dialog.present()
        
    def show_new_folder_dialog(self, button):
        dialog = Gtk.Dialog()
        dialog.set_title("New Folder")
        dialog.set_transient_for(self.get_root())
        dialog.set_modal(True)
        
        # Add buttons
        dialog.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL,
            "Create", Gtk.ResponseType.OK
        )
        
        content = dialog.get_content_area()
        content.set_margin_start(12)
        content.set_margin_end(12)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        
        # Get selected directory or use project root
        selection = self.tree_view.get_selection()
        model, iter = selection.get_selected()
        if iter:
            parent_path = Path(model.get_value(iter, 1))
            if not parent_path.is_dir():
                parent_path = parent_path.parent
        else:
            parent_path = self.project_dir
            
        # Create form
        form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Folder name entry
        name_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        name_label = Gtk.Label(label="Folder Name:", xalign=0)
        name_entry = Gtk.Entry()
        name_entry.set_hexpand(True)
        name_box.append(name_label)
        name_box.append(name_entry)
        form.append(name_box)
        
        content.append(form)
        
        def on_response(dialog, response):
            if response == Gtk.ResponseType.OK:
                folder_name = name_entry.get_text()
                if folder_name:
                    folder_path = parent_path / folder_name
                    try:
                        folder_path.mkdir(parents=True)
                        self.refresh_tree()
                    except Exception as e:
                        print(f"Error creating folder: {e}")
            dialog.destroy()
            
        dialog.connect("response", on_response)
        dialog.present()
        
    def on_gesture_pressed(self, gesture, n_press, x, y):
        # Get the path at the clicked position
        path = self.tree_view.get_path_at_pos(int(x), int(y))
        if path:
            # Select the clicked item
            self.tree_view.get_selection().select_path(path[0])
            # Get the model and iter
            model = self.tree_view.get_model()
            iter = model.get_iter(path[0])
            if iter:
                path = model.get_value(iter, 1)
                self.show_context_menu(gesture, path)
        return True
        
    def show_context_menu(self, gesture, path):
        menu = Gtk.PopoverMenu()
        menu.set_parent(self.tree_view)
        
        # Create menu model
        menu_model = Gio.Menu()
        
        # Add menu items
        menu_model.append("Delete", "file.delete")
        menu_model.append("Rename", "file.rename")
        
        # Create actions
        delete_action = Gio.SimpleAction.new("delete", None)
        delete_action.connect("activate", lambda action, param: self.delete_item(path))
        
        rename_action = Gio.SimpleAction.new("rename", None)
        rename_action.connect("activate", lambda action, param: self.rename_item(path))
        
        # Add actions to the window
        window = self.get_root()
        window.add_action(delete_action)
        window.add_action(rename_action)
        
        # Set the menu model
        menu.set_menu_model(menu_model)
        
        # Show the menu
        menu.popup()
        
    def delete_item(self, path):
        path = Path(path)
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
            self.refresh_tree()
        except Exception as e:
            print(f"Error deleting item: {e}")
            
    def rename_item(self, path):
        path = Path(path)
        dialog = Gtk.Dialog()
        dialog.set_title("Rename")
        dialog.set_transient_for(self.get_root())
        dialog.set_modal(True)
        
        # Add buttons
        dialog.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL,
            "Rename", Gtk.ResponseType.OK
        )
        
        content = dialog.get_content_area()
        content.set_margin_start(12)
        content.set_margin_end(12)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        
        # Create form
        form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Name entry
        name_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        name_label = Gtk.Label(label="New Name:", xalign=0)
        name_entry = Gtk.Entry()
        name_entry.set_text(path.name)
        name_entry.set_hexpand(True)
        name_box.append(name_label)
        name_box.append(name_entry)
        form.append(name_box)
        
        content.append(form)
        
        def on_response(dialog, response):
            if response == Gtk.ResponseType.OK:
                new_name = name_entry.get_text()
                if new_name:
                    try:
                        new_path = path.parent / new_name
                        path.rename(new_path)
                        self.refresh_tree()
                    except Exception as e:
                        print(f"Error renaming item: {e}")
            dialog.destroy()
            
        dialog.connect("response", on_response)
        dialog.present()
        
    def refresh_tree(self):
        # Clear the tree
        self.store.clear()
        # Repopulate
        self.populate_tree()
        
    def populate_tree(self):
        def add_to_tree(parent_iter, path):
            for item in path.iterdir():
                if item.name.startswith('.'):
                    continue
                    
                if item.is_file():
                    self.store.append(parent_iter, [item.name, str(item)])
                elif item.is_dir():
                    child_iter = self.store.append(parent_iter, [item.name, str(item)])
                    add_to_tree(child_iter, item)
                    
        add_to_tree(None, self.project_dir)
        
    def on_selection_changed(self, selection):
        model, iter = selection.get_selected()
        if iter:
            path = model.get_value(iter, 1)
            if os.path.isfile(path):
                self.emit("file-selected", path)

class Editor(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
        
        # Create the file tree view
        self.file_tree = None
        
        # Create the editor area
        editor_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        editor_box.set_hexpand(True)
        
        # Create the editor toolbar
        self.toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.toolbar.add_css_class("toolbar")
        self.toolbar.set_margin_start(12)
        self.toolbar.set_margin_end(12)
        self.toolbar.set_margin_top(12)
        self.toolbar.set_margin_bottom(12)
        
        # Add toolbar buttons
        self.save_btn = Gtk.Button(label="Save")
        self.save_btn.add_css_class("suggested-action")
        self.save_btn.connect("clicked", self.save_file)
        self.toolbar.append(self.save_btn)
        
        self.build_btn = Gtk.Button(label="Build")
        self.build_btn.connect("clicked", self.build_project)
        self.toolbar.append(self.build_btn)
        
        self.run_btn = Gtk.Button(label="Run")
        self.run_btn.connect("clicked", self.run_project)
        self.toolbar.append(self.run_btn)
        
        editor_box.append(self.toolbar)
        
        # Create the source view
        self.source_view = GtkSource.View()
        self.source_view.set_hexpand(True)
        self.source_view.set_vexpand(True)
        
        # Set up syntax highlighting
        self.language_manager = GtkSource.LanguageManager()
        self.buffer = GtkSource.Buffer()
        self.buffer.set_language(self.language_manager.get_language("kotlin"))
        self.source_view.set_buffer(self.buffer)
        
        # Add line numbers
        self.source_view.set_show_line_numbers(True)
        
        # Set cursor color to white and dark theme
        self.source_view.set_cursor_visible(True)
        
        # Create a CSS provider for styling
        css_provider = Gtk.CssProvider()
        css = """
        textview {
            background-color: #2d2d2d;
            color: #ffffff;
            padding: 12px;
        }
        textview text {
            caret-color: #ffffff;
        }
        .file-tree-header {
            background-color: #1e1e1e;
            border-bottom: 1px solid #3d3d3d;
        }
        .file-tree-title {
            font-weight: bold;
            color: #ffffff;
        }
        .file-tree-view {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        .toolbar {
            background-color: #1e1e1e;
            border-bottom: 1px solid #3d3d3d;
        }
        .toolbar button {
            margin-right: 6px;
        }
        .line-numbers {
            background-color: #2d2d2d;
            color: #666666;
            padding: 0 8px;
        }
        """
        css_provider.load_from_data(css.encode())
        
        # Apply the CSS
        style_context = self.source_view.get_style_context()
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
        # Add the source view to a scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self.source_view)
        scrolled.set_margin_start(12)
        scrolled.set_margin_end(12)
        scrolled.set_margin_bottom(12)
        scrolled.set_vexpand(True)
        editor_box.append(scrolled)
        
        self.append(editor_box)
        
        # Initialize LSP client
        self.lsp_client = None
        self.lsp_queue = queue.Queue()
        self.lsp_thread = None
        
        # Store current file path
        self.current_file_path = None
        
    def set_project_dir(self, project_dir):
        # Remove existing file tree if any
        if self.file_tree and self.file_tree.get_parent() == self:
            self.remove(self.file_tree)
            
        # Create new file tree
        self.file_tree = FileTreeView(project_dir)
        self.file_tree.set_size_request(250, -1)  # Set fixed width for file tree
        self.file_tree.set_vexpand(True)  # Make the file tree expand vertically
        self.file_tree.connect("file-selected", self.on_file_selected)
        self.prepend(self.file_tree)
        
    def on_file_selected(self, tree, file_path):
        self.open_file(file_path)
        
    def open_file(self, file_path):
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                self.buffer.set_text(content)
                
            # Store the current file path
            self.current_file_path = file_path
                
            # Start LSP server if it's a Kotlin file
            if file_path.endswith('.kt'):
                try:
                    self.start_lsp_server(file_path)
                except Exception as e:
                    print(f"LSP server not available: {e}")
                    print("Code completion and analysis features will be limited.")
                    print("To install the Kotlin language server:")
                    print("1. Using npm: npm install -g kotlin-language-server")
                    print("2. Build from source: https://github.com/fwcd/kotlin-language-server")
                    
        except Exception as e:
            print(f"Error opening file: {e}")
            
    def save_file(self, button):
        try:
            if not self.current_file_path:
                return
                
            start, end = self.buffer.get_bounds()
            content = self.buffer.get_text(start, end, False)
                
            with open(self.current_file_path, 'w') as f:
                f.write(content)
                
        except Exception as e:
            print(f"Error saving file: {e}")
            
    def build_project(self, button):
        if not self.current_file_path:
            return
            
        project_dir = Path(self.current_file_path).parent
        while project_dir.name != "app" and project_dir != project_dir.parent:
            project_dir = project_dir.parent
            
        if project_dir.name != "app":
            print("Not in an Android project")
            return
            
        # Show build progress dialog
        dialog = Gtk.Dialog(title="Building Project", transient_for=self.get_root(), modal=True)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        
        content = dialog.get_content_area()
        content.set_margin_start(12)
        content.set_margin_end(12)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        
        # Add progress bar
        progress = Gtk.ProgressBar()
        progress.set_hexpand(True)
        content.append(progress)
        
        # Add status label
        status = Gtk.Label(label="Building project...")
        content.append(status)
        
        dialog.show()
        
        def build_thread():
            try:
                # Run Gradle build
                process = subprocess.Popen(
                    ["./gradlew", "assembleDebug"],
                    cwd=str(project_dir.parent),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Read output
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    if line:
                        GLib.idle_add(update_status, line.strip())
                        
                # Check result
                if process.returncode == 0:
                    GLib.idle_add(build_success)
                else:
                    error = process.stderr.read()
                    GLib.idle_add(build_failed, error)
                    
            except Exception as e:
                GLib.idle_add(build_failed, str(e))
                
        def update_status(text):
            status.set_text(text)
            return False
            
        def build_success():
            dialog.response(Gtk.ResponseType.OK)
            dialog.destroy()
            
            # Show success message
            message = Gtk.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Build successful!"
            )
            message.run()
            message.destroy()
            
        def build_failed(error):
            dialog.response(Gtk.ResponseType.CANCEL)
            dialog.destroy()
            
            # Show error message
            message = Gtk.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=f"Build failed:\n{error}"
            )
            message.run()
            message.destroy()
            
        # Start build thread
        threading.Thread(target=build_thread, daemon=True).start()
        
    def run_project(self, button):
        if not self.current_file_path:
            return
            
        project_dir = Path(self.current_file_path).parent
        while project_dir.name != "app" and project_dir != project_dir.parent:
            project_dir = project_dir.parent
            
        if project_dir.name != "app":
            print("Not in an Android project")
            return
            
        # Show device selection dialog
        dialog = Gtk.Dialog(title="Select Device", transient_for=self.get_root(), modal=True)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Run", Gtk.ResponseType.OK)
        
        content = dialog.get_content_area()
        content.set_margin_start(12)
        content.set_margin_end(12)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        
        # Get list of devices
        try:
            devices = subprocess.check_output(
                ["adb", "devices", "-l"],
                text=True
            ).strip().split("\n")[1:]
            
            # Create device list
            device_list = Gtk.ListBox()
            device_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
            
            for device in devices:
                if device.strip():
                    parts = device.split()
                    device_id = parts[0]
                    device_info = " ".join(parts[1:])
                    row = Gtk.ListBoxRow()
                    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                    id_label = Gtk.Label(label=device_id, xalign=0)
                    info_label = Gtk.Label(label=device_info, xalign=0)
                    box.append(id_label)
                    box.append(info_label)
                    row.set_child(box)
                    device_list.append(row)
                    
            content.append(device_list)
            
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                # Get selected device
                selected = device_list.get_selected_row()
                if selected:
                    device_id = selected.get_child().get_first_child().get_text()
                    
                    # Show run progress dialog
                    run_dialog = Gtk.Dialog(title="Running App", transient_for=self.get_root(), modal=True)
                    run_dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
                    
                    run_content = run_dialog.get_content_area()
                    run_content.set_margin_start(12)
                    run_content.set_margin_end(12)
                    run_content.set_margin_top(12)
                    run_content.set_margin_bottom(12)
                    
                    # Add progress bar
                    progress = Gtk.ProgressBar()
                    progress.set_hexpand(True)
                    run_content.append(progress)
                    
                    # Add status label
                    status = Gtk.Label(label="Installing and running app...")
                    run_content.append(status)
                    
                    run_dialog.show()
                    
                    def run_thread():
                        try:
                            # Install and run the app
                            package_name = self.get_package_name(project_dir)
                            if not package_name:
                                GLib.idle_add(run_failed, "Could not determine package name")
                                return
                                
                            # Install the app
                            process = subprocess.Popen(
                                ["adb", "-s", device_id, "install", "-r", str(project_dir.parent / "app/build/outputs/apk/debug/app-debug.apk")],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True
                            )
                            
                            # Read output
                            while True:
                                line = process.stdout.readline()
                                if not line and process.poll() is not None:
                                    break
                                if line:
                                    GLib.idle_add(update_status, line.strip())
                                    
                            if process.returncode != 0:
                                error = process.stderr.read()
                                GLib.idle_add(run_failed, error)
                                return
                                
                            # Start the app
                            process = subprocess.Popen(
                                ["adb", "-s", device_id, "shell", "monkey", "-p", package_name, "1"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True
                            )
                            
                            if process.returncode == 0:
                                GLib.idle_add(run_success)
                            else:
                                error = process.stderr.read()
                                GLib.idle_add(run_failed, error)
                                
                        except Exception as e:
                            GLib.idle_add(run_failed, str(e))
                            
                    def update_status(text):
                        status.set_text(text)
                        return False
                        
                    def run_success():
                        run_dialog.response(Gtk.ResponseType.OK)
                        run_dialog.destroy()
                        
                        # Show success message
                        message = Gtk.MessageDialog(
                            transient_for=self.get_root(),
                            modal=True,
                            message_type=Gtk.MessageType.INFO,
                            buttons=Gtk.ButtonsType.OK,
                            text="App started successfully!"
                        )
                        message.run()
                        message.destroy()
                        
                    def run_failed(error):
                        run_dialog.response(Gtk.ResponseType.CANCEL)
                        run_dialog.destroy()
                        
                        # Show error message
                        message = Gtk.MessageDialog(
                            transient_for=self.get_root(),
                            modal=True,
                            message_type=Gtk.MessageType.ERROR,
                            buttons=Gtk.ButtonsType.OK,
                            text=f"Failed to run app:\n{error}"
                        )
                        message.run()
                        message.destroy()
                        
                    # Start run thread
                    threading.Thread(target=run_thread, daemon=True).start()
                    
            dialog.destroy()
            
        except Exception as e:
            print(f"Error getting devices: {e}")
            dialog.destroy()
            
    def get_package_name(self, app_dir):
        try:
            # Read AndroidManifest.xml
            manifest_path = app_dir / "src/main/AndroidManifest.xml"
            if not manifest_path.exists():
                return None
                
            with open(manifest_path, 'r') as f:
                content = f.read()
                
            # Extract package name
            import re
            match = re.search(r'package="([^"]+)"', content)
            if match:
                return match.group(1)
                
            return None
            
        except Exception as e:
            print(f"Error reading manifest: {e}")
            return None
        
    def start_lsp_server(self, file_path):
        if self.lsp_client:
            self.stop_lsp_server()
            
        # Start the Kotlin LSP server
        try:
            # Try to find kotlin-language-server in common locations
            lsp_paths = [
                'kotlin-language-server',  # System PATH
                os.path.expanduser('~/.local/bin/kotlin-language-server'),  # Local bin
                '/usr/local/bin/kotlin-language-server',  # System local bin
                '/usr/bin/kotlin-language-server'  # System bin
            ]
            
            lsp_found = False
            for path in lsp_paths:
                try:
                    self.lsp_client = subprocess.Popen(
                        [path],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    lsp_found = True
                    break
                except FileNotFoundError:
                    continue
                    
            if not lsp_found:
                print("Kotlin language server not found. Please install it using one of these methods:")
                print("1. Using npm: npm install -g kotlin-language-server")
                print("2. Build from source: https://github.com/fwcd/kotlin-language-server")
                return
                
            # Start the LSP communication thread
            self.lsp_thread = threading.Thread(target=self.lsp_communication_loop)
            self.lsp_thread.daemon = True
            self.lsp_thread.start()
            
            # Initialize the LSP connection
            self.initialize_lsp(file_path)
            
        except Exception as e:
            print(f"Error starting LSP server: {e}")
            print("Please install the Kotlin language server for better code completion and analysis.")
            
    def stop_lsp_server(self):
        if self.lsp_client:
            self.lsp_client.terminate()
            self.lsp_client = None
            
        if self.lsp_thread:
            self.lsp_thread.join()
            self.lsp_thread = None
            
    def initialize_lsp(self, file_path):
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "processId": os.getpid(),
                "rootUri": f"file://{os.path.dirname(file_path)}",
                "capabilities": {
                    "textDocument": {
                        "completion": {
                            "completionItem": {
                                "snippetSupport": True
                            }
                        },
                        "synchronization": {
                            "didSave": True
                        }
                    }
                }
            }
        }
        
        self.lsp_queue.put(json.dumps(init_request) + "\r\n")
        
    def lsp_communication_loop(self):
        while self.lsp_client:
            try:
                # Read from LSP server
                line = self.lsp_client.stdout.readline()
                if line:
                    response = json.loads(line)
                    self.handle_lsp_response(response)
                    
                # Write to LSP server
                try:
                    message = self.lsp_queue.get_nowait()
                    self.lsp_client.stdin.write(message)
                    self.lsp_client.stdin.flush()
                except queue.Empty:
                    pass
                    
            except Exception as e:
                print(f"Error in LSP communication: {e}")
                break
                
    def handle_lsp_response(self, response):
        # Handle LSP server responses
        if "method" in response:
            if response["method"] == "textDocument/publishDiagnostics":
                # Handle diagnostics
                pass
            elif response["method"] == "textDocument/completion":
                # Handle completions
                pass 
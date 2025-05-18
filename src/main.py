#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio, Gdk
import os
import subprocess
import json
from pathlib import Path
from project_manager import ProjectManager
from device_manager import DeviceManager
from editor import Editor
import sys

# Set Wayland as the default platform
os.environ['GDK_BACKEND'] = 'wayland'
os.environ['GTK_USE_PORTAL'] = '1'

class NewProjectDialog(Adw.Window):
    def __init__(self, parent):
        super().__init__(title="New Project", transient_for=parent, modal=True)
        self.set_default_size(400, -1)
        
        # Create the main box
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(box)
        
        # Create header bar
        header = Adw.HeaderBar()
        box.append(header)
        
        # Add buttons to header bar
        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda x: self.close())
        header.pack_start(cancel_btn)
        
        create_btn = Gtk.Button(label="Create")
        create_btn.add_css_class("suggested-action")
        create_btn.connect("clicked", self.on_create_clicked)
        header.pack_end(create_btn)
        
        # Create content area
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content.set_margin_start(12)
        content.set_margin_end(12)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        content.set_spacing(12)
        box.append(content)
        
        # Create form
        form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Project name
        name_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        name_label = Gtk.Label(label="Project Name:", xalign=0)
        self.name_entry = Gtk.Entry()
        self.name_entry.set_hexpand(True)
        name_box.append(name_label)
        name_box.append(self.name_entry)
        form.append(name_box)
        
        # Package name
        package_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        package_label = Gtk.Label(label="Package Name:", xalign=0)
        self.package_entry = Gtk.Entry()
        self.package_entry.set_hexpand(True)
        package_box.append(package_label)
        package_box.append(self.package_entry)
        form.append(package_box)
        
        # Minimum SDK
        sdk_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        sdk_label = Gtk.Label(label="Minimum SDK:", xalign=0)
        self.sdk_entry = Gtk.Entry()
        self.sdk_entry.set_text("21")
        self.sdk_entry.set_hexpand(True)
        sdk_box.append(sdk_label)
        sdk_box.append(self.sdk_entry)
        form.append(sdk_box)
        
        content.append(form)
        
        # Store parent window reference
        self.parent = parent
        
    def on_create_clicked(self, button):
        values = self.get_values()
        try:
            project_dir = self.parent.project_manager.create_project(
                values['name'],
                values['package'],
                values['min_sdk']
            )
            self.parent.open_project(project_dir)
            self.close()
        except Exception as e:
            print(f"Error creating project: {e}")
        
    def get_values(self):
        return {
            'name': self.name_entry.get_text(),
            'package': self.package_entry.get_text(),
            'min_sdk': self.sdk_entry.get_text()
        }

class DockApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id='com.github.mobotronst.dockapp')
        self.connect('activate', self.on_activate)
        
        # Initialize managers
        self.project_manager = ProjectManager()
        self.device_manager = DeviceManager()
        
    def on_activate(self, app):
        # Create the main window
        self.window = Adw.ApplicationWindow(application=app)
        self.window.set_title("DockApp")
        self.window.set_default_size(1200, 800)
        
        # Create the main layout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.window.set_content(self.main_box)
        
        # Create the header bar
        header = Adw.HeaderBar()
        self.main_box.append(header)
        
        # Add new project button
        new_project_btn = Gtk.Button()
        new_project_btn.set_icon_name("document-new-symbolic")
        new_project_btn.set_tooltip_text("New Project")
        new_project_btn.connect("clicked", self.show_new_project_dialog)
        header.pack_start(new_project_btn)
        
        # Add open project button
        open_project_btn = Gtk.Button()
        open_project_btn.set_icon_name("document-open-symbolic")
        open_project_btn.set_tooltip_text("Open Project")
        open_project_btn.connect("clicked", self.show_open_project_dialog)
        header.pack_start(open_project_btn)
        
        # Create the main stack for different views
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.main_box.append(self.stack)
        
        # Create welcome view
        welcome_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        welcome_box.set_halign(Gtk.Align.CENTER)
        welcome_box.set_valign(Gtk.Align.CENTER)
        welcome_box.set_spacing(24)
        
        welcome_title = Gtk.Label(label="Welcome to DockApp")
        welcome_title.add_css_class("title-1")
        welcome_box.append(welcome_title)
        
        welcome_text = Gtk.Label(label="Create a new project or open an existing one to get started")
        welcome_text.add_css_class("body")
        welcome_box.append(welcome_text)
        
        welcome_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        welcome_buttons.set_halign(Gtk.Align.CENTER)
        
        welcome_new_btn = Gtk.Button()
        welcome_new_btn.set_icon_name("document-new-symbolic")
        welcome_new_btn.set_label("New Project")
        welcome_new_btn.add_css_class("suggested-action")
        welcome_new_btn.connect("clicked", self.show_new_project_dialog)
        welcome_buttons.append(welcome_new_btn)
        
        welcome_open_btn = Gtk.Button()
        welcome_open_btn.set_icon_name("document-open-symbolic")
        welcome_open_btn.set_label("Open Project")
        welcome_open_btn.connect("clicked", self.show_open_project_dialog)
        welcome_buttons.append(welcome_open_btn)
        
        welcome_box.append(welcome_buttons)
        
        self.stack.add_named(welcome_box, "welcome")
        
        # Create editor view
        editor_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.editor = Editor()
        editor_box.append(self.editor)
        self.stack.add_named(editor_box, "editor")
        
        # Load projects
        self.load_projects()
        
        # Show welcome screen by default
        self.stack.set_visible_child_name("welcome")
        
        # Show the window
        self.window.present()
        
    def show_new_project_dialog(self, button):
        dialog = Gtk.Dialog()
        dialog.set_title("New Project")
        dialog.set_transient_for(self.window)
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
        
        # Create form
        form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Project name entry
        name_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        name_label = Gtk.Label(label="Project Name:", xalign=0)
        name_entry = Gtk.Entry()
        name_entry.set_hexpand(True)
        name_box.append(name_label)
        name_box.append(name_entry)
        form.append(name_box)
        
        # Package name entry
        package_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        package_label = Gtk.Label(label="Package Name:", xalign=0)
        package_entry = Gtk.Entry()
        package_entry.set_hexpand(True)
        package_box.append(package_label)
        package_box.append(package_entry)
        form.append(package_box)
        
        content.append(form)
        
        def on_response(dialog, response):
            if response == Gtk.ResponseType.OK:
                project_name = name_entry.get_text()
                package_name = package_entry.get_text()
                
                if project_name and package_name:
                    try:
                        project_dir = self.project_manager.create_project(project_name, package_name)
                        self.editor.set_project_dir(str(project_dir))
                        self.stack.set_visible_child_name("editor")
                    except Exception as e:
                        print(f"Error creating project: {e}")
            dialog.destroy()
            
        dialog.connect("response", on_response)
        dialog.present()
        
    def show_open_project_dialog(self, button):
        dialog = Gtk.FileChooserDialog()
        dialog.set_title("Open Project")
        dialog.set_transient_for(self.window)
        dialog.set_modal(True)
        dialog.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
        
        # Add buttons
        dialog.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL,
            "Open", Gtk.ResponseType.OK
        )
        
        def on_response(dialog, response):
            if response == Gtk.ResponseType.OK:
                file = dialog.get_file()
                if file:
                    project_dir = Path(file.get_path())
                    self.editor.set_project_dir(str(project_dir))
                    self.stack.set_visible_child_name("editor")
            dialog.destroy()
            
        dialog.connect("response", on_response)
        dialog.present()
        
    def load_projects(self):
        projects = self.project_manager.list_projects()
        # TODO: Show projects in a list or grid
        
def main():
    app = DockApp()
    return app.run(sys.argv)

if __name__ == '__main__':
    main() 
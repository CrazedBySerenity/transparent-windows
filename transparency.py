import threading
import sys
import os
import time
import json
from win32 import win32gui, winxpgui, win32api
import win32.lib.win32con as win32con
import keyboard
import tkinter as tk
from tkinter import messagebox, ttk

try:
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

class TransparentWindowsApp:
    def __init__(self):
        self.running = True
        self.opacity_step_1 = 10
        self.opacity_step_10 = 255
        self.opacity = 30
        self.icon = None
        
        # Default keyboard shortcuts
        self.default_shortcuts = {
            'modifier_keys': ['ctrl', 'shift', 'alt'],
            'number_keys': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        }
        
        # Load or create settings
        self.settings_file = "transparent_windows_settings.json"
        self.shortcuts = self.load_settings()
        
    def load_settings(self):
        """Load keyboard shortcuts from settings file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Validate settings
                    if 'modifier_keys' in settings and 'number_keys' in settings:
                        return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        # Return default settings if loading fails
        return self.default_shortcuts.copy()
    
    def save_settings(self):
        """Save keyboard shortcuts to settings file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.shortcuts, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_shortcut_string(self):
        """Get a readable string of current shortcuts"""
        modifiers = '+'.join([key.title() for key in self.shortcuts['modifier_keys']])
        return f"{modifiers}+0-9"
        
    def change_window_opacity(self):
        """Apply transparency to the currently active window"""
        try:
            # time.sleep(0.1)  # Small delay to ensure we get the right window
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                window_title = win32gui.GetWindowText(hwnd)
                
                # Skip our own windows to prevent crashes
                # if any(skip_word in window_title.lower() for skip_word in 
                #       ['transparent windows', 'about', 'error', 'message', 'settings']):
                #     print(f"Skipping window: {window_title}")
                #     return
                
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                                     win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
                winxpgui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0,0,0), self.opacity, win32con.LWA_ALPHA)
                
                transparency_percent = round((self.opacity / 255) * 100)
                print(f"Applied {transparency_percent}% opacity to: {window_title}")
                
        except Exception as e:
            print(f"Error changing opacity: {e}")
    
    def are_modifiers_pressed(self):
        """Check if all modifier keys are currently pressed"""
        try:
            for key in self.shortcuts['modifier_keys']:
                if not keyboard.is_pressed(key):
                    return False
            return True
        except:
            return False
    
    def keyboard_listener(self):
        """Listen for keyboard shortcuts"""
        shortcut_str = self.get_shortcut_string()
        print(f"Keyboard listener started. Use {shortcut_str} to change transparency.")
        
        while self.running:
            try:
                if self.are_modifiers_pressed():
                    for key in self.shortcuts['number_keys']:
                        if keyboard.is_pressed(key):
                            num = int(key)
                            
                            if num == 0:
                                self.opacity = 1  # Nearly invisible
                            elif num == 1:
                                self.opacity = self.opacity_step_1
                            elif num == 9:
                                self.opacity = self.opacity_step_10
                            else:
                                # Calculate opacity for levels 2-8
                                self.opacity = round(self.opacity_step_1 + ((self.opacity_step_10 - self.opacity_step_1) / 8) * (num - 1))
                            
                            self.change_window_opacity()
                            # time.sleep(0.4)  # Prevent multiple triggers
                            break
                
                time.sleep(0.05)  # Prevent excessive CPU usage
                        
            except Exception as e:
                if self.running:
                    print(f"Keyboard listener error: {e}")
                    time.sleep(1)
    
    def create_tray_icon(self):
        """Create a simple icon for the system tray"""
        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw a window icon with transparency effect
        draw.rectangle([8, 8, 56, 48], fill=(100, 100, 100, 255), outline=(50, 50, 50, 255), width=2)
        draw.rectangle([8, 8, 56, 20], fill=(50, 100, 200, 255))
        draw.rectangle([16, 28, 48, 40], fill=(150, 150, 150, 128))
        draw.rectangle([20, 32, 44, 36], fill=(200, 200, 200, 64))
        draw.text((26, 50), "T", fill=(0, 0, 0, 255))
        
        return image
    
    def show_about(self):
        """Show information about the application"""
        def show_dialog():
            root = tk.Tk()
            root.withdraw()
            
            shortcut_str = self.get_shortcut_string()
            about_text = f"""Transparent Windows by Sophia

Current Keyboard Shortcuts:
• {shortcut_str.replace('0-9', '0')}: Nearly invisible (1%)
• {shortcut_str.replace('0-9', '1')}: Most transparent (10%)
• {shortcut_str.replace('0-9', '2-8')}: Gradual transparency levels
• {shortcut_str.replace('0-9', '9')}: Fully opaque (100%)

Usage:
1. Focus on any window
2. Press {shortcut_str.replace('0-9', 'number key (0-9)')}
3. Window becomes transparent

Right-click the tray icon for options.
Use Settings to customize keyboard shortcuts."""
            
            messagebox.showinfo("About Transparent Windows", about_text)
            root.destroy()
        
        threading.Thread(target=show_dialog, daemon=True).start()
    
    def show_settings(self):
        """Show settings dialog for customizing keyboard shortcuts"""
        def show_settings_dialog():
            settings_window = tk.Tk()
            settings_window.title("Transparent Windows - Settings")
            settings_window.geometry("500x500")
            settings_window.resizable(False, False)
            
            # Center the window
            settings_window.update_idletasks()
            x = (settings_window.winfo_screenwidth() // 2) - (500 // 2)
            y = (settings_window.winfo_screenheight() // 2) - (400 // 2)
            settings_window.geometry(f"+{x}+{y}")
            
            main_frame = tk.Frame(settings_window, padx=20, pady=20)
            main_frame.pack(fill='both', expand=True)
            
            # Title
            title_label = tk.Label(main_frame, text="Keyboard Shortcut Settings", 
                                  font=('Arial', 14, 'bold'))
            title_label.pack(pady=(0, 20))
            
            # Current shortcuts display
            current_frame = tk.LabelFrame(main_frame, text="Current Shortcuts", padx=10, pady=10)
            current_frame.pack(fill='x', pady=(0, 20))
            
            current_shortcut = self.get_shortcut_string()
            current_label = tk.Label(current_frame, text=f"Active: {current_shortcut}", 
                                   font=('Arial', 12, 'bold'), fg='green')
            current_label.pack()
            
            # Modifier keys selection
            modifier_frame = tk.LabelFrame(main_frame, text="Modifier Keys (Select multiple)", padx=10, pady=10)
            modifier_frame.pack(fill='x', pady=(0, 10))
            
            # Modifier key checkboxes
            modifier_vars = {}
            available_modifiers = ['ctrl', 'shift', 'alt', 'win']
            
            for i, mod in enumerate(available_modifiers):
                var = tk.BooleanVar()
                var.set(mod in self.shortcuts['modifier_keys'])
                modifier_vars[mod] = var
                
                cb = tk.Checkbutton(modifier_frame, text=mod.title(), variable=var)
                cb.grid(row=i//2, column=i%2, sticky='w', padx=10, pady=2)
            
            # Instructions
            instruction_frame = tk.Frame(main_frame)
            instruction_frame.pack(fill='x', pady=(0, 20))
            
            instruction_text = """Instructions:
• Select at least one modifier key (Ctrl, Shift, Alt, Win)
• The number keys 0-9 will be used automatically
• Avoid common combinations like Ctrl+C, Ctrl+V, etc.
• Recommended: Ctrl+Shift+Alt for maximum compatibility"""
            
            instruction_label = tk.Label(instruction_frame, text=instruction_text, 
                                       justify='left', wraplength=450)
            instruction_label.pack()
            
            # Buttons
            button_frame = tk.Frame(main_frame)
            button_frame.pack(fill='x', pady=(10, 0))
            
            def apply_settings():
                # Get selected modifiers
                selected_modifiers = [mod for mod, var in modifier_vars.items() if var.get()]
                
                if not selected_modifiers:
                    messagebox.showerror("Error", "Please select at least one modifier key.")
                    return
                
                # Update shortcuts
                old_shortcut = self.get_shortcut_string()
                self.shortcuts['modifier_keys'] = selected_modifiers
                new_shortcut = self.get_shortcut_string()
                
                # Save settings
                if self.save_settings():
                    messagebox.showinfo("Settings Saved", 
                                      f"Shortcuts updated!\n\nOld: {old_shortcut}\nNew: {new_shortcut}\n\nRestart may be required for changes to take full effect.")
                    settings_window.destroy()
                else:
                    messagebox.showerror("Error", "Failed to save settings.")
            
            def reset_defaults():
                if messagebox.askyesno("Reset to Defaults", "Reset to default shortcuts (Ctrl+Shift+Alt+0-9)?"):
                    self.shortcuts = self.default_shortcuts.copy()
                    if self.save_settings():
                        messagebox.showinfo("Reset Complete", "Settings reset to defaults.\nRestart may be required.")
                        settings_window.destroy()
                    else:
                        messagebox.showerror("Error", "Failed to reset settings.")
            
            tk.Button(button_frame, text="Apply", command=apply_settings, width=12).pack(side='left', padx=(0, 10))
            tk.Button(button_frame, text="Reset to Defaults", command=reset_defaults, width=15).pack(side='left', padx=(0, 10))
            tk.Button(button_frame, text="Cancel", command=settings_window.destroy, width=12).pack(side='right')
            
            settings_window.mainloop()
        
        threading.Thread(target=show_settings_dialog, daemon=True).start()
    
    def reset_all_windows(self):
        """Reset all windows to full opacity"""
        def reset_windows():
            try:
                def enum_window_callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                        windows.append(hwnd)
                    return True
                
                windows = []
                win32gui.EnumWindows(enum_window_callback, windows)
                
                reset_count = 0
                for hwnd in windows:
                    try:
                        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                                             win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
                        winxpgui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0,0,0), 255, win32con.LWA_ALPHA)
                        reset_count += 1
                    except:
                        continue
                
                print(f"Reset {reset_count} windows to full opacity")
                
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo("Reset Complete", f"Reset {reset_count} windows to full opacity")
                root.destroy()
                
            except Exception as e:
                print(f"Reset failed: {e}")
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("Reset Failed", f"Error: {e}")
                root.destroy()
        
        threading.Thread(target=reset_windows, daemon=True).start()
    
    def quit_app(self):
        """Quit the application"""
        self.running = False
        if self.icon:
            self.icon.stop()
        print("Transparent Windows shutting down...")
        os._exit(0)
    
    def run_system_tray(self):
        """Run the system tray application"""
        if not TRAY_AVAILABLE:
            print("System tray not available. Please install: pip install pillow pystray")
            self.run_console_mode()
            return
        
        try:
            image = self.create_tray_icon()
            
            shortcut_str = self.get_shortcut_string()
            menu = pystray.Menu(
                item('About', self.show_about),
                item('Settings', self.show_settings),
                item('Reset All Windows', self.reset_all_windows),
                pystray.Menu.SEPARATOR,
                item('Quit', self.quit_app)
            )
            
            self.icon = pystray.Icon("TransparentWindows", image, f"Transparent Windows - {shortcut_str}", menu)
            
            keyboard_thread = threading.Thread(target=self.keyboard_listener, daemon=True)
            keyboard_thread.start()
            
            print("Transparent Windows is running in the system tray.")
            print("Look for the icon in the bottom-right corner of your screen.")
            print(f"Use {shortcut_str} to change window transparency.")
            
            self.icon.run()
            
        except Exception as e:
            print(f"System tray error: {e}")
            print("Falling back to console mode...")
            self.run_console_mode()
    
    def run_console_mode(self):
        """Fallback console mode if system tray fails"""
        shortcut_str = self.get_shortcut_string()
        
        print("\n" + "="*50)
        print("TRANSPARENT WINDOWS - CONSOLE MODE")
        print("="*50)
        print(f"Use {shortcut_str} to change window transparency:")
        print("• 0 = Nearly invisible (1%)")
        print("• 1 = Most transparent (10%)")
        print("• 9 = Fully opaque (100%)")
        print("• 2-8 = Gradual transparency levels")
        print("\nPress Ctrl+C to quit")
        print("="*50)
        
        keyboard_thread = threading.Thread(target=self.keyboard_listener, daemon=True)
        keyboard_thread.start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.running = False

def main():
    """Main function to run the application"""
    if os.name != 'nt':
        print("Error: This application only works on Windows.")
        input("Press Enter to exit...")
        return
    
    print("Starting Transparent Windows...")
    
    try:
        app = TransparentWindowsApp()
        app.run_system_tray()
        
    except ImportError as e:
        error_msg = f"Missing required library: {e}\n\nRequired packages:\npip install pywin32 keyboard pillow pystray"
        print(error_msg)
        input("Press Enter to exit...")
        
    except Exception as e:
        error_msg = f"An error occurred: {e}"
        print(error_msg)
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
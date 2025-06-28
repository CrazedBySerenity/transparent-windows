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
        self.settings_file = "transparent_windows_settings.json"
        
        # Default shortcuts
        self.default_shortcuts = {
            'modifier1': 'ctrl',
            'modifier2': 'shift', 
            'modifier3': 'alt',
            'block_input': True
        }
        
        # Load settings
        self.shortcuts = self.load_settings()
        
    def load_settings(self):
        """Load shortcuts from settings file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Validate settings
                    if all(key in settings for key in self.default_shortcuts.keys()):
                        return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        # Return defaults if loading fails
        return self.default_shortcuts.copy()
    
    def save_settings(self):
        """Save shortcuts to settings file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.shortcuts, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_shortcut_display(self):
        """Get human-readable shortcut combination"""
        modifiers = []
        for mod_key in ['modifier1', 'modifier2', 'modifier3']:
            if self.shortcuts.get(mod_key):
                modifiers.append(self.shortcuts[mod_key].title())
        
        if modifiers:
            return " + ".join(modifiers) + " + 0-9"
        return "0-9"
    
    def change_window_opacity(self):
        """Apply transparency to the currently active window"""
        try:
            # time.sleep(0.1)  # Small delay to ensure we get the right window
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                window_title = win32gui.GetWindowText(hwnd)
                
                # # Skip our own windows to prevent crashes
                # if any(skip_word in window_title.lower() for skip_word in 
                #       ['transparent windows', 'about', 'error', 'message', 'options', 'settings']):
                #     print(f"Skipping window: {window_title}")
                #     return
                
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                                     win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
                winxpgui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0,0,0), self.opacity, win32con.LWA_ALPHA)
                
                transparency_percent = round((self.opacity / 255) * 100)
                print(f"Applied {transparency_percent}% opacity to: {window_title}")
                
        except Exception as e:
            print(f"Error changing opacity: {e}")
    
    def is_shortcut_active(self):
        """Check if the current shortcut combination is pressed"""
        try:
            modifiers_pressed = True
            
            # Check each modifier
            for mod_key in ['modifier1', 'modifier2', 'modifier3']:
                modifier = self.shortcuts.get(mod_key)
                if modifier and modifier.strip():
                    if not keyboard.is_pressed(modifier):
                        modifiers_pressed = False
                        break
            
            return modifiers_pressed
        except:
            return False
    
    def keyboard_listener(self):
        """Listen for keyboard shortcuts"""
        shortcut_display = self.get_shortcut_display()
        print(f"Keyboard listener started. Use {shortcut_display} to change transparency.")
        
        # Valid number keys
        valid_keys = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        last_trigger_time = 0
        
        while self.running:
            try:
                if self.is_shortcut_active():
                    current_time = time.time()
                    
                    for key in valid_keys:
                        if keyboard.is_pressed(key):
                            # Prevent rapid triggering
                            if current_time - last_trigger_time < 0.3:
                                continue
                            
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
                            last_trigger_time = current_time
                            
                            # Block the input if enabled
                            if self.shortcuts.get('block_input', True):
                                try:
                                    # Suppress the key event
                                    keyboard.block_key(key)
                                    time.sleep(0.1)
                                    keyboard.unblock_key(key)()
                                    print("Succesfully blocked input")
                                except:
                                    print("Failed to blocked input")
                                    pass  # If blocking fails, continue anyway
                            
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
            
            shortcut_display = self.get_shortcut_display()
            about_text = f"""Transparent Windows by Sophia

Current Shortcuts: {shortcut_display}
• 0: Nearly invisible (1%)
• 1: Most transparent (10%)
• 2-8: Gradual transparency levels
• 9: Fully opaque (100%)

Usage:
1. Focus on any window
2. Press your shortcut combination + number key
3. Window becomes transparent

Right-click the tray icon for options.
You can customize shortcuts in Options."""
            
            messagebox.showinfo("About Transparent Windows", about_text)
            root.destroy()
        
        threading.Thread(target=show_dialog, daemon=True).start()
    
    def show_options(self):
        """Show options dialog for customizing shortcuts"""
        def show_options_dialog():
            root = tk.Tk()
            root.title("Transparent Windows - Options")
            # root.geometry("450x350")
            root.resizable(True, True)
            
            # Center the window
            root.update_idletasks()
            x = (root.winfo_screenwidth() // 2) - (450 // 2)
            y = (root.winfo_screenheight() // 2) - (600 // 2)
            root.geometry(f"450x600+{x}+{y}")
            
            main_frame = tk.Frame(root, padx=20, pady=20)
            main_frame.pack(fill='both', expand=True)
            
            # Title
            title_label = tk.Label(main_frame, text="Shortcut Options", 
                                  font=('Arial', 14, 'bold'))
            title_label.pack(pady=(0, 20))
            
            # Current shortcuts display
            current_frame = tk.LabelFrame(main_frame, text="Current Shortcuts", padx=10, pady=10)
            current_frame.pack(fill='x', pady=(0, 20))
            
            current_label = tk.Label(current_frame, text=f"Current: {self.get_shortcut_display()}", 
                                   font=('Arial', 10))
            current_label.pack()
            
            # Modifier selection
            modifier_frame = tk.LabelFrame(main_frame, text="Customize Modifiers", padx=10, pady=10)
            modifier_frame.pack(fill='x', pady=(0, 20))
            
            modifier_options = ['', 'ctrl', 'shift', 'alt', 'win']
            
            # Modifier 1
            tk.Label(modifier_frame, text="Modifier 1:").grid(row=0, column=0, sticky='w', pady=2)
            mod1_var = tk.StringVar(value=self.shortcuts.get('modifier1', ''))
            mod1_combo = ttk.Combobox(modifier_frame, textvariable=mod1_var, values=modifier_options, width=10)
            mod1_combo.grid(row=0, column=1, padx=(10, 0), pady=2)
            
            # Modifier 2
            tk.Label(modifier_frame, text="Modifier 2:").grid(row=1, column=0, sticky='w', pady=2)
            mod2_var = tk.StringVar(value=self.shortcuts.get('modifier2', ''))
            mod2_combo = ttk.Combobox(modifier_frame, textvariable=mod2_var, values=modifier_options, width=10)
            mod2_combo.grid(row=1, column=1, padx=(10, 0), pady=2)
            
            # Modifier 3
            tk.Label(modifier_frame, text="Modifier 3:").grid(row=2, column=0, sticky='w', pady=2)
            mod3_var = tk.StringVar(value=self.shortcuts.get('modifier3', ''))
            mod3_combo = ttk.Combobox(modifier_frame, textvariable=mod3_var, values=modifier_options, width=10)
            mod3_combo.grid(row=2, column=1, padx=(10, 0), pady=2)
            
            # Block input option
            block_frame = tk.LabelFrame(main_frame, text="Input Blocking", padx=10, pady=10)
            block_frame.pack(fill='x', pady=(0, 20))
            
            block_var = tk.BooleanVar(value=self.shortcuts.get('block_input', True))
            block_check = tk.Checkbutton(block_frame, 
                                       text="Block default key behavior when using shortcuts\n(Prevents typing numbers when shortcuts are pressed)",
                                       variable=block_var, wraplength=350)
            block_check.pack(anchor='w')
            
            # Preset buttons
            preset_frame = tk.LabelFrame(main_frame, text="Quick Presets", padx=10, pady=10)
            preset_frame.pack(fill='x', pady=(0, 20))
            
            def apply_preset(preset):
                if preset == "safe":
                    mod1_var.set('ctrl')
                    mod2_var.set('shift')
                    mod3_var.set('alt')
                elif preset == "simple":
                    mod1_var.set('ctrl')
                    mod2_var.set('alt')
                    mod3_var.set('')
                elif preset == "minimal":
                    mod1_var.set('shift')
                    mod2_var.set('')
                    mod3_var.set('')
            
            preset_btn_frame = tk.Frame(preset_frame)
            preset_btn_frame.pack()
            
            tk.Button(preset_btn_frame, text="Safe (Ctrl+Shift+Alt)", 
                     command=lambda: apply_preset("safe")).pack(side='left', padx=5)
            tk.Button(preset_btn_frame, text="Simple (Ctrl+Alt)", 
                     command=lambda: apply_preset("simple")).pack(side='left', padx=5)
            tk.Button(preset_btn_frame, text="Minimal (Shift)", 
                     command=lambda: apply_preset("minimal")).pack(side='left', padx=5)
            
            # Buttons
            button_frame = tk.Frame(main_frame)
            button_frame.pack(pady=10)
            
            def save_and_close():
                # Save new settings
                new_shortcuts = {
                    'modifier1': mod1_var.get(),
                    'modifier2': mod2_var.get(),
                    'modifier3': mod3_var.get(),
                    'block_input': block_var.get()
                }
                
                self.shortcuts = new_shortcuts
                if self.save_settings():
                    messagebox.showinfo("Settings Saved", 
                                      f"New shortcuts: {self.get_shortcut_display()}\n\nRestart may be required for full effect.")
                else:
                    messagebox.showerror("Error", "Failed to save settings.")
                
                root.destroy()
            
            def reset_defaults():
                result = messagebox.askyesno("Reset to Defaults", 
                                           "Reset to default shortcuts (Ctrl+Shift+Alt+0-9)?")
                if result:
                    self.shortcuts = self.default_shortcuts.copy()
                    if self.save_settings():
                        messagebox.showinfo("Reset Complete", "Settings reset to defaults.")
                        root.destroy()
            
            tk.Button(button_frame, text="Save", command=save_and_close, width=10).pack(side='left', padx=5)
            tk.Button(button_frame, text="Reset Defaults", command=reset_defaults, width=12).pack(side='left', padx=5)
            tk.Button(button_frame, text="Cancel", command=root.destroy, width=10).pack(side='left', padx=5)
            
            # Instructions
            instructions = tk.Label(main_frame, 
                                  text="Leave modifier fields empty to disable them.\nExample: Only 'Modifier 1' = Ctrl+0-9",
                                  font=('Arial', 8), fg='gray')
            instructions.pack(pady=(10, 0))
            
            root.mainloop()
        
        threading.Thread(target=show_options_dialog, daemon=True).start()
    
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
            
            menu = pystray.Menu(
                item('About', self.show_about),
                item('Options', self.show_options),
                item('Reset All Windows', self.reset_all_windows),
                pystray.Menu.SEPARATOR,
                item('Quit', self.quit_app)
            )
            
            shortcut_display = self.get_shortcut_display()
            self.icon = pystray.Icon("TransparentWindows", image, f"Transparent Windows - {shortcut_display}", menu)
            
            # Start keyboard listener in background
            keyboard_thread = threading.Thread(target=self.keyboard_listener, daemon=True)
            keyboard_thread.start()
            
            print("Transparent Windows is running in the system tray.")
            print("Look for the icon in the bottom-right corner of your screen.")
            print(f"Use {shortcut_display} to change window transparency.")
            
            self.icon.run()
            
        except Exception as e:
            print(f"System tray error: {e}")
            print("Falling back to console mode...")
            self.run_console_mode()
    
    def run_console_mode(self):
        """Fallback console mode if system tray fails"""
        print("\n" + "="*50)
        print("TRANSPARENT WINDOWS - CONSOLE MODE")
        print("="*50)
        shortcut_display = self.get_shortcut_display()
        print(f"Use {shortcut_display} to change window transparency:")
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